import json
import re
from functools import wraps
from typing import Any, Awaitable, Callable, Dict, Optional, Tuple, TypeVar, Union

from pydantic import BaseModel

from web_novel_gpt.logger import logger
from web_novel_gpt.schema import (
    ChapterOutline,
    CheckpointKeys,
    CheckpointType,
    DetailedOutline,
    Novel,
    NovelIntent,
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


def save_checkpoint(checkpoint_type: Union[str, CheckpointType]):
    """
    装饰器: 用于保存生成过程中的检查点

    Args:
        checkpoint_type: 检查点类型,支持 'volume', 'chapter', 'novel'
    """

    def prepare_volume_checkpoint(
        self,
        result: Optional[NovelVolume],
        intent: Optional[NovelIntent],
        rough_outline: Optional[OutlineType],
    ) -> Dict[str, Any]:
        """准备卷级别检查点数据"""
        return {
            CheckpointKeys.INTENT: intent.model_dump() if intent else None,
            CheckpointKeys.ROUGH_OUTLINE: serialize_outline(rough_outline),
            CheckpointKeys.VOLUMES: [
                v.model_dump() for v in getattr(self, "current_volumes", [])
            ],
            CheckpointKeys.CURRENT_VOLUME: result.model_dump() if result else None,
            CheckpointKeys.CURRENT_OUTLINES["chapter"]: serialize_outline(
                getattr(self, "current_chapter_outline", None)
            ),
            CheckpointKeys.CURRENT_OUTLINES["detailed"]: serialize_outline(
                getattr(self, "current_detailed_outline", None)
            ),
        }

    def prepare_chapter_checkpoint(
        self,
        result: str,
    ) -> Dict[str, Any]:
        """准备章节级别检查点数据"""
        return {
            CheckpointKeys.CHAPTER_CONTENT: result,
            CheckpointKeys.DETAILED_OUTLINE: serialize_outline(
                getattr(self, "current_detailed_outline", None)
            ),
            CheckpointKeys.CHAPTER_OUTLINE: serialize_outline(
                getattr(self, "current_chapter_outline", None)
            ),
        }

    def prepare_novel_checkpoint(
        self,
        result: Novel,
    ) -> Dict[str, Any]:
        """准备小说级别检查点数据"""
        checkpoint_data = {
            **result.model_dump(),
            CheckpointKeys.OUTLINE_OBJECTS["rough"]: serialize_outline(
                getattr(self, "current_rough_outline", None)
            ),
            CheckpointKeys.OUTLINE_OBJECTS["chapter"]: serialize_outline(
                getattr(self, "current_chapter_outline", None)
            ),
            CheckpointKeys.OUTLINE_OBJECTS["detailed"]: serialize_outline(
                getattr(self, "current_detailed_outline", None)
            ),
        }
        # 确保cost_info存在
        if CheckpointKeys.COST_INFO not in checkpoint_data:
            checkpoint_data[CheckpointKeys.COST_INFO] = {}

        return checkpoint_data

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(self, *args, **kwargs) -> T:
            if not self.current_novel_id:
                logger.warning("No current novel ID found, skipping checkpoint save")
                return await func(self, *args, **kwargs)

            try:
                result = await func(self, *args, **kwargs)

                # Step 2: 根据检查点类型准备数据
                if checkpoint_type == CheckpointType.VOLUME:
                    checkpoint_data = prepare_volume_checkpoint(
                        self,
                        result,
                        kwargs.get("intent"),
                        kwargs.get("rough_outline"),
                    )
                    self.novel_saver.save_checkpoint(
                        self.current_novel_id, checkpoint_data
                    )

                elif checkpoint_type == CheckpointType.CHAPTER:
                    volume_number = kwargs.get("volume_number")
                    chapter_number = kwargs.get("designated_chapter")
                    if not (volume_number and chapter_number):
                        logger.warning(
                            "Missing volume_number or chapter_number for chapter checkpoint"
                        )
                    else:
                        checkpoint_data = prepare_chapter_checkpoint(self, result)
                        self.novel_saver.save_chapter(
                            self.current_novel_id,
                            volume_number,
                            chapter_number,
                            checkpoint_data,
                        )

                elif checkpoint_type == CheckpointType.NOVEL:
                    checkpoint_data = prepare_novel_checkpoint(self, result)
                    self.novel_saver.save_checkpoint(
                        self.current_novel_id, checkpoint_data
                    )
                else:
                    logger.warning(f"Unknown checkpoint type: {checkpoint_type}")
                    return result

                logger.info(
                    f"Successfully saved {checkpoint_type} checkpoint for "
                    f"novel {self.current_novel_id}"
                )

                return result

            except Exception as e:
                logger.error(
                    f"Error saving {checkpoint_type} checkpoint: {str(e)}",
                    exc_info=True,
                )
                raise

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


def extract_content(
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
    for key, tag in tag_mappings[outline_type].items():
        extracted_content = extract_tag_content(tag)
        if extracted_content is None:
            raise ValueError(f"Required content '{tag}' not found in document")
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
