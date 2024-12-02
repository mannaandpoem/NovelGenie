import json
import os
from functools import wraps
from typing import Callable, Dict, List, Optional

from pydantic import BaseModel, Field, model_validator

from web_novel_gpt.config import config
from web_novel_gpt.logger import logger


class NovelIntent(BaseModel):
    """Novel generation intent model."""

    title: str = Field(..., description="小说名称")
    description: str = Field(..., description="小说的基本描述")
    genre: str = Field(..., description="小说的类型")


class NovelVolume(BaseModel):
    """Novel volume model."""

    volume_number: int = Field(..., ge=1, description="卷号")
    detailed_outline: str = Field(..., min_length=10, description="详细大纲")
    outline_summary: str = Field(..., min_length=10, description="大纲摘要")
    chapters: List[str] = Field(default_factory=list, description="章节内容列表")

    @model_validator(mode="after")
    def validate_chapters(self) -> "NovelVolume":
        if not all(len(chapter) > 0 for chapter in self.chapters):
            raise ValueError("所有章节都必须有内容")
        return self


class Novel(BaseModel):
    """Complete novel model."""

    intent: NovelIntent
    rough_outline: str = Field(..., min_length=10, description="粗略大纲")
    volumes: List[NovelVolume]
    cost_info: Dict = Field(default_factory=dict, description="成本信息")


class NovelSaver(BaseModel):
    """Novel saving and loading utility."""

    base_dir: str = Field(default_factory=lambda: config.novel.workspace)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure base directory exists
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_checkpoint_path(self, novel_id: str) -> str:
        return os.path.join(self.base_dir, f"{novel_id}_checkpoint.json")

    def _get_chapter_dir(self, novel_id: str) -> str:
        chapter_dir = os.path.join(self.base_dir, novel_id)
        os.makedirs(chapter_dir, exist_ok=True)
        return chapter_dir

    def save_checkpoint(self, novel_id: str, novel_data: Dict) -> None:
        """Save novel generation checkpoint."""
        checkpoint_path = self._get_checkpoint_path(novel_id)

        # Convert any Pydantic models to dict
        if isinstance(novel_data, BaseModel):
            novel_data = novel_data.model_dump()

        # Handle nested Pydantic models
        for key, value in novel_data.items():
            if isinstance(value, BaseModel):
                novel_data[key] = value.model_dump()
            elif isinstance(value, list):
                novel_data[key] = [
                    item.model_dump() if isinstance(item, BaseModel) else item
                    for item in value
                ]

        try:
            with open(checkpoint_path, "w", encoding="utf-8") as f:
                json.dump(novel_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving checkpoint: {str(e)}")
            raise

    def load_checkpoint(self, novel_id: str) -> Optional[Dict]:
        """Load existing checkpoint."""
        checkpoint_path = self._get_checkpoint_path(novel_id)
        try:
            if os.path.exists(checkpoint_path):
                with open(checkpoint_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading checkpoint: {str(e)}")
            return None
        return None

    def save_chapter(
        self, novel_id: str, volume_num: int, chapter_num: int, content: str
    ) -> None:
        """Save individual chapter content."""
        chapter_dir = self._get_chapter_dir(novel_id)
        chapter_path = os.path.join(chapter_dir, f"v{volume_num}_ch{chapter_num}.txt")
        try:
            with open(chapter_path, "w", encoding="utf-8") as f:
                if isinstance(content, BaseModel):
                    content = content.model_dump()
                f.write(str(content))
        except Exception as e:
            print(f"Error saving chapter: {str(e)}")
            raise


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
                        checkpoint_data = {"current_volume": result.model_dump()}
                    elif checkpoint_type == "novel":
                        checkpoint_data = result.model_dump()
                    else:
                        checkpoint_data = {
                            "intent": self.current_intent.model_dump()
                            if hasattr(self, "current_intent")
                            else None,
                            "rough_outline": self.current_rough_outline
                            if hasattr(self, "current_rough_outline")
                            else None,
                            "volumes": [v.model_dump() for v in self.current_volumes]
                            if hasattr(self, "current_volumes")
                            else [],
                            "current_volume": result.model_dump() if result else None,
                        }

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
