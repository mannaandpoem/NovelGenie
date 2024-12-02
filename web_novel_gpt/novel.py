import json
import os
from pathlib import Path
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


class NovelSaver(BaseModel):
    """Novel saving and loading utility with organized directory structure."""

    base_dir: str = Field(default_factory=lambda: config.novel.workspace)

    class Config:
        arbitrary_types_allowed = True

    @model_validator(mode="after")
    def validate_structure(self) -> "NovelSaver":
        """Ensure required subdirectory structure exists."""
        base_path = Path(self.base_dir)
        if not base_path.exists():
            raise ValueError(f"Base directory {self.base_dir} does not exist")
        return self

    def _get_novel_dir(self, novel_id: str) -> str:
        """Get or create the novel-specific directory."""
        novel_dir = os.path.join(self.base_dir, novel_id)
        os.makedirs(novel_dir, exist_ok=True)
        return novel_dir

    def _get_chapters_dir(self, novel_id: str) -> str:
        """Get or create the chapters directory for a novel."""
        chapters_dir = os.path.join(self._get_novel_dir(novel_id), "chapters")
        os.makedirs(chapters_dir, exist_ok=True)
        return chapters_dir

    def _get_checkpoints_dir(self, novel_id: str) -> str:
        """Get or create the checkpoints directory for a novel."""
        checkpoints_dir = os.path.join(self._get_novel_dir(novel_id), "checkpoints")
        os.makedirs(checkpoints_dir, exist_ok=True)
        return checkpoints_dir

    def _get_checkpoint_path(self, novel_id: str) -> str:
        """Get the full path for a checkpoint file."""
        return os.path.join(self._get_checkpoints_dir(novel_id), "checkpoint.json")

    def save_checkpoint(self, novel_id: str, novel_data: Dict) -> None:
        """Save novel generation checkpoint in organized directory structure."""
        checkpoint_path = self._get_checkpoint_path(novel_id)

        # Convert Pydantic models to dict recursively
        def convert_to_dict(data):
            if isinstance(data, BaseModel):
                return data.model_dump()
            elif isinstance(data, dict):
                return {k: convert_to_dict(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [convert_to_dict(item) for item in data]
            return data

        novel_data = convert_to_dict(novel_data)

        try:
            with open(checkpoint_path, "w", encoding="utf-8") as f:
                json.dump(novel_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving checkpoint: {str(e)}")
            raise

    def save_chapter(
        self, novel_id: str, volume_num: int, chapter_num: int, content: str
    ) -> None:
        """Save individual chapter content in organized directory structure."""
        chapter_dir = self._get_chapters_dir(novel_id)
        volume_dir = os.path.join(chapter_dir, f"volume_{volume_num}")
        os.makedirs(volume_dir, exist_ok=True)

        chapter_path = os.path.join(volume_dir, f"chapter_{chapter_num}.txt")
        try:
            content_to_save = (
                content.model_dump() if isinstance(content, BaseModel) else str(content)
            )
            with open(chapter_path, "w", encoding="utf-8") as f:
                f.write(content_to_save)
        except Exception as e:
            print(f"Error saving chapter: {str(e)}")
            raise

    def load_checkpoint(self, novel_id: str) -> Optional[Dict]:
        """Load existing checkpoint from organized directory structure."""
        checkpoint_path = self._get_checkpoint_path(novel_id)
        try:
            if os.path.exists(checkpoint_path):
                with open(checkpoint_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading checkpoint: {str(e)}")
            return None
        return None
