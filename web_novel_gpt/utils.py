import json
import re
from functools import wraps
from typing import Any, Awaitable, Callable, Dict, Optional, Tuple, TypeVar, Union, cast

from pydantic import BaseModel

from web_novel_gpt.logger import logger
from web_novel_gpt.schema import (
    Chapter,
    ChapterOutline,
    CheckpointType,
    DetailedOutline,
    Novel,
    NovelVolume,
    OutlineType,
    RoughOutline,
)


T = TypeVar("T", bound=BaseModel)


def save_output(content: str, file_path: str) -> None:
    """Save content to specified file path."""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def json_parse(response: str) -> str:
    """
    Extract JSON string from LLM response.

    Args:
        response (str): Raw response from LLM

    Returns:
        str: Cleaned JSON string
    """
    # Try to find JSON pattern in the response
    json_pattern = r"\{[\s\S]*\}"
    match = re.search(json_pattern, response)

    if match:
        return match.group()
    return response


def save_checkpoint(checkpoint_type: CheckpointType):
    """
    Decorator for saving complete novel state during generation.

    Args:
        checkpoint_type (CheckpointType): Type of checkpoint to save
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(self, *args, **kwargs) -> T:
            result = await func(self, *args, **kwargs)

            # Base checkpoint data with novel-level info
            checkpoint_data = {
                "intent": self.intent.model_dump() if self.intent else None,
                "rough_outline": self.rough_outline.model_dump()
                if self.rough_outline
                else None,
                "volumes": [v.model_dump() for v in self.volumes],
                "current_volume_num": self.current_volume_num,
                "current_chapter_num": self.current_chapter_num,
            }

            if checkpoint_type == CheckpointType.VOLUME:
                volume = cast(NovelVolume, result)
                checkpoint_data["current_volume"] = volume.model_dump()

            elif checkpoint_type == CheckpointType.CHAPTER:
                chapter = cast(Chapter, result)
                # Save chapter content separately
                if self.current_volume_num and self.current_chapter_num:
                    self.novel_saver.save_chapter(
                        self.novel_id,
                        self.current_volume_num,
                        self.current_chapter_num,
                        chapter,
                    )

                # Update checkpoint with current chapter data
                checkpoint_data.update(
                    {
                        "current_chapter": {
                            "title": chapter.title,
                            "content": chapter.content,
                        },
                        # "chapter_outline": self.chapter_outlines.model_dump()
                        "chapter_outlines": [
                            co.model_dump()
                            for co in self.volumes[
                                self.current_volume_num - 1
                            ].chapter_outlines
                        ]
                        if self.volumes
                        else None,
                        # "detailed_outline": self.detailed_outlines.model_dump()
                        "detailed_outlines": [
                            do.model_dump()
                            for do in self.volumes[
                                self.current_volume_num - 1
                            ].detailed_outlines
                        ]
                        if self.volumes
                        else None,
                    }
                )

            elif checkpoint_type == CheckpointType.NOVEL:
                novel = cast(Novel, result)
                checkpoint_data.update(
                    {
                        "intent": novel.intent.model_dump(),
                        "rough_outline": novel.rough_outline.model_dump(),
                        "volumes": [v.model_dump() for v in novel.volumes],
                        "cost_info": novel.cost_info,
                    }
                )

            self.novel_saver.save_checkpoint(self.novel_id, checkpoint_data)
            logger.info(
                f"Saved {checkpoint_type.value} checkpoint for novel {self.novel_id}"
            )
            return result

        return wrapper

    return decorator


def parse_intent(response: str) -> Tuple[str, str, str]:
    """
    Parse intent analysis response and extract components.

    Args:
        response (str): Response string from intent analysis

    Returns:
        Tuple[str, str, str]: (description, genre, word_count)
    """
    intent = json_parse(response)
    intent_json = json.loads(intent)
    return (
        intent_json.get("title"),
        intent_json.get("description"),
        intent_json.get("genre"),
    )


def serialize_outline(
    outline: Optional[Union[RoughOutline, ChapterOutline, DetailedOutline]]
) -> Optional[Dict[str, Any]]:
    """
    Serialize an outline object to dictionary format.

    Args:
        outline: The outline object to serialize. Can be RoughOutline,
                ChapterOutline or DetailedOutline.

    Returns:
        dict: The serialized outline data as a dictionary.
        None: If input outline is None.
    """
    if outline is None:
        return None
    return outline.model_dump()


def load_outline_from_dict(
    data: Optional[Dict[str, Any]], outline_type: OutlineType
) -> Optional[Union[RoughOutline, ChapterOutline, DetailedOutline]]:
    """
    Reconstruct an outline object from dictionary data.

    Args:
        data: Dictionary containing the outline data.
        outline_type: Type of outline to create (rough/chapter/detailed).

    Returns:
        An outline object of the specified type.
        None if input data is None/empty.

    Raises:
        ValueError: If outline_type is invalid.
        ValidationError: If data validation fails.
    """
    if not data:
        return None

    outline_classes = {
        OutlineType.ROUGH: RoughOutline,
        OutlineType.CHAPTER: ChapterOutline,
        OutlineType.DETAILED: DetailedOutline,
    }

    outline_class = outline_classes.get(outline_type)
    if outline_class is None:
        raise ValueError(f"Unknown outline type: {outline_type}")

    return outline_class.model_validate(data)


def extract_outline(
    document: str, outline_type: OutlineType
) -> Union[RoughOutline, ChapterOutline, DetailedOutline]:
    """
    Extracts content from LLM response based on outline type and returns appropriate outline object.

    Args:
        document (str): The input text document from LLM response.
        outline_type (OutlineType): The type of outline to extract.

    Returns:
        Union[RoughOutline, ChapterOutline, DetailedOutline]: An outline object containing the extracted content.

    Raises:
        ValueError: If required content is missing or outline_type is invalid.
    """

    def extract_tag_content(tag: str) -> Optional[str]:
        """Helper function to extract content between tags."""
        pattern = f"<{tag}>(.*?)</{tag}>"
        match = re.search(pattern, document, re.DOTALL)
        return match.group(1).strip() if match else None

    # Tag mappings for different outline types
    tag_mappings = {
        OutlineType.ROUGH: {
            "worldview_system": "worldview_system",
            "character_system": "character_system",
            "plot_design": "plot_design",
        },
        OutlineType.CHAPTER: {
            "chapter_overview": "chapter_overview",
            "characters_content": "characters_content",
        },
        OutlineType.DETAILED: {"storyline": "storyline"},
    }

    # Extract content based on outline type
    content = {}
    for key, t in tag_mappings[outline_type].items():
        extracted_content = extract_tag_content(t)
        if extracted_content is None:
            raise ValueError(f"Required content '{t}' not found in document")
        content[key] = extracted_content

    # Create appropriate outline object based on type
    if outline_type == OutlineType.ROUGH:
        return RoughOutline(**content)
    elif outline_type == OutlineType.CHAPTER:
        return ChapterOutline(**content)
    elif outline_type == OutlineType.DETAILED:
        return DetailedOutline(**content)
    else:
        raise ValueError(f"Invalid outline type: {outline_type}")
