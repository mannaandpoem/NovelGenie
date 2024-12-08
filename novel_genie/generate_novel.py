import re
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from novel_genie.config import NovelGenerationConfig
from novel_genie.cost import Cost
from novel_genie.llm import LLM
from novel_genie.logger import logger
from novel_genie.prompts.chapter_outline_generator_prompt import (
    CHAPTER_OUTLINE_GENERATOR_PROMPT,
)
from novel_genie.prompts.content_generator_prompt import CONTENT_GENERATOR_PROMPT_V2
from novel_genie.prompts.content_optimizer_prompt import CONTENT_OPTIMIZER_PROMPT
from novel_genie.prompts.detail_outline_generator_prompt import (
    DETAILED_OUTLINE_GENERATOR_PROMPT_V2,
    DETAILED_OUTLINE_SUMMARY_PROMPT,
)
from novel_genie.prompts.intent_analyzer_prompt import INTENT_ANALYZER_PROMPT
from novel_genie.prompts.rough_outline_prompt import ROUGH_OUTLINE_GENERATOR_PROMPT_V2
from novel_genie.schema import (
    Chapter,
    ChapterOutline,
    CheckpointType,
    DetailedOutline,
    Novel,
    NovelIntent,
    NovelSaver,
    NovelVolume,
    OutlineType,
    RoughOutline,
)
from novel_genie.utils import (
    T,
    extract_commands_from_response,
    extract_outline,
    parse_intent,
    process_edit_commands,
    save_checkpoint,
)


