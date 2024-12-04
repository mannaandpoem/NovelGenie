import re
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from web_novel_gpt.config import WebNovelGenerationConfig
from web_novel_gpt.cost import Cost
from web_novel_gpt.llm import LLM
from web_novel_gpt.logger import logger
from web_novel_gpt.prompts.chapter_outline_generator_prompt import (
    CHAPTER_OUTLINE_GENERATOR_PROMPT,
)
from web_novel_gpt.prompts.content_generator_prompt import CONTENT_GENERATOR_PROMPT
from web_novel_gpt.prompts.content_optimizer_prompt import CONTENT_OPTIMIZER_PROMPT
from web_novel_gpt.prompts.detail_outline_generator_prompt import (
    DETAILED_OUTLINE_GENERATOR_PROMPT_V2,
    DETAILED_OUTLINE_SUMMARY_PROMPT,
)
from web_novel_gpt.prompts.intent_analyzer_prompt import INTENT_ANALYZER_PROMPT
from web_novel_gpt.prompts.rough_outline_prompt import ROUGH_OUTLINE_GENERATOR_PROMPT_V2
from web_novel_gpt.schema import (
    ChapterOutline,
    DetailedOutline,
    Novel,
    NovelIntent,
    NovelSaver,
    NovelVolume,
    OutlineType,
    RoughOutline,
)
from web_novel_gpt.utils import (
    extract_content,
    load_outline_from_dict,
    parse_intent,
    save_checkpoint,
)


