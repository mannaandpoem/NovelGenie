import os
import yaml
import threading


class Config:
    """单例模式的配置类"""
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with cls._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_is_initialized"):
            self._is_initialized = True
            self._config = self._load_config()

    def _get_project_root(self) -> str:
        """获取项目根目录"""
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _get_config_path(self) -> str:
        """获取配置文件路径"""
        root = self._get_project_root()
        config_path = os.path.join(root, "config", "config.yaml")
        if not os.path.exists(config_path):
            # 如果 config.yaml 不存在，尝试加载 config.example.yaml
            config_path = os.path.join(root, "config", "config.example.yaml")
        if not os.path.exists(config_path):
            raise FileNotFoundError("未找到配置文件 config.yaml 或 config.example.yaml")
        return config_path

    def _load_config(self) -> dict:
        """加载配置文件"""
        config_path = self._get_config_path()
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get(self, key, default=None):
        """获取配置中的值"""
        return self._config.get(key, default)

    def set(self, key, value):
        """动态设置配置的值"""
        self._config[key] = value


# 实例化配置对象
config = Config()
