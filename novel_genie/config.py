import os
import threading

import yaml
from pydantic import BaseModel, Field


def get_project_root() -> str:
    """获取项目根目录"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


NovelGenie = get_project_root()


class LLMSettings(BaseModel):
    """LLM相关配置"""

    model: str = Field(..., description="模型名称")
    base_url: str = Field(..., description="API基础URL")
    api_key: str = Field(..., description="API密钥")
    max_tokens: int = Field(1000, description="每个请求的最大token数")
    temperature: float = Field(0.7, description="采样温度")


class NovelSettings(BaseModel):
    """小说生成相关配置"""

    volume_count: int = Field(1, description="卷数")
    chapter_count_per_volume: int = Field(3, description="每卷章节数")
    section_word_count: int = Field(1000, description="每节字数")
    workspace: str = Field("workspace", description="工作目录")


class AppConfig(BaseModel):
    """应用总配置"""

    llm: LLMSettings
    novel: NovelSettings


class Config:
    """单例配置类"""

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self._config = None
                    self._load_initial_config()
                    self._initialized = True

    @staticmethod
    def _get_config_path() -> str:
        """获取配置文件路径"""
        root = NovelGenie
        config_path = os.path.join(root, "config", "config.yaml")
        if not os.path.exists(config_path):
            config_path = os.path.join(root, "config", "config.example.yaml")
        if not os.path.exists(config_path):
            raise FileNotFoundError("未找到配置文件 config.yaml 或 config.example.yaml")
        return config_path

    def _load_config(self) -> dict:
        """加载配置文件"""
        config_path = self._get_config_path()
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _load_initial_config(self):
        """初始化配置"""
        raw_config = self._load_config()

        config_dict = {
            "llm": {
                "model": raw_config.get("llm", {}).get("model"),
                "base_url": raw_config.get("llm", {}).get("base_url"),
                "api_key": raw_config.get("llm", {}).get("api_key"),
                "max_tokens": raw_config.get("llm", {}).get("max_tokens", 1000),
                "temperature": raw_config.get("llm", {}).get("temperature", 0.7),
            },
            "novel": {
                "volume_count": raw_config.get("novel", {}).get("volume_count", 1),
                "section_word_count": raw_config.get("novel", {}).get(
                    "section_word_count", 1000
                ),
                "chapter_count_per_volume": raw_config.get("novel", {}).get(
                    "chapter_count_per_volume", 3
                ),
                "workspace": raw_config.get("novel", {}).get("workspace", "workspace"),
            },
        }

        self._config = AppConfig(**config_dict)

    @property
    def llm(self) -> LLMSettings:
        """获取LLM配置"""
        return self._config.llm

    @property
    def novel(self) -> NovelSettings:
        """获取小说生成配置"""
        return self._config.novel


# 实例化配置对象
config = Config()


class NovelGenerationConfig(BaseModel):
    """novel generation configuration."""

    section_word_count: int = Field(
        default_factory=lambda: config.novel.section_word_count
    )
    volume_count: int = Field(default_factory=lambda: config.novel.volume_count)
    chapter_count_per_volume: int = Field(
        default_factory=lambda: config.novel.chapter_count_per_volume
    )
    workspace: str = Field(default_factory=lambda: config.novel.workspace)


# 示例使用
if __name__ == "__main__":
    # LLM配置访问
    print(f"Model: {config.llm.model}")
    print(f"API Key: {config.llm.api_key}")
    print(f"Max Tokens: {config.llm.max_tokens}")

    # 小说配置访问
    print(f"Number of Volumes: {config.novel.volume_count}")
    print(f"Section Word Count: {config.novel.section_word_count}")
