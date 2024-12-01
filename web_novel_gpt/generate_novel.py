import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from datetime import datetime
from web_novel_gpt.llm import LLM
from web_novel_gpt.prompts.chapter_generator_prompt import CHAPTER_GENERATOR_PROMPT
from web_novel_gpt.prompts.content_optimizer_prompt import CONTENT_OPTIMIZER_PROMPT
from web_novel_gpt.prompts.detail_outline_generator_prompt import (
    DETAILED_OUTLINE_GENERATOR_PROMPT,
    DETAILED_OUTLINE_SUMMARY_PROMPT
)
from web_novel_gpt.prompts.intent_analyzer_prompt import INTENT_ANALYZER_PROMPT
from web_novel_gpt.prompts.rough_outline_prompt import ROUGH_OUTLINE_GENERATOR_PROMPT
from web_novel_gpt.utils import Cost, parse_intent


@dataclass
class NovelIntent:
    """Data class for storing novel generation intent."""
    description: str
    genre: str
    word_count: int
    volume_count: int = 1


@dataclass
class NovelVolume:
    """Data class for storing novel volume data."""
    volume_number: int
    detailed_outline: str
    outline_summary: str
    chapters: List[str]


@dataclass
class Novel:
    """Data class for storing complete novel data."""
    intent: NovelIntent
    rough_outline: str
    volumes: List[NovelVolume]
    cost_info: Dict


