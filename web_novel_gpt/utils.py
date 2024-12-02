import json
import re
from functools import wraps
from typing import Callable, Tuple

from web_novel_gpt.logger import logger


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


def save_checkpoint(checkpoint_type: str):
    """
    装饰器：用于保存生成过程中的检查点
    Args:
        checkpoint_type: 检查点类型，如 'volume', 'chapter', 'novel'
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            try:
                result = await func(self, *args, **kwargs)

                if self.current_novel_id:
                    if checkpoint_type == "volume":
                        checkpoint_data = {
                            "intent": kwargs.get("intent").model_dump()
                            if "intent" in kwargs
                            else None,
                            "rough_outline": kwargs.get("rough_outline"),
                            "volumes": [
                                v.model_dump()
                                for v in getattr(self, "current_volumes", [])
                            ],
                            "current_volume": result.model_dump() if result else None,
                        }
                        self.novel_saver.save_checkpoint(
                            self.current_novel_id, checkpoint_data
                        )
                    elif checkpoint_type == "chapter":
                        # 从kwargs中获取volume_number和chapter_number
                        volume_number = kwargs.get("volume_number")
                        chapter_number = kwargs.get("designated_chapter")
                        if volume_number and chapter_number:
                            self.novel_saver.save_chapter(
                                self.current_novel_id,
                                volume_number,
                                chapter_number,
                                result,
                            )
                    elif checkpoint_type == "novel":
                        checkpoint_data = result.model_dump()
                        self.novel_saver.save_checkpoint(
                            self.current_novel_id, checkpoint_data
                        )

                    logger.info(
                        f"Saved {checkpoint_type} checkpoint for novel {self.current_novel_id}"
                    )

                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
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
