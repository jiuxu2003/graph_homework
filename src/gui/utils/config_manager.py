"""
用户配置目录管理

负责初始化和管理用户配置目录（~/.spectrum_allocation/）。
"""

import os
from pathlib import Path
import json


class UserConfigManager:
    """用户配置管理器"""

    # 配置目录路径
    CONFIG_DIR = Path.home() / ".spectrum_allocation"
    HISTORY_DB = CONFIG_DIR / "history.db"
    PREFERENCES_FILE = CONFIG_DIR / "preferences.json"
    LOG_FILE = CONFIG_DIR / "gui.log"

    # 默认偏好设置
    DEFAULT_PREFERENCES = {
        "window_width": 1200,
        "window_height": 800,
        "window_x": None,
        "window_y": None,
        "last_config_dir": None,
        "last_output_dir": None,
        "show_tooltips": True,
        "auto_save_history": True,
        "viz_dpi": 100,
        "viz_style": "default"
    }

    @classmethod
    def ensure_config_dir(cls) -> Path:
        """
        确保用户配置目录存在

        Returns:
            Path: 配置目录路径
        """
        cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        return cls.CONFIG_DIR

    @classmethod
    def load_preferences(cls) -> dict:
        """
        加载用户偏好设置

        Returns:
            dict: 偏好设置字典
        """
        cls.ensure_config_dir()

        if cls.PREFERENCES_FILE.exists():
            try:
                with open(cls.PREFERENCES_FILE, 'r', encoding='utf-8') as f:
                    return {**cls.DEFAULT_PREFERENCES, **json.load(f)}
            except Exception as e:
                print(f"警告: 加载偏好设置失败: {e}")
                return cls.DEFAULT_PREFERENCES.copy()
        else:
            # 首次运行，创建默认配置
            cls.save_preferences(cls.DEFAULT_PREFERENCES)
            return cls.DEFAULT_PREFERENCES.copy()

    @classmethod
    def save_preferences(cls, preferences: dict):
        """
        保存用户偏好设置

        Args:
            preferences: 偏好设置字典
        """
        cls.ensure_config_dir()

        try:
            with open(cls.PREFERENCES_FILE, 'w', encoding='utf-8') as f:
                json.dump(preferences, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"警告: 保存偏好设置失败: {e}")

    @classmethod
    def get_history_db_path(cls) -> Path:
        """
        获取历史记录数据库路径

        Returns:
            Path: 数据库文件路径
        """
        cls.ensure_config_dir()
        return cls.HISTORY_DB

    @classmethod
    def get_log_file_path(cls) -> Path:
        """
        获取日志文件路径

        Returns:
            Path: 日志文件路径
        """
        cls.ensure_config_dir()
        return cls.LOG_FILE


# 应用启动时自动初始化配置目录
UserConfigManager.ensure_config_dir()
