import ast
import inspect
import json
import re
from functools import wraps
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
)

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


def extract_code_content(
    response: str, language: str = "", filter_others: bool = True
) -> str:
    """
    提取或移除响应中的代码块，基于指定的语言和过滤标志。

    Args:
        response (str): 包含代码块的原始响应。
        language (str, optional): 要过滤的语言。如果为空，则根据 `filter_others` 处理所有代码块。
        filter_others (bool, optional):
            - 如果为 True:
                - 保留指定语言的代码块。
                - 如果 `language` 为空，保留没有语言标识符的纯代码块。
            - 如果为 False:
                - 移除指定语言的代码块。
                - 如果 `language` 为空，移除所有代码块。

    Returns:
        str: 过滤后的响应内容。
    """
    # 定义支持的语言
    supported_languages = {"", "thinking", "python", "json"}

    # 输入验证
    if not isinstance(response, str):
        raise TypeError("Response must be a string")
    if not isinstance(language, str):
        raise TypeError("Language must be a string")
    if not isinstance(filter_others, bool):
        raise TypeError("filter_others must be a boolean")

    language = language.lower()
    if language not in supported_languages:
        raise ValueError(
            f"Language must be one of: {', '.join(repr(l) for l in supported_languages)}"
        )

    # 正则表达式匹配代码块
    # 捕获可选的语言标识符和代码内容
    block_pattern = r"```(?P<lang>\w+)?\n?(?P<content>[\s\S]*?)```"

    # 查找所有代码块
    blocks = list(re.finditer(block_pattern, response))

    if not blocks:
        return response.strip()  # 如果没有代码块，返回原始响应

    # 初始化新响应的列表
    new_response = []
    last_pos = 0  # 记录上一个匹配结束的位置

    # 遍历所有代码块
    for match in blocks:
        start, end = match.span()
        block_lang = (match.group("lang") or "").lower()
        block_content = match.group("content").strip()

        # 将代码块之前的文本添加到新响应中
        new_response.append(response[last_pos:start])

        if filter_others:
            if language:
                # 保留指定语言的代码块内容
                if block_lang == language:
                    new_response.append(block_content)
                # 否则移除代码块（不添加任何内容）
            else:
                # 保留没有语言标识符的纯代码块内容
                if not block_lang:
                    new_response.append(block_content)
                # 否则移除代码块
        else:
            if language:
                # 移除指定语言的代码块，保留其他代码块（包括标识符）
                if block_lang != language:
                    new_response.append(match.group(0))  # 保留整个代码块
                # 否则移除代码块（不添加任何内容）
            else:
                # 移除所有代码块
                pass  # 不添加任何内容

        # 更新上一个匹配结束的位置
        last_pos = end

    # 添加最后一个代码块之后的文本
    new_response.append(response[last_pos:])

    # 连接所有部分并返回
    return "".join(new_response).strip()


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


def parse_intent(response: str) -> Tuple[str, str, str, str]:
    """
    Parse intent analysis response and extract components.

    Args:
        response (str): Response string from intent analysis

    Returns:
        Tuple[str, str, str]: (description, genre, word_count)
    """
    intent = extract_code_content(response, language="json")
    intent_json = json.loads(intent)
    return (
        intent_json.get("title"),
        intent_json.get("description"),
        intent_json.get("genre"),
        intent_json.get("work_length"),
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


def filter_thinking_blocks() -> (
    Callable[
        [Callable[..., Union[str, Awaitable[str]]]],
        Callable[..., Union[str, Awaitable[str]]],
    ]
):
    """
    Decorator that removes `thinking` language code blocks from function return values.
    Supports both synchronous and asynchronous functions.

    Returns:
        Callable: Decorated function that automatically filters `thinking` code blocks from the return value.
    """

    def decorator(
        func: Callable[..., Union[str, Awaitable[str]]]
    ) -> Callable[..., Union[str, Awaitable[str]]]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> str:
            result = await func(*args, **kwargs)
            # If there are no 'thinking' code blocks, return the result as is
            if "```thinking" not in result:
                return result
            # Remove the 'thinking' blocks and return the cleaned result
            return extract_code_content(
                result, language="thinking", filter_others=False
            )

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> str:
            result = func(*args, **kwargs)
            # If there are no 'thinking' code blocks, return the result as is
            if "```thinking" not in result:
                return result
            # Remove the 'thinking' blocks and return the cleaned result
            return extract_code_content(
                result, language="thinking", filter_others=False
            )

        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

    return decorator
