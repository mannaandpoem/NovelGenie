import json
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

    def _ensure_dirs(self, novel_id: str) -> Dict[str, Path]:
        """Ensure all required directories exist and return their paths."""
        novel_dir = Path(self.base_dir) / novel_id
        dirs = {
            "novel": novel_dir,
            "novel_content": novel_dir / "novel",
            "checkpoints": novel_dir / "checkpoints",
        }
        for path in dirs.values():
            path.mkdir(parents=True, exist_ok=True)
        return dirs

    def save_checkpoint(self, novel_id: str, novel_data: Dict) -> None:
        """Save novel generation checkpoint."""
        checkpoint_path = self._ensure_dirs(novel_id)["checkpoints"] / "checkpoint.json"

        def to_dict(data):
            if isinstance(data, BaseModel):
                return data.model_dump()
            elif isinstance(data, dict):
                return {k: to_dict(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [to_dict(item) for item in data]
            return data

        try:
            checkpoint_path.write_text(
                json.dumps(to_dict(novel_data), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            raise RuntimeError(f"Failed to save checkpoint: {e}") from e

    def save_chapter(
        self, novel_id: str, volume_num: int, chapter_num: int, content: str
    ) -> None:
        """Save individual chapter content."""
        volume_dir = (
            self._ensure_dirs(novel_id)["novel_content"] / f"volume_{volume_num}"
        )
        volume_dir.mkdir(exist_ok=True)

        chapter_path = volume_dir / f"chapter_{chapter_num}.txt"
        try:
            content_str = (
                content.model_dump() if isinstance(content, BaseModel) else str(content)
            )
            chapter_path.write_text(content_str, encoding="utf-8")
        except Exception as e:
            raise RuntimeError(f"Failed to save chapter: {e}") from e

    def load_checkpoint(self, novel_id: str) -> Optional[Dict]:
        """Load existing checkpoint if available."""
        checkpoint_path = self._ensure_dirs(novel_id)["checkpoints"] / "checkpoint.json"
        try:
            return (
                json.loads(checkpoint_path.read_text(encoding="utf-8"))
                if checkpoint_path.exists()
                else None
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load checkpoint: {e}") from e
