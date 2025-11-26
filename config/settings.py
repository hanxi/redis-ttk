"""
配置管理模块
用于保存和加载应用程序设置
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from redis_client import RedisConfig


@dataclass
class AppSettings:
    """应用程序设置"""

    # 窗口设置
    window_width: int = 1200
    window_height: int = 800
    window_x: int | None = None
    window_y: int | None = None
    window_maximized: bool = False

    # 界面设置
    theme: str = "superhero"
    font_family: str = "Consolas"
    font_size: int = 10

    # 编辑器设置
    auto_save: bool = False
    auto_refresh: bool = True
    show_line_numbers: bool = True
    word_wrap: bool = True

    # 连接设置
    auto_connect_last: bool = False
    connection_timeout: float = 5.0
    max_keys_display: int = 1000

    # 其他设置
    confirm_delete: bool = True
    show_tooltips: bool = True
    debug_mode: bool = False
    readonly_mode: bool = False


class Settings:
    """设置管理器"""

    def __init__(self):
        """初始化设置管理器"""
        # 设置文件路径
        self.config_dir = Path.home() / ".redis-ttk"
        self.config_file = self.config_dir / "settings.json"
        self.connections_file = self.config_dir / "connections.json"

        # 确保配置目录存在
        self.config_dir.mkdir(exist_ok=True)

        # 防抖保存相关
        self._save_timer = None
        self._save_delay = 500  # 500ms延迟保存

        # 加载设置
        self.app_settings = self.load_app_settings()
        self.connections = self.load_connections()

    def load_app_settings(self) -> AppSettings:
        """加载应用程序设置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, encoding="utf-8") as f:
                    data = json.load(f)
                    return AppSettings(**data)
        except Exception as e:
            print(f"加载设置失败: {e}")

        # 返回默认设置
        return AppSettings()

    def save_app_settings(self, immediate=False):
        """保存应用程序设置"""
        if immediate:
            self._do_save_app_settings()
        else:
            # 使用防抖机制延迟保存
            self._schedule_save()

    def _schedule_save(self):
        """调度延迟保存"""
        if self._save_timer:
            self._save_timer.cancel()

        import threading

        self._save_timer = threading.Timer(
            self._save_delay / 1000.0, self._do_save_app_settings
        )
        self._save_timer.start()

    def _do_save_app_settings(self):
        """实际执行保存操作"""
        try:
            # 创建临时文件，原子性写入
            temp_file = self.config_file.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(asdict(self.app_settings), f, indent=2, ensure_ascii=False)

            # 原子性替换
            temp_file.replace(self.config_file)

        except Exception as e:
            print(f"保存设置失败: {e}")
            # 清理临时文件
            if temp_file.exists():
                temp_file.unlink()

    def load_connections(self) -> dict[str, dict[str, Any]]:
        """加载连接配置"""
        try:
            if self.connections_file.exists():
                with open(self.connections_file, encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载连接配置失败: {e}")

        return {}

    def save_connections(self):
        """保存连接配置"""
        try:
            with open(self.connections_file, "w", encoding="utf-8") as f:
                json.dump(self.connections, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存连接配置失败: {e}")

    def save_connection(self, name: str, config: RedisConfig):
        """保存连接配置"""
        import time

        connection_data = {
            "host": config.host,
            "port": config.port,
            "password": config.password,
            "db": config.db,
            "decode_responses": config.decode_responses,
            "socket_timeout": config.socket_timeout,
            "socket_connect_timeout": config.socket_connect_timeout,
            "retry_on_timeout": config.retry_on_timeout,
            "created_time": time.time(),
            "last_used": time.time(),
        }

        # 如果连接已存在，更新最后使用时间
        if name in self.connections:
            connection_data["created_time"] = self.connections[name].get(
                "created_time", time.time()
            )

        self.connections[name] = connection_data

        # 限制最多保存10个连接（不包括特殊的__last__连接）
        regular_connections = {
            k: v for k, v in self.connections.items() if k != "__last__"
        }
        if len(regular_connections) > 10:
            # 按最后使用时间排序，删除最旧的连接
            sorted_connections = sorted(
                regular_connections.items(),
                key=lambda x: x[1].get("last_used", 0),
                reverse=True,
            )
            # 保留最新的10个
            self.connections = dict(sorted_connections[:10])
            # 重新添加__last__连接
            if "__last__" in self.connections:
                self.connections["__last__"] = self.connections["__last__"]

        self.save_connections()

    def get_connection(self, name: str) -> RedisConfig | None:
        """获取连接配置"""
        if name in self.connections:
            data = self.connections[name]
            # 过滤掉 RedisConfig 不需要的字段
            config_data = {
                key: value
                for key, value in data.items()
                if key
                in [
                    "host",
                    "port",
                    "password",
                    "db",
                    "decode_responses",
                    "socket_timeout",
                    "socket_connect_timeout",
                    "retry_on_timeout",
                ]
            }
            return RedisConfig(**config_data)
        return None

    def delete_connection(self, name: str):
        """删除连接配置"""
        if name in self.connections:
            del self.connections[name]
            self.save_connections()

    def get_connection_names(self) -> list:
        """获取所有连接名称（排除特殊连接）"""
        return [name for name in self.connections.keys() if name != "__last__"]

    def get_recent_connections(self) -> list:
        """获取最近使用的连接列表"""
        regular_connections = {
            k: v for k, v in self.connections.items() if k != "__last__"
        }
        # 按最后使用时间排序
        sorted_connections = sorted(
            regular_connections.items(),
            key=lambda x: x[1].get("last_used", 0),
            reverse=True,
        )
        return [{"name": name, "config": data} for name, data in sorted_connections]

    def save_last_connection(self, config: RedisConfig):
        """保存最后使用的连接"""
        self.save_connection("__last__", config)

    def update_connection_last_used(self, name: str):
        """更新连接的最后使用时间"""
        import time

        if name in self.connections:
            self.connections[name]["last_used"] = time.time()
            self.save_connections()

    def get_last_connection(self) -> RedisConfig | None:
        """获取最后使用的连接"""
        return self.get_connection("__last__")

    def save_window_geometry(
        self, width: int, height: int, x: int, y: int, maximized: bool = False
    ):
        """保存窗口几何信息"""
        self.app_settings.window_width = width
        self.app_settings.window_height = height
        self.app_settings.window_x = x
        self.app_settings.window_y = y
        self.app_settings.window_maximized = maximized
        self.save_app_settings()

    def get_window_geometry(self) -> tuple:
        """获取窗口几何信息"""
        return (
            self.app_settings.window_width,
            self.app_settings.window_height,
            self.app_settings.window_x,
            self.app_settings.window_y,
            self.app_settings.window_maximized,
        )

    def set_theme(self, theme: str):
        """设置主题"""
        self.app_settings.theme = theme
        self.save_app_settings()

    def get_theme(self) -> str:
        """获取主题"""
        return self.app_settings.theme

    def set_font(self, family: str, size: int):
        """设置字体"""
        self.app_settings.font_family = family
        self.app_settings.font_size = size
        self.save_app_settings()

    def get_font(self) -> tuple:
        """获取字体"""
        return self.app_settings.font_family, self.app_settings.font_size

    def set_editor_options(
        self,
        auto_save: bool = None,
        auto_refresh: bool = None,
        show_line_numbers: bool = None,
        word_wrap: bool = None,
    ):
        """设置编辑器选项"""
        if auto_save is not None:
            self.app_settings.auto_save = auto_save
        if auto_refresh is not None:
            self.app_settings.auto_refresh = auto_refresh
        if show_line_numbers is not None:
            self.app_settings.show_line_numbers = show_line_numbers
        if word_wrap is not None:
            self.app_settings.word_wrap = word_wrap
        self.save_app_settings()

    def get_editor_options(self) -> dict[str, bool]:
        """获取编辑器选项"""
        return {
            "auto_save": self.app_settings.auto_save,
            "auto_refresh": self.app_settings.auto_refresh,
            "show_line_numbers": self.app_settings.show_line_numbers,
            "word_wrap": self.app_settings.word_wrap,
        }

    def set_connection_options(
        self,
        auto_connect_last: bool = None,
        connection_timeout: float = None,
        max_keys_display: int = None,
    ):
        """设置连接选项"""
        if auto_connect_last is not None:
            self.app_settings.auto_connect_last = auto_connect_last
        if connection_timeout is not None:
            self.app_settings.connection_timeout = connection_timeout
        if max_keys_display is not None:
            self.app_settings.max_keys_display = max_keys_display
        self.save_app_settings()

    def get_connection_options(self) -> dict[str, Any]:
        """获取连接选项"""
        return {
            "auto_connect_last": self.app_settings.auto_connect_last,
            "connection_timeout": self.app_settings.connection_timeout,
            "max_keys_display": self.app_settings.max_keys_display,
        }

    def set_other_options(
        self,
        confirm_delete: bool = None,
        show_tooltips: bool = None,
        debug_mode: bool = None,
        readonly_mode: bool = None,
    ):
        """设置其他选项"""
        if confirm_delete is not None:
            self.app_settings.confirm_delete = confirm_delete
        if show_tooltips is not None:
            self.app_settings.show_tooltips = show_tooltips
        if debug_mode is not None:
            self.app_settings.debug_mode = debug_mode
        if readonly_mode is not None:
            self.app_settings.readonly_mode = readonly_mode
        self.save_app_settings()

    def get_other_options(self) -> dict[str, bool]:
        """获取其他选项"""
        return {
            "confirm_delete": self.app_settings.confirm_delete,
            "show_tooltips": self.app_settings.show_tooltips,
            "debug_mode": self.app_settings.debug_mode,
            "readonly_mode": self.app_settings.readonly_mode,
        }

    def is_readonly_mode(self) -> bool:
        """检查是否为只读模式"""
        return self.app_settings.readonly_mode

    def reset_to_defaults(self):
        """重置为默认设置"""
        self.app_settings = AppSettings()
        self.save_app_settings()

    def export_settings(self, file_path: str):
        """导出设置到文件"""
        try:
            export_data = {
                "app_settings": asdict(self.app_settings),
                "connections": self.connections,
            }

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"导出设置失败: {e}")
            return False

    def import_settings(self, file_path: str):
        """从文件导入设置"""
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            # 导入应用设置
            if "app_settings" in data:
                self.app_settings = AppSettings(**data["app_settings"])
                self.save_app_settings()

            # 导入连接配置
            if "connections" in data:
                self.connections.update(data["connections"])
                self.save_connections()

            return True
        except Exception as e:
            print(f"导入设置失败: {e}")
            return False

    def save(self):
        """保存所有设置"""
        self.save_app_settings()
        self.save_connections()