class NovelSaver:
    """处理小说保存和加载的工具类"""

    def __init__(self, base_dir: str = "../workspace/novel_checkpoints"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def _get_checkpoint_path(self, novel_id: str) -> str:
        return os.path.join(self.base_dir, f"{novel_id}_checkpoint.json")

    def _get_chapter_dir(self, novel_id: str) -> str:
        chapter_dir = os.path.join(self.base_dir, novel_id)
        os.makedirs(chapter_dir, exist_ok=True)
        return chapter_dir

    def save_checkpoint(self, novel_id: str, novel_data: Dict) -> None:
        """保存小说生成的检查点"""
        checkpoint_path = self._get_checkpoint_path(novel_id)
        with open(checkpoint_path, 'w', encoding='utf-8') as f:
            json.dump(novel_data, f, ensure_ascii=False, indent=2)

    def load_checkpoint(self, novel_id: str) -> Optional[Dict]:
        """加载已有的检查点"""
        checkpoint_path = self._get_checkpoint_path(novel_id)
        if os.path.exists(checkpoint_path):
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def save_chapter(self, novel_id: str, volume_num: int, chapter_num: int, content: str) -> None:
        """保存单独的章节内容"""
        chapter_dir = self._get_chapter_dir(novel_id)
        chapter_path = os.path.join(chapter_dir, f"v{volume_num}_ch{chapter_num}.txt")
        with open(chapter_path, 'w', encoding='utf-8') as f:
            f.write(content)


class WebNovelGPT:
    def __init__(self):
        """Initialize WebNovelGPT with LLM provider and cost tracker."""
        self.llm = LLM()
        self.cost_tracker = Cost()
        self.novel_saver = NovelSaver()
        self._current_novel_id = None

    @staticmethod
    def _generate_novel_id(description: str) -> str:
        """生成唯一的小说ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{description[:5]}_{timestamp}"

    async def analyze_intent(self, user_input: str) -> NovelIntent:
        """Analyze user input to extract story details."""
        prompt = INTENT_ANALYZER_PROMPT.format(user_input=user_input)
        response = await self.llm.ask(prompt)
        description, genre, word_count, volume_count = parse_intent(response)
        return NovelIntent(description, genre, word_count, volume_count)

    async def generate_rough_outline(self, user_input, intent: NovelIntent) -> str:
        """Generate rough outline based on story intent."""
        prompt = ROUGH_OUTLINE_GENERATOR_PROMPT.format(
            user_input=user_input,
            genre=intent.genre,
            description=intent.description,
            word_count=intent.word_count,
            volume_count=intent.volume_count
        )
        return await self.llm.ask(prompt)

    async def generate_detailed_outline_summary(
            self,
            volume_number: int,
            rough_outline: str,
            detailed_outline: str
    ) -> str:
        """Generate summary of detailed outline."""
        prompt = DETAILED_OUTLINE_SUMMARY_PROMPT.format(
            volume_number=volume_number,
            rough_outline=rough_outline,
            detailed_outline=detailed_outline
        )
        return await self.llm.ask(prompt)

    @staticmethod
    def _split_into_chapters(detailed_outline: str) -> List[str]:
        """Split detailed outline into chapter outlines."""
        return [
            outline.strip()
            for outline in detailed_outline.split("\n\n")
            if outline.strip()
        ]

    async def generate_chapter(
            self,
            designated_chapter: int,
            detailed_outline: str,
            rough_outline: str,
            section_word_count: int = 2000,
            chapters: List[str] = None
    ) -> str:
        """Generate a single chapter."""

        prompt = CHAPTER_GENERATOR_PROMPT.format(
            designated_chapter=designated_chapter,
            rough_outline=rough_outline,
            detailed_outline=detailed_outline,
            section_word_count=section_word_count,
            chapters="\n\n".join(chapters) if chapters else ""
        )
        return await self.llm.ask(prompt)

    async def _optimize_chapter(
            self,
            chapter: str,
            section_word_count: int
    ) -> str:
        """Optimize a single chapter."""
        prompt = CONTENT_OPTIMIZER_PROMPT.format(
            chapter_content=chapter,
            section_word_count=section_word_count
        )
        return await self.llm.ask(prompt)

    async def generate_volume(
            self,
            volume_number: int,
            intent: NovelIntent,
            rough_outline: str,
            section_word_count: int,
            prev_volume_summary: Optional[str] = None,
            need_optimization: bool = False
    ) -> NovelVolume:
        """Generate a complete volume of the novel."""
        # 生成详细大纲
        detailed_outline = await self.generate_detailed_outline(
            volume_number=volume_number,
            description=intent.description,
            rough_outline=rough_outline,
            section_word_count=section_word_count,
            prev_volume_summary=prev_volume_summary
        )

        # 生成大纲摘要
        outline_summary = await self.generate_detailed_outline_summary(
            volume_number=volume_number,
            rough_outline=rough_outline,
            detailed_outline=detailed_outline
        )

        # 按章节顺序生成内容
        chapter_outlines = self._split_into_chapters(detailed_outline)
        chapters = []

        # 保存当前进度
        volume_data = {
            "volume_number": volume_number,
            "detailed_outline": detailed_outline,
            "outline_summary": outline_summary,
            "chapters": chapters
        }

        for i, chapter_outline in enumerate(chapter_outlines, 1):
            try:
                chapter = await self.generate_chapter(
                    designated_chapter=i,
                    detailed_outline=chapter_outline,  # TODO: Fix this
                    rough_outline=rough_outline,
                    section_word_count=section_word_count,
                    chapters=chapters
                )
                if need_optimization:
                    chapter = await self._optimize_chapter(chapter, section_word_count)

                chapters.append(chapter)

                # 保存单独的章节文件
                if self._current_novel_id:
                    self.novel_saver.save_chapter(
                        self._current_novel_id,
                        volume_number,
                        i,
                        chapter
                    )

                # 更新并保存检查点
                volume_data["chapters"] = chapters
                if self._current_novel_id:
                    self.novel_saver.save_checkpoint(
                        self._current_novel_id,
                        {"current_volume": volume_data}
                    )

            except Exception as e:
                print(f"Error generating chapter {i} in volume {volume_number}: {str(e)}")
                # 保存当前进度，即使发生错误
                if self._current_novel_id:
                    self.novel_saver.save_checkpoint(
                        self._current_novel_id,
                        {"current_volume": volume_data}
                    )
                raise

        return NovelVolume(
            volume_number=volume_number,
            detailed_outline=detailed_outline,
            outline_summary=outline_summary,
            chapters=chapters
        )

    async def generate_detailed_outline(
            self,
            volume_number: int,
            description: str,
            rough_outline: str,
            section_word_count: int,
            prev_volume_summary: Optional[str] = None
    ) -> str:
        """Generate detailed outline for a volume."""
        prompt = DETAILED_OUTLINE_GENERATOR_PROMPT.format(
            designated_volume=volume_number,
            description=description,
            rough_outline=rough_outline,
            section_word_count=section_word_count,
            prev_volume_summary=prev_volume_summary if prev_volume_summary else "This is the first volume."
        )
        return await self.llm.ask(prompt)

    async def generate_volumes(
            self,
            num_volumes: int,
            intent: NovelIntent,
            rough_outline: str,
            section_word_count: int,
            prev_volume_summary: Optional[str] = None
    ) -> List[NovelVolume]:
        """Generate volumes for the novel."""
        volumes = []

        for i in range(num_volumes):
            volume = await self.generate_volume(
                volume_number=i + 1,
                intent=intent,
                rough_outline=rough_outline,
                section_word_count=section_word_count,
                prev_volume_summary=prev_volume_summary
            )
            volumes.append(volume)
            prev_volume_summary = volume.outline_summary

            # 保存当前进度
            current_state = {
                "intent": asdict(intent),
                "rough_outline": rough_outline,
                "volumes": [asdict(v) for v in volumes],
                "current_volume": None
            }
            self.novel_saver.save_checkpoint(self._current_novel_id, current_state)

        return volumes

    async def generate_novel(
            self,
            user_input: str,
            genre: Optional[str] = None,
            section_word_count: int = 2000,
            num_volumes: int = 1,
            resume_novel_id: Optional[str] = None
    ) -> Dict:
        """Generate complete novel from user input."""
        # 如果提供了 novel_id，尝试恢复之前的进度
        if resume_novel_id:
            self._current_novel_id = resume_novel_id
            checkpoint = self.novel_saver.load_checkpoint(resume_novel_id)
            if checkpoint:
                print(f"Resuming from checkpoint for novel {resume_novel_id}")
                return await self._resume_generation(checkpoint, section_word_count, num_volumes)

        # 新建小说生成进程
        intent = await self.analyze_intent(user_input)
        if genre:
            intent.genre = genre

        # 生成新的 novel_id
        self._current_novel_id = self._generate_novel_id(intent.description)

        rough_outline = await self.generate_rough_outline(user_input, intent)

        # 保存初始状态
        initial_state = {
            "intent": asdict(intent),
            "rough_outline": rough_outline,
            "volumes": [],
            "current_volume": None
        }
        self.novel_saver.save_checkpoint(self._current_novel_id, initial_state)

        # 按卷生成内容
        volumes = await self.generate_volumes(num_volumes, intent, rough_outline, section_word_count)

        novel = Novel(
            intent=intent,
            rough_outline=rough_outline,
            volumes=volumes,
            cost_info=self.cost_tracker.get()
        )

        # 保存最终小说内容
        self.novel_saver.save_checkpoint(self._current_novel_id, asdict(novel))

        return asdict(novel)

    async def _resume_generation(
            self,
            checkpoint: Dict,
            section_word_count: int,
            num_volumes: int
    ) -> Dict:
        """从检查点恢复小说生成"""
        intent = NovelIntent(**checkpoint["intent"])
        rough_outline = checkpoint["rough_outline"]
        volumes = [NovelVolume(**v) for v in checkpoint["volumes"]]

        # 从上次中断的地方继续
        current_volume = len(volumes)
        prev_volume_summary = volumes[-1].outline_summary if volumes else None

        volumes = await self.generate_volumes(
            num_volumes - current_volume,
            intent,
            rough_outline,
            section_word_count,
            prev_volume_summary
        )

        novel = Novel(
            intent=intent,
            rough_outline=rough_outline,
            volumes=volumes,
            cost_info=self.cost_tracker.get()
        )

        return asdict(novel)
