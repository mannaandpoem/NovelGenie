import json
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, model_validator

from novel_genie.config import config


class OutlineType(str, Enum):
    """Outline type enumeration."""

    ROUGH = "rough"
    CHAPTER = "chapter"
    DETAILED = "detailed"


class CheckpointType(str, Enum):
    """检查点类型枚举"""

    VOLUME = "volume"
    CHAPTER = "chapter"
    NOVEL = "novel"


class OutlineBase(BaseModel):
    """Base outline model with common fields."""

    outline_type: OutlineType

    class Config:
        from_attributes = True


class RoughOutline(OutlineBase):
    """Novel-level rough outline."""

    outline_type: OutlineType = OutlineType.ROUGH
    worldview_system: str = Field(..., min_length=10)
    character_system: str = Field(..., min_length=10)
    volume_design: list = Field(default_factory=list)


class ChapterOutline(OutlineBase):
    """Volume-level chapter outline."""

    outline_type: OutlineType = OutlineType.CHAPTER
    chapter_overview: str = Field(..., min_length=10)
    characters_content: str = Field(..., min_length=10)

    def __str__(self):
        return f"{self.chapter_overview}\n\n{self.characters_content}"


class DetailedOutline(OutlineBase):
    """Chapter-level detailed outline."""

    outline_type: OutlineType = OutlineType.DETAILED
    storyline: str = Field(..., min_length=10)

    def __str__(self):
        return self.storyline


class Chapter(BaseModel):
    """Chapter model with its own outline."""

    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=100)

    def __str__(self):
        return f"{self.title}\n\n{self.content}"


class NovelVolume(BaseModel):
    """Volume model containing chapters and outlines."""

    volume_num: int = Field(..., ge=1)
    chapter_outlines: List[Optional[ChapterOutline]] = Field(default_factory=list)
    detailed_outlines: List[Optional[DetailedOutline]] = Field(default_factory=list)
    chapters: List[Optional[Chapter]] = Field(default_factory=list)


class NovelIntent(BaseModel):
    """Novel generation intent model."""

    title: str = Field(..., description="小说名称")
    description: str = Field(..., description="小说的基本描述")
    genre: str = Field("轻小说", description="小说的类型")
    work_length: str = Field("短篇", description="小说的篇幅")


class Novel(BaseModel):
    """Complete novel model with hierarchical structure."""

    intent: NovelIntent
    rough_outline: RoughOutline  # 小说级别大纲
    volumes: List[NovelVolume]
    cost_info: Dict = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_novel(self) -> "Novel":
        # 验证卷号连续性
        volume_nums = [vol.volume_num for vol in self.volumes]
        expected_numbers = list(range(1, len(self.volumes) + 1))
        if volume_nums != expected_numbers:
            raise ValueError("Volume numbers must be sequential")
        return self


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

        checkpoint_path.write_text(
            json.dumps(to_dict(novel_data), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def save_chapter(
        self, novel_id: str, volume_num: int, chapter_num: int, chapter: Chapter
    ) -> None:
        """Save individual chapter content."""
        volume_dir = (
            self._ensure_dirs(novel_id)["novel_content"] / f"volume_{volume_num}"
        )
        volume_dir.mkdir(exist_ok=True)

        chapter_path = volume_dir / f"chapter_{chapter_num}.txt"
        chapter_path.write_text(str(chapter), encoding="utf-8")

    def load_checkpoint(self, novel_id: str) -> Optional[Dict]:
        """Load existing checkpoint if available."""
        checkpoint_path = self._ensure_dirs(novel_id)["checkpoints"] / "checkpoint.json"
        if checkpoint_path.exists():
            return json.loads(checkpoint_path.read_text(encoding="utf-8"))
        return None


def create_sample_novel():
    rough_outline = RoughOutline(
        worldview_system="魔法世界体系" * 10,
        character_system="主角是一位年轻魔法师" * 10,
        plot_design="探索魔法世界的冒险故事" * 10,
    )

    chapter_outline = ChapterOutline(
        chapter_overview="第一卷整体概述" * 10,
        characters_content="主要角色介绍" * 10,
        volume_num=1,
    )

    detailed_outline = DetailedOutline(storyline="第一章详细故事情节" * 10, chapter_num=1)

    chapter = Chapter(
        title="第一章",
        content="章节具体内容..." * 100,
    )

    volume = NovelVolume(
        volume_num=1,
        chapter_outline=chapter_outline,
        chapters=[chapter],
        detailed_outline=detailed_outline,
    )

    return Novel(
        intent=NovelIntent(title="示例小说", description="这是一个示例小说" * 10, genre="奇幻"),
        rough_outline=rough_outline,
        volumes=[volume],
        cost_info={"cost": 1000},
    )


if __name__ == "__main__":
    novel = create_sample_novel()
    print(novel.model_dump_json(indent=2))