class WebNovelGPT(BaseModel):
    """Web novel generation main class."""

    llm: LLM = Field(default_factory=LLM)
    cost_tracker: Cost = Field(default_factory=Cost)
    novel_saver: NovelSaver = Field(default_factory=NovelSaver)
    gen_config: WebNovelGenerationConfig = Field(
        default_factory=WebNovelGenerationConfig
    )
    current_novel_id: Optional[str] = Field(None, exclude=True)
    current_intent: Optional[NovelIntent] = Field(None, exclude=True)
    current_volumes: List[NovelVolume] = Field(default_factory=list, exclude=True)
    current_rough_outline: Optional[RoughOutline] = Field(None, exclude=True)
    current_chapter_outline: Optional[ChapterOutline] = Field(None, exclude=True)
    current_detailed_outline: Optional[DetailedOutline] = Field(None, exclude=True)

    class Config:
        arbitrary_types_allowed = True

    @staticmethod
    def _generate_novel_id(description: str) -> str:
        """Generate unique novel ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{description[:5]}_{timestamp}"

    async def analyze_intent(self, user_input: str) -> NovelIntent:
        """Analyze user input to extract story details."""
        logger.info("Analyzing user input to extract story details")
        prompt = INTENT_ANALYZER_PROMPT.format(user_input=user_input)
        response = await self.llm.ask(prompt)
        title, description, genre = parse_intent(response)
        return NovelIntent(
            title=title,
            description=description,
            genre=genre,
        )

    async def generate_rough_outline(
        self, user_input: str, intent: Optional[NovelIntent] = None
    ) -> RoughOutline:
        """Generate rough outline based on story intent."""
        logger.info(f"Generating rough outline for novel '{intent.title}'")
        prompt = ROUGH_OUTLINE_GENERATOR_PROMPT_V2.format(
            user_input=user_input,
            title=intent.title,
            genre=intent.genre,
            description=intent.description,
            volume_count=self.gen_config.volume_count,
        )
        response = await self.llm.ask(prompt)
        return extract_content(response, OutlineType.ROUGH)

    async def generate_detailed_outline_summary(
        self,
        volume_number: int,
        rough_outline: str,
        detailed_outline: str,
    ) -> str:
        """Generate summary of detailed outline."""
        prompt = DETAILED_OUTLINE_SUMMARY_PROMPT.format(
            volume_number=volume_number,
            rough_outline=rough_outline,
            detailed_outline=detailed_outline,
        )
        return await self.llm.ask(prompt)

    @staticmethod
    def _split_into_chapters(detailed_outline: str) -> List[str]:
        """
        Split detailed outline into chapter outlines based on '### 第x章' markers.

        Args:
            detailed_outline: String containing the full outline with chapter markers

        Returns:
            List of strings, each containing a chapter's content including its marker
        """
        # 使用正则表达式匹配章节标记
        pattern = r"(?=#\s第[0-9]+章(?:\s|$))"

        # 分割文本
        chapters = re.split(pattern, detailed_outline)

        # 过滤空章节并验证章节标记
        return [
            chapter.strip()
            for chapter in chapters
            if chapter.strip() and re.match(r"^#\s第[0-9]+章(?:\s|$)", chapter.strip())
        ]

    async def generate_detailed_outline(
        self, designated_volume, prev_volume_summary
    ) -> DetailedOutline:
        """Generate detailed outline for a single chapter."""

        chapter_range = ...
        prompt = DETAILED_OUTLINE_GENERATOR_PROMPT_V2.format(
            designated_volume=designated_volume,
            chapter_range=chapter_range,
            description=self.current_intent.description,
            section_word_count=self.gen_config.section_word_count,
            prev_volume_summary=prev_volume_summary,
            chapter_outline=self.current_chapter_outline,
        )
        response = await self.llm.ask(prompt)
        return extract_content(response, OutlineType.DETAILED)

    @save_checkpoint("chapter")
    async def generate_chapter(
        self,
        designated_chapter: int,
        detailed_outline: str,
        rough_outline: str,
        chapters: Optional[List[str]] = None,
    ) -> str:
        """Generate a single chapter."""
        chapters = chapters or []

        prompt = CONTENT_GENERATOR_PROMPT.format(
            designated_chapter=designated_chapter,
            rough_outline=rough_outline,
            detailed_outline=detailed_outline,
            section_word_count=self.gen_config.section_word_count,
            chapters="\n\n".join(chapters),
        )
        return await self.llm.ask(prompt)

    @save_checkpoint("chapter")
    async def _optimize_chapter(self, chapter: str) -> str:
        """Optimize a single chapter."""
        prompt = CONTENT_OPTIMIZER_PROMPT.format(
            chapter_content=chapter,
            section_word_count=self.gen_config.section_word_count,
        )
        return await self.llm.ask(prompt)

    async def generate_chapter_outline(
        self,
        volume_number: int,
        description: str,
        rough_outline: RoughOutline,
        prev_volume_summary: Optional[str] = None,
    ) -> ChapterOutline:
        """Generate chapter outline for a volume."""
        chapter_count_per_volume = self.gen_config.chapter_count_per_volume
        start_chapter = (
            volume_number * chapter_count_per_volume - chapter_count_per_volume + 1
        )

        prompt = CHAPTER_OUTLINE_GENERATOR_PROMPT.format(
            designated_volume=volume_number,
            description=description,
            rough_outline=str(rough_outline),
            section_word_count=self.gen_config.section_word_count,
            prev_volume_summary=prev_volume_summary or "无",
            chapter_range=f"第{volume_number}卷：第{start_chapter}-{start_chapter + chapter_count_per_volume - 1}章",
        )
        response = await self.llm.ask(prompt)
        return extract_content(response, OutlineType.CHAPTER)

    @save_checkpoint("volume")
    @save_checkpoint("volume")
    async def generate_volume(
        self,
        volume_number: int,
        intent: NovelIntent,
        rough_outline: RoughOutline,
        prev_volume_summary: Optional[str] = None,
        need_optim: bool = False,
    ) -> NovelVolume:
        """Generate a complete volume of the novel."""
        logger.info(f"Starting generation of volume {volume_number}")

        chapters: List[str] = []

        # Initialize volume with empty data first
        volume = NovelVolume(
            volume_number=volume_number,
            detailed_outline="",
            outline_summary="",
            chapters=chapters,
        )

        # Generate chapters one by one
        for chapter_num in range(self.gen_config.chapter_count_per_volume):
            await self._generate_single_chapter(
                volume=volume,
                volume_number=volume_number,
                chapter_num=chapter_num,
                intent=intent,
                rough_outline=rough_outline,
                prev_volume_summary=prev_volume_summary,
                need_optim=need_optim,
                chapters=chapters,
            )
            logger.info(
                f"Successfully generated chapter {chapter_num + 1} in volume {volume_number}"
            )

        return volume

    async def _generate_single_chapter(
        self,
        volume: NovelVolume,
        volume_number: int,
        chapter_num: int,
        intent: NovelIntent,
        rough_outline: RoughOutline,
        prev_volume_summary: Optional[str],
        need_optim: bool,
        chapters: List[str],
    ) -> None:
        """Generate a single chapter including its outlines and content."""
        # Generate chapter outline for current chapter
        self.current_chapter_outline = await self.generate_chapter_outline(
            volume_number=volume_number,
            description=intent.description,
            rough_outline=rough_outline,
            prev_volume_summary=prev_volume_summary,
        )

        # Generate detailed outline for current chapter
        self.current_detailed_outline = await self.generate_detailed_outline()

        # Update volume with latest outline
        volume.detailed_outline = str(self.current_detailed_outline)
        volume.outline_summary = str(self.current_chapter_outline)

        # Generate current chapter
        chapter = await self._generate_volume_chapter(
            volume_number=volume_number, need_optim=need_optim
        )

        chapters.append(chapter)
        volume.chapters = chapters

    async def generate_volumes(
        self,
        volume_count: int,
        intent: NovelIntent,
        rough_outline: RoughOutline,
        prev_volume_summary: Optional[str] = None,
    ) -> List[NovelVolume]:
        """Generate volumes for the novel."""
        volumes: List[NovelVolume] = []
        current_summary = prev_volume_summary

        for i in range(volume_count):
            volume = await self.generate_volume(
                volume_number=i + 1,
                intent=intent,
                rough_outline=rough_outline,
                prev_volume_summary=current_summary,
            )
            volumes.append(volume)
            current_summary = volume.outline_summary

        return volumes

    @save_checkpoint("novel")
    async def generate_novel(
        self,
        user_input: str,
        genre: Optional[str] = None,
        resume_novel_id: Optional[str] = None,
    ) -> Novel:
        """Generate complete novel from user input."""
        # Resume from checkpoint if provided
        if resume_novel_id:
            self.current_novel_id = resume_novel_id
            checkpoint = self.novel_saver.load_checkpoint(resume_novel_id)
            if checkpoint:
                logger.info(f"Resuming from checkpoint for novel {resume_novel_id}")
                return await self._resume_generation(checkpoint)

        logger.info("Starting new novel generation")
        self.current_intent = await self.analyze_intent(user_input)
        if genre:
            self.current_intent.genre = genre

        self.current_novel_id = self._generate_novel_id(self.current_intent.description)
        self.current_rough_outline = await self.generate_rough_outline(
            user_input, self.current_intent
        )

        self.current_volumes = await self.generate_volumes(
            self.gen_config.volume_count,
            self.current_intent,
            self.current_rough_outline,
        )

        novel = Novel(
            intent=self.current_intent,
            rough_outline=str(self.current_rough_outline),
            volumes=self.current_volumes,
            cost_info=self.cost_tracker.get(),
        )

        return novel

    @save_checkpoint("novel")
    async def _resume_generation(self, resume_novel_id: str) -> Novel:
        """从检查点恢复小说生成"""
        checkpoint = self.novel_saver.load_checkpoint(resume_novel_id)
        if not checkpoint:
            raise ValueError(f"No checkpoint found for novel {resume_novel_id}")

        # 恢复各种大纲对象
        self.current_rough_outline = load_outline_from_dict(
            checkpoint.get("rough_outline_obj"), OutlineType.ROUGH
        )
        self.current_chapter_outline = load_outline_from_dict(
            checkpoint.get("chapter_outline_obj"), OutlineType.CHAPTER
        )
        self.current_detailed_outline = load_outline_from_dict(
            checkpoint.get("detailed_outline_obj"), OutlineType.DETAILED
        )

        # 恢复基本数据
        intent = NovelIntent(**checkpoint["intent"])
        volumes = [NovelVolume(**v) for v in checkpoint["volumes"]]

        # 从上次中断的地方继续
        current_volume = len(volumes)
        prev_volume_summary = volumes[-1].outline_summary if volumes else None

        remaining_volumes = await self.generate_volumes(
            self.gen_config.volume_count - current_volume,
            intent,
            self.current_rough_outline,
            prev_volume_summary,
        )

        volumes.extend(remaining_volumes)

        return Novel(
            intent=intent,
            rough_outline=str(self.current_rough_outline),
            volumes=volumes,
            cost_info=self.cost_tracker.get(),
        )
