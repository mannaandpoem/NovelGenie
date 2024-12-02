from typing import Optional


class NovelGenerationBaseError(Exception):
    """Base exception for all novel generation related errors."""


class ChapterGenerationError(NovelGenerationBaseError):
    """Exception raised when chapter generation fails."""

    def __init__(self, chapter_info: str):
        self.chapter_info = chapter_info
        super().__init__(f"Failed to generate {chapter_info}")


class OutlineGenerationError(NovelGenerationBaseError):
    """Exception raised when outline generation fails."""

    def __init__(self, outline_type: str, volume_number: Optional[int] = None):
        self.outline_type = outline_type
        self.volume_number = volume_number
        message = f"Failed to generate {outline_type} outline"
        if volume_number:
            message += f" for volume {volume_number}"
        super().__init__(message)


class NovelSaveError(NovelGenerationBaseError):
    """Exception raised when saving novel data fails."""

    def __init__(self, novel_id: str, operation: str):
        self.novel_id = novel_id
        self.operation = operation
        super().__init__(f"Failed to {operation} novel {novel_id}")
