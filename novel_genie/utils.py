import json
from functools import wraps
from typing import Any, Awaitable, Callable, Dict, Optional, Tuple, TypeVar, Union, cast

from pydantic import BaseModel

from novel_genie.logger import logger
from novel_genie.schema import (
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


import ast
import re
from typing import List


def extract_code_content(response: str, language: str = None) -> str:
    """
    Extract code content from LLM response, supporting multiple formats including JSON and Python.

    Args:
        response (str): Raw response from LLM
        language (str, optional): Expected language/format (e.g., 'json', 'python').
                                  If None, tries to detect automatically.

    Returns:
        str: Cleaned code content string
    """
    # Pattern to capture code blocks with optional language specifier
    code_block_pattern = r"```(?:\w+)?\s*([\s\S]*?)\s*```"
    block_matches = re.finditer(code_block_pattern, response)

    for match in block_matches:
        content = match.group(1).strip()
        if language:
            lang_pattern = rf"```{language}\s*([\s\S]*?)\s*```"
            if re.match(lang_pattern, match.group(0), re.IGNORECASE):
                return content
        else:
            if content:
                return content

    # Fallback: attempt to find JSON or Python literals outside code blocks
    if not language or language.lower() == "json":
        json_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", response)
        if json_match:
            return json_match.group(1).strip()
    elif language.lower() == "python":
        python_match = re.search(r"(?:\[.*\])", response, re.DOTALL)
        if python_match:
            return python_match.group(1).strip()

    return response.strip()


def extract_commands_from_response(response_text: str) -> List[str]:
    """
    Extract the commands list from the response text.

    Args:
        response_text (str): The raw response text containing commands

    Returns:
        list: List of edit commands
    """
    # Extract the code content assuming it's Python code
    code_content = extract_code_content(response_text, language="python")

    try:
        # Safely evaluate the Python list using ast.literal_eval
        # Find the cmds list assignment
        cmds_match = re.search(r"cmds\s*=\s*(\[[\s\S]*\])", code_content)
        if not cmds_match:
            raise ValueError("No 'cmds' list found in the code content.")

        cmds_str = cmds_match.group(1)
        cmds = ast.literal_eval(cmds_str)
        if not isinstance(cmds, list):
            raise ValueError("'cmds' is not a list.")
        return cmds
    except Exception as e:
        raise ValueError(f"Error parsing commands: {e}")


def process_edit_commands(original_content: str, commands: List[str]) -> str:
    """
    Apply multiple edit commands to the original text content.

    Args:
        original_content (str): The original text content
        commands (list): List of edit commands in the format:
                        ["edit start:end <<EOF\nnew content\nEOF", ...]

    Returns:
        str: Modified text content after applying all edits
    """
    lines = original_content.splitlines()

    parsed_commands = []
    for cmd in commands:
        # Regex to parse the edit command
        match = re.match(r"edit\s+(\d+):(\d+)\s+<<EOF\s*\n([\s\S]*?)\nEOF", cmd.strip())
        if match:
            start_line = int(match.group(1))
            end_line = int(match.group(2))
            replacement = match.group(3).split("\n")
            parsed_commands.append((start_line, end_line, replacement))
        else:
            raise ValueError(f"Invalid edit command format: {cmd}")

    # Sort commands by start_line in descending order to avoid line number shifts
    parsed_commands.sort(key=lambda x: x[0], reverse=True)

    for start, end, replacement in parsed_commands:
        if start < 1 or end > len(lines):
            raise IndexError(f"Edit range {start}:{end} is out of bounds.")
        # Replace the specified range with the replacement lines
        lines[start - 1 : end] = replacement

    return "\n".join(lines)


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
    intent = extract_code_content(response)
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

    def extract_tag_content(
        tag: str, is_list: bool = False
    ) -> Union[str, List[str], None]:
        """
        Helper function to extract content between tags.

        Args:
            tag (str): The tag name to extract content from.
            is_list (bool): If True, extracts multiple instances of the tag as a list.

        Returns:
            Union[str, List[str], None]: Extracted content as string or list of strings.
        """
        pattern = f"<{tag}>(.*?)</{tag}>"
        if is_list:
            matches = re.finditer(pattern, document, re.DOTALL)
            return [match.group(1).strip() for match in matches] if matches else None
        else:
            match = re.search(pattern, document, re.DOTALL)
            return match.group(1).strip() if match else None

    # Tag mappings for different outline types with type hints
    tag_mappings = {
        OutlineType.ROUGH: {
            "worldview_system": ("worldview_system", False),
            "character_system": ("character_system", False),
            "volume_design": ("volume_design", True),  # Now marked as a list
        },
        OutlineType.CHAPTER: {
            "chapter_overview": ("chapter_overview", False),
            "characters_content": ("characters_content", False),
        },
        OutlineType.DETAILED: {"storyline": ("storyline", False)},
    }

    # Extract content based on outline type
    content = {}
    for key, (tag, is_list) in tag_mappings[outline_type].items():
        extracted_content = extract_tag_content(tag, is_list)
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
