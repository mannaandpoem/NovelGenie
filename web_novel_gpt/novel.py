import json
import os
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, model_validator

from web_novel_gpt.config import config


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


# novel.py
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