class NovelGenie(BaseModel):
    """Web novel generation engine."""

    llm: LLM = Field(default_factory=LLM)
    cost_tracker: Cost = Field(default_factory=Cost)
    novel_saver: NovelSaver = Field(default_factory=NovelSaver)
    generation_config: NovelGenerationConfig = Field(
        default_factory=NovelGenerationConfig
    )

    user_input: Optional[str] = Field(None, exclude=True)
    novel_id: Optional[str] = Field(None, exclude=True)
    intent: Optional[NovelIntent] = Field(None, exclude=True)

    volumes: List[NovelVolume] = Field(default_factory=list, exclude=True)
    rough_outline: Optional[RoughOutline] = Field(None, exclude=True)
    chapter_outline: Optional[ChapterOutline] = Field(None, exclude=True)
    detailed_outline: Optional[DetailedOutline] = Field(None, exclude=True)

    current_volume_num: Optional[int] = Field(None, exclude=True)
    current_chapter_num: Optional[int] = Field(None, exclude=True)

    class Config:
        arbitrary_types_allowed = True

    @staticmethod
    def generate_novel_id(title: str) -> str:
        """Generate unique novel ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{title}_{timestamp}"

    async def analyze_intent(self) -> NovelIntent:
        """Analyze user input to extract story details."""
        logger.info("Analyzing user input to extract story details")
        prompt = INTENT_ANALYZER_PROMPT.format(user_input=self.user_input)
        response = await self.llm.ask(prompt)
        title, description, genre, work_length = parse_intent(response)
        return NovelIntent(
            title=title,
            description=description,
            genre=genre,
            work_length=work_length,
        )

    async def generate_rough_outline(self) -> RoughOutline:
        """Generate rough outline based on story intent."""
        logger.info(f"Generating rough outline for novel '{self.intent.title}'")
        prompt = ROUGH_OUTLINE_GENERATOR_PROMPT_V2.format(
            user_input=self.user_input,
            work_length=self.intent.work_length,
            title=self.intent.title,
            genre=self.intent.genre,
            description=self.intent.description,
            volume_count=self.generation_config.volume_count,
            chapter_count_per_volume=self.generation_config.chapter_count_per_volume,
        )
        response = await self.llm.ask(prompt)
        return extract_outline(response, OutlineType.ROUGH)

    async def generate_detailed_outline(
        self, prev_volume_summary: Optional[str] = None
    ) -> DetailedOutline:
        """Generate detailed outline for a single chapter."""
        # Apply sliding window to get latest n detailed outlines from previous detailed outlines
        existing_detailed_outlines = self._get_latest_elements(
            attribute_name="detailed_outlines"
        )

        # FIXME: rough_outline should be fix
        prompt = DETAILED_OUTLINE_GENERATOR_PROMPT_V2.format(
            work_length=self.intent.work_length,
            chapter_count_per_volume=self.generation_config.chapter_count_per_volume,
            designated_volume=self.current_volume_num,
            designated_chapter=self.current_chapter_num,
            description=self.intent.description,
            rough_outline=str(self.rough_outline),
            worldview_system=self.rough_outline.worldview_system,
            character_system=self.rough_outline.character_system,
            volume_design=self.rough_outline.volume_design[self.current_volume_num - 1],
            section_word_count=self.generation_config.section_word_count,
            prev_volume_summary=prev_volume_summary,
            chapter_outline=self.chapter_outline,
            existing_detailed_outlines="\n\n".join(
                str(outline) for outline in existing_detailed_outlines
            ),
        )
        response = await self.llm.ask(prompt)
        return extract_outline(response, OutlineType.DETAILED)

    @save_checkpoint(CheckpointType.CHAPTER)
    async def generate_chapter(self) -> Chapter:
        """Generate a single chapter."""
        existing_chapters = self._get_latest_elements(attribute_name="chapters")
        prompt = CONTENT_GENERATOR_PROMPT_V2.format(
            description=self.intent.description,
            work_length=self.intent.work_length,
            chapter_count_per_volume=self.generation_config.chapter_count_per_volume,
            designated_volume=self.current_volume_num,
            designated_chapter=self.current_chapter_num,
            worldview_system=self.rough_outline.worldview_system,
            character_system=self.rough_outline.character_system,
            volume_design=self.rough_outline.volume_design[self.current_volume_num - 1],
            chapter_outline=self.chapter_outline,
            detailed_outline=self.detailed_outline,
            section_word_count=self.generation_config.section_word_count,
            existing_chapters="\n\n".join(
                str(outline) for outline in existing_chapters
            ),
        )
        response = await self.llm.ask(prompt)
        # Extract chapter title and content
        title = re.search(r"## 第\s*[0-9零一二三四五六七八九]+\s*章\s+.+", response).group()
        content = response.split(title, 1)[1].strip()
        return Chapter(title=title, content=content)

    @save_checkpoint(CheckpointType.CHAPTER)
    async def optimize_chapter_content(self, chapter: Chapter) -> Chapter:
        """Optimize a single chapter."""
        prompt = CONTENT_OPTIMIZER_PROMPT.format(
            original_chapter_content=chapter.content
        )
        rsp = await self.llm.ask(prompt)
        commands = extract_commands_from_response(rsp)

        # 应用编辑命令
        modified_content = process_edit_commands(chapter.content, commands)
        chapter.content = modified_content
        return chapter

    async def generate_chapter_outline(
        self, prev_volume_summary: Optional[str] = None
    ) -> ChapterOutline:
        """Generate chapter outline for a volume."""
        existing_chapter_outlines = self._get_latest_elements(
            attribute_name="chapter_outlines"
        )
        prompt = CHAPTER_OUTLINE_GENERATOR_PROMPT.format(
            user_input=self.user_input,
            work_length=self.intent.work_length,
            chapter_count_per_volume=self.generation_config.chapter_count_per_volume,
            designated_volume=self.current_volume_num,
            designated_chapter=self.current_chapter_num,
            description=self.intent.description,
            worldview_system=self.rough_outline.worldview_system,
            character_system=self.rough_outline.character_system,
            volume_design=self.rough_outline.volume_design[self.current_volume_num - 1],
            section_word_count=self.generation_config.section_word_count,
            existing_chapter_outlines="\n\n".join(
                str(outline) for outline in existing_chapter_outlines
            ),
            prev_volume_summary=prev_volume_summary,
        )
        response = await self.llm.ask(prompt)
        return extract_outline(response, OutlineType.CHAPTER)

    def _get_latest_elements(self, attribute_name: str) -> List[T]:
        """从当前卷或上一卷中获取指定属性的最新元素。"""
        # 尝试从当前卷获取指定属性
        current_volume_elements = (
            getattr(self.volumes[self.current_volume_num - 1], attribute_name, [])
            if self.volumes and self.current_volume_num > 0
            else []
        )

        # 如果当前卷的元素为空，尝试从上一卷获取
        if not current_volume_elements and self.current_volume_num > 1:
            previous_volume_elements = getattr(
                self.volumes[self.current_volume_num - 2], attribute_name, []
            )
            # 从上一卷获取最新的几条元素
            current_volume_elements = previous_volume_elements[
                -self.generation_config.sliding_window_size :
            ]

        logger.info(
            f"Found {len(current_volume_elements)} existing elements for {attribute_name}"
        )

        # 返回经过滑动窗口处理后的元素
        return current_volume_elements[-self.generation_config.sliding_window_size :]

    @save_checkpoint(CheckpointType.VOLUME)
    async def generate_volume(
        self,
        volume: NovelVolume,
        prev_volume_summary: Optional[str] = None,
    ) -> NovelVolume:
        """Generate a complete volume of the novel."""
        # Generate chapters one by one
        chapter_count_per_volume = self.generation_config.chapter_count_per_volume
        start_chapter = chapter_count_per_volume * (self.current_volume_num - 1) + 1
        self.current_chapter_num = (
            self.current_chapter_num + 1
            if self.current_chapter_num is not None
            else None
        )
        start_chapter = self.current_chapter_num or start_chapter
        end_chapter = self.current_volume_num * chapter_count_per_volume
        for chapter_num in range(start_chapter, end_chapter + 1):
            self.current_chapter_num = chapter_num
            logger.info(
                f"Generating chapter {self.current_chapter_num} for volume {self.current_volume_num}"
            )
            await self._generate_single_chapter(
                volume=volume, prev_volume_summary=prev_volume_summary
            )
            logger.info(
                f"Successfully generated chapter {self.current_chapter_num} in volume {self.current_volume_num}"
            )

        return volume

    async def _generate_single_chapter(
        self,
        volume: NovelVolume,
        prev_volume_summary: Optional[str],
    ) -> None:
        """Generate a single chapter including its outlines and content."""
        # Generate chapter outline for current chapter
        self.chapter_outline = await self.generate_chapter_outline(
            prev_volume_summary=prev_volume_summary
        )
        volume.chapter_outlines.append(self.chapter_outline)

        # Generate detailed outline for current chapter
        self.detailed_outline = await self.generate_detailed_outline(
            prev_volume_summary=prev_volume_summary
        )
        # volume.detailed_outlines = self.detailed_outline
        volume.detailed_outlines.append(self.detailed_outline)

        # Generate current chapter
        chapter = await self.generate_chapter()
        if self.generation_config.need_optimize:
            logger.info(f"Optimizing content for chapter {chapter.title}")
            chapter = await self.optimize_chapter_content(chapter)

        volume.chapters.append(chapter)

    async def generate_volumes(self):
        """Generate volumes for the novel."""
        start_volume = self.current_volume_num or 1
        for volume_num in range(start_volume, self.generation_config.volume_count + 1):
            self.current_volume_num = volume_num
            logger.info(f"Starting generation of volume {self.current_volume_num}")
            volume = NovelVolume(volume_num=self.current_volume_num)
            self.volumes.append(volume)
            await self.generate_volume(volume)

    @save_checkpoint(CheckpointType.NOVEL)
    async def generate_novel(
        self,
        user_input: str,
        intent: Optional[NovelIntent] = None,
        resume_novel_id: Optional[str] = None,
    ) -> Novel:
        """Generate complete novel from user input."""
        # Resume from checkpoint if provided
        if resume_novel_id:
            self.novel_id = resume_novel_id
            return await self._resume_generation()

        self.user_input = user_input
        logger.info("Starting new novel generation")

        self.intent = await self.analyze_intent() if not intent else intent

        self.novel_id = self.generate_novel_id(self.intent.title)
        logger.info(f"Generating novel ID for description: {self.intent.title}")

        self.rough_outline = await self.generate_rough_outline()

        await self.generate_volumes()

        novel = Novel(
            intent=self.intent,
            rough_outline=self.rough_outline,
            volumes=self.volumes,
            cost_info=self.cost_tracker.get(),
        )

        return novel

    async def _resume_generation(self) -> Novel:
        """Resume novel generation from checkpoint."""
        checkpoint_data = self.novel_saver.load_checkpoint(self.novel_id)
        if not checkpoint_data:
            raise ValueError(f"No checkpoint found for novel {self.novel_id}")

        logger.info(f"Resuming novel generation for novel ID {self.novel_id}")
        try:
            # Restore instance variables
            self.intent = (
                NovelIntent(**checkpoint_data["intent"])
                if checkpoint_data.get("intent")
                else None
            )
            self.rough_outline = (
                RoughOutline(**checkpoint_data["rough_outline"])
                if checkpoint_data.get("rough_outline")
                else None
            )
            self.current_volume_num = checkpoint_data.get("current_volume_num")
            self.current_chapter_num = checkpoint_data.get("current_chapter_num")

            # Reconstruct volumes with their outlines and chapters
            volumes = []
            for vol_data in checkpoint_data.get("volumes", []):
                chapter_outline_data = vol_data.get("chapter_outline")
                detailed_outline_data = vol_data.get("detailed_outline")

                volume = NovelVolume(
                    volume_num=vol_data["volume_num"],
                    chapter_outline=ChapterOutline(**chapter_outline_data)
                    if chapter_outline_data
                    else None,
                    detailed_outline=DetailedOutline(**detailed_outline_data)
                    if detailed_outline_data
                    else None,
                    chapters=[Chapter(**ch) for ch in vol_data.get("chapters", [])],
                )
                volumes.append(volume)

            await self.generate_volumes()

            # Create and return novel object
            novel = Novel(
                intent=self.intent,
                rough_outline=self.rough_outline,
                volumes=self.volumes,
                cost_info=checkpoint_data.get("cost_info", {}),
            )

            logger.info(f"Successfully resumed novel generation for {self.novel_id}")
            return novel

        except Exception as e:
            logger.error(f"Failed to resume novel generation: {str(e)}")
            raise RuntimeError(f"Resume generation failed: {str(e)}") from e

    async def generate_detailed_outline_summary(
        self,
        volume_num: int,
        rough_outline: str,
        detailed_outline: str,
    ) -> str:
        """Generate summary of detailed outline."""
        logger.info(f"Generating detailed outline summary for volume {volume_num}")
        prompt = DETAILED_OUTLINE_SUMMARY_PROMPT.format(
            volume_num=volume_num,
            rough_outline=rough_outline,
            detailed_outline=detailed_outline,
        )
        return await self.llm.ask(prompt)
