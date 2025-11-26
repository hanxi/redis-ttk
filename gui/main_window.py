"""
主窗口界面
Redis TTK 客户端的主界面窗口
"""

import tkinter as tk
from typing import Any

import ttkbootstrap as ttk
from ttkbootstrap.constants import (
    BOTH,
    BOTTOM,
    DANGER,
    DISABLED,
    HORIZONTAL,
    INFO,
    LEFT,
    NORMAL,
    PRIMARY,
    READONLY,
    RIGHT,
    SECONDARY,
    SUCCESS,
    VERTICAL,
    WARNING,
    X,
    Y,
)

from config.settings import Settings
from gui.connection_dialog import ConnectionDialog
from gui.custom_dialogs import askstring, askyesno, showerror, showinfo, showwarning
from gui.key_browser import KeyBrowser
from gui.settings_dialog import SettingsDialog
from gui.value_editor import ValueEditor
from redis_client import RedisClient, RedisConfig


class MainWindow:
    """主窗口类"""

    def __init__(self, root: ttk.Window):
        """初始化主窗口"""
        self.root = root
        self.redis_client: RedisClient | None = None
        self.settings = Settings()

        # 设置窗口属性
        self.setup_window()

        # 创建界面
        self.create_widgets()

        # 绑定事件
        self.bind_events()

        # 加载设置
        self.load_settings()

    def setup_window(self):
        """设置窗口属性"""
        self.root.title("Redis TTK Client")

        # 设置窗口居中
        self.center_window()

        # 设置窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def center_window(self):
        """窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        """创建界面组件"""
        # 创建主菜单
        self.create_menu()

        # 创建工具栏
        self.create_toolbar()

        # 创建状态栏
        self.create_statusbar()

        # 创建主内容区域
        self.create_main_content()

    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 连接菜单
        connection_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="连接", menu=connection_menu)
        connection_menu.add_command(
            label="新建连接...", command=self.new_connection, accelerator="Ctrl+N"
        )
        connection_menu.add_command(
            label="断开连接", command=self.disconnect, accelerator="Ctrl+D"
        )
        connection_menu.add_separator()
        connection_menu.add_command(
            label="退出", command=self.on_closing, accelerator="Ctrl+Q"
        )

        # 数据库菜单
        database_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="数据库", menu=database_menu)
        database_menu.add_command(
            label="刷新", command=self.refresh_keys, accelerator="F5"
        )
        database_menu.add_command(label="清空数据库", command=self.flush_database)
        database_menu.add_separator()
        database_menu.add_command(label="服务器信息", command=self.show_server_info)

        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="设置...", command=self.show_settings)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)

    def create_toolbar(self):
        """创建工具栏"""
        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(fill=X, padx=5, pady=2)

        # 连接按钮
        self.connect_btn = ttk.Button(
            self.toolbar, text="连接", command=self.new_connection, bootstyle=SUCCESS
        )
        self.connect_btn.pack(side=LEFT, padx=2)

        # 断开连接按钮
        self.disconnect_btn = ttk.Button(
            self.toolbar,
            text="断开",
            command=self.disconnect,
            bootstyle=DANGER,
            state=DISABLED,
        )
        self.disconnect_btn.pack(side=LEFT, padx=2)

        # 分隔符
        ttk.Separator(self.toolbar, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=5)

        # 刷新按钮
        self.refresh_btn = ttk.Button(
            self.toolbar, text="刷新", command=self.refresh_keys, state=DISABLED
        )
        self.refresh_btn.pack(side=LEFT, padx=2)

        # 新增键按钮
        self.add_key_btn = ttk.Button(
            self.toolbar,
            text="新增键",
            command=self.add_new_key,
            bootstyle=PRIMARY,
            state=DISABLED,
        )
        self.add_key_btn.pack(side=LEFT, padx=2)

        # 数据库选择
        ttk.Label(self.toolbar, text="数据库:").pack(side=LEFT, padx=(10, 2))
        self.db_combo = ttk.Combobox(self.toolbar, width=5, state=DISABLED)
        self.db_combo.set("0")
        self.db_combo.pack(side=LEFT, padx=2)
        self.db_combo.bind("<<ComboboxSelected>>", self.on_database_changed)

    def create_statusbar(self):
        """创建状态栏"""
        self.statusbar = ttk.Frame(self.root)
        self.statusbar.pack(fill=X, side=BOTTOM)

        # 连接状态
        self.status_label = ttk.Label(
            self.statusbar, text="未连接", bootstyle=SECONDARY
        )
        self.status_label.pack(side=LEFT, padx=5)

        # 键数量
        self.key_count_label = ttk.Label(self.statusbar, text="", bootstyle=INFO)
        self.key_count_label.pack(side=RIGHT, padx=5)

        # 只读模式指示器
        self.readonly_label = ttk.Label(
            self.statusbar, text="只读模式", bootstyle=WARNING
        )
        # 初始时隐藏，根据设置显示

    def create_main_content(self):
        """创建主内容区域"""
        # 创建主面板
        self.main_paned = ttk.Panedwindow(self.root, orient=HORIZONTAL)
        self.main_paned.pack(fill=BOTH, expand=True, padx=5, pady=5)

        # 左侧键浏览器
        self.key_browser = KeyBrowser(self.main_paned, self.on_key_selected)
        self.key_browser.set_main_window(self)  # 设置主窗口引用
        self.main_paned.add(self.key_browser.frame, weight=1)

        # 右侧值编辑器
        self.value_editor = ValueEditor(self.main_paned, self.on_value_changed)
        self.value_editor.set_refresh_callback(self.on_key_selected)
        self.main_paned.add(self.value_editor.frame, weight=2)

    def bind_events(self):
        """绑定键盘事件"""
        self.root.bind("<Control-n>", lambda e: self.new_connection())
        self.root.bind("<Control-d>", lambda e: self.disconnect())
        self.root.bind("<Control-q>", lambda e: self.on_closing())
        self.root.bind("<F5>", lambda e: self.refresh_keys())

    def load_settings(self):
        """加载设置"""
        try:
            # 应用窗口几何设置（先设置窗口，再应用主题）
            width, height, x, y, maximized = self.settings.get_window_geometry()
            if x is not None and y is not None:
                self.root.geometry(f"{width}x{height}+{x}+{y}")
            else:
                self.root.geometry(f"{width}x{height}")
                self.center_window()

            if maximized:
                self.root.state("zoomed")

            # 延迟应用主题设置，确保所有组件都已初始化
            theme = self.settings.get_theme()
            if theme:
                self.root.after(100, lambda: self._apply_theme_safely_on_load(theme))

            # 应用只读模式设置
            self.update_readonly_mode()

            # 加载最后的连接配置
            last_config = self.settings.get_last_connection()
            connection_options = self.settings.get_connection_options()
            if last_config and connection_options.get("auto_connect_last", False):
                # 自动连接到上次的连接
                self.root.after(1000, lambda: self.connect_to_redis(last_config))

        except Exception as e:
            print(f"加载设置失败: {e}")

    def _apply_theme_safely_on_load(self, theme: str):
        """在加载时安全地应用主题"""
        try:
            self.root.style.theme_use(theme)
            self.root.update_idletasks()
        except Exception as e:
            print(f"加载时应用主题失败: {e}")

    def new_connection(self):
        """新建连接"""
        dialog = ConnectionDialog(self.root, self.settings)
        if dialog.result:
            config = dialog.result
            # 如果保存了连接配置，更新最后使用时间
            if dialog.connection_name:
                self.settings.update_connection_last_used(dialog.connection_name)
            self.connect_to_redis(config)

    def connect_to_redis(self, config: RedisConfig):
        """连接到 Redis"""
        try:
            # 创建 Redis 客户端
            self.redis_client = RedisClient(config)

            # 尝试连接
            if self.redis_client.connect():
                # 更新界面状态
                self.update_connection_status(True)

                # 保存连接配置
                self.settings.save_last_connection(config)

                # 加载数据库列表
                self.load_databases()

                # 刷新键列表
                self.refresh_keys()

                showinfo("成功", "连接 Redis 成功！")
            else:
                showerror("错误", "连接 Redis 失败！")

        except Exception as e:
            showerror("错误", f"连接失败: {e}")

    def disconnect(self):
        """断开连接"""
        if self.redis_client:
            self.redis_client.disconnect()
            self.redis_client = None

        # 更新界面状态
        self.update_connection_status(False)

        # 清空界面
        self.key_browser.clear()
        self.value_editor.clear()

    def update_connection_status(self, connected: bool):
        """更新连接状态"""
        if connected:
            self.status_label.config(text="已连接", bootstyle=SUCCESS)
            self.connect_btn.config(state=DISABLED)
            self.disconnect_btn.config(state=NORMAL)
            self.refresh_btn.config(state=NORMAL)
            self.add_key_btn.config(state=NORMAL)
            self.db_combo.config(state=READONLY)
        else:
            self.status_label.config(text="未连接", bootstyle=SECONDARY)
            self.connect_btn.config(state=NORMAL)
            self.disconnect_btn.config(state=DISABLED)
            self.refresh_btn.config(state=DISABLED)
            self.add_key_btn.config(state=DISABLED)
            self.db_combo.config(state=DISABLED)
            self.key_count_label.config(text="")

    def load_databases(self):
        """加载数据库列表"""
        if not self.redis_client:
            return

        try:
            databases = self.redis_client.get_databases()
            self.db_combo["values"] = [str(db) for db in databases]
            self.db_combo.set(str(self.redis_client.config.db))
        except Exception as e:
            showerror("错误", f"加载数据库列表失败: {e}")

    def on_database_changed(self, event=None):
        """数据库切换事件"""
        if not self.redis_client:
            return

        try:
            db_number = int(self.db_combo.get())
            if self.redis_client.select_database(db_number):
                self.refresh_keys()
            else:
                showerror("错误", "切换数据库失败")
        except ValueError:
            showerror("错误", "无效的数据库编号")
        except Exception as e:
            showerror("错误", f"切换数据库失败: {e}")

    def refresh_keys(self):
        """刷新键列表"""
        if not self.redis_client:
            return

        try:
            keys = self.redis_client.get_all_keys()
            self.key_browser.load_keys(keys)
            self.key_count_label.config(text=f"共 {len(keys)} 个键")
        except Exception as e:
            showerror("错误", f"刷新键列表失败: {e}")

    def on_key_selected(self, key: str):
        """键选择事件"""
        if not self.redis_client or not key:
            self.value_editor.clear()
            return

        try:
            # 获取键信息
            key_info = self.redis_client.get_key_info(key)

            # 获取键值
            value = self.redis_client.get_value(key)

            # 更新键浏览器中的键信息显示
            self.key_browser.update_key_info(
                key, key_info["type"], key_info["ttl"], key_info["size"]
            )

            # 显示在值编辑器中
            self.value_editor.load_key_value(key, key_info, value)

        except Exception as e:
            showerror("错误", f"加载键值失败: {e}")

    def on_value_changed(self, key: str, new_value: Any, key_type: str):
        """值变更事件"""
        if not self.redis_client:
            return

        # 检查只读模式
        if self.settings.is_readonly_mode():
            showwarning("只读模式", "当前处于只读模式，无法修改数据")
            return

        try:
            # 保存新值
            if self.redis_client.set_value(key, new_value, key_type):
                showinfo("成功", "保存成功！")
                # 刷新键列表（可能影响键的信息）
                self.refresh_keys()
            else:
                showerror("错误", "保存失败")

        except Exception as e:
            showerror("错误", f"保存失败: {e}")

    def add_new_key(self):
        """添加新键"""
        if not self.redis_client:
            return

        # 检查只读模式
        if self.settings.is_readonly_mode():
            showwarning("只读模式", "当前处于只读模式，无法添加新键")
            return

        # 显示新键对话框
        key_name = askstring("新建键", "请输入键名:")
        if not key_name:
            return

        try:
            # 检查键是否已存在
            if self.redis_client.client.exists(key_name):
                if not askyesno("确认", f"键 '{key_name}' 已存在，是否覆盖？"):
                    return

            # 设置默认值
            self.redis_client.set_value(key_name, "", "string")

            # 刷新键列表
            self.refresh_keys()

            # 选中新键
            self.key_browser.select_key(key_name)

        except Exception as e:
            showerror("错误", f"创建键失败: {e}")

    def flush_database(self):
        """清空数据库"""
        if not self.redis_client:
            return

        # 检查只读模式
        if self.settings.is_readonly_mode():
            showwarning("只读模式", "当前处于只读模式，无法清空数据库")
            return

        if askyesno("确认", "确定要清空当前数据库吗？此操作不可恢复！"):
            try:
                self.redis_client.client.flushdb()
                self.refresh_keys()
                showinfo("成功", "数据库已清空")
            except Exception as e:
                showerror("错误", f"清空数据库失败: {e}")

    def show_server_info(self):
        """显示服务器信息"""
        if not self.redis_client:
            return

        try:
            info = self.redis_client.get_server_info()

            # 创建信息窗口
            info_window = ttk.Toplevel(self.root)
            info_window.title("Redis 服务器信息")
            info_window.geometry("600x400")

            # 创建文本框显示信息
            text_widget = tk.Text(info_window, wrap=tk.WORD)
            scrollbar = ttk.Scrollbar(
                info_window, orient=VERTICAL, command=text_widget.yview
            )
            text_widget.configure(yscrollcommand=scrollbar.set)

            # 格式化信息
            info_text = ""
            for key, value in info.items():
                info_text += f"{key}: {value}\n"

            text_widget.insert(tk.END, info_text)
            text_widget.config(state=tk.DISABLED)

            # 布局
            text_widget.pack(side=LEFT, fill=BOTH, expand=True)
            scrollbar.pack(side=RIGHT, fill=Y)

        except Exception as e:
            showerror("错误", f"获取服务器信息失败: {e}")

    def show_settings(self):
        """显示设置对话框"""
        try:
            dialog = SettingsDialog(self.root, self.settings)
            if dialog.result:
                # 设置已应用，可能需要更新界面
                self.apply_theme_changes()
        except Exception as e:
            showerror("错误", f"打开设置对话框失败: {e}")

    def apply_theme_changes(self):
        """应用主题变更"""
        try:
            # 获取当前主题
            current_theme = self.settings.get_theme()

            # 应用新主题
            self.root.style.theme_use(current_theme)

            # 更新只读模式状态
            self.update_readonly_mode()

            # 强制刷新界面
            self.root.update_idletasks()

            # 显示成功消息
            showinfo(
                "主题变更", f"主题已成功变更为 '{current_theme}'！", parent=self.root
            )

        except Exception as e:
            print(f"应用主题变更失败: {e}")

    def _save_combobox_state(self):
        """保存Combobox组件的状态"""
        try:
            if hasattr(self, "db_combo") and self.db_combo is not None:
                return {
                    "current_value": self.db_combo.get(),
                    "values": self.db_combo["values"],
                    "state": str(self.db_combo["state"]),
                    "width": self.db_combo["width"],
                }
        except Exception as e:
            print(f"保存Combobox状态失败: {e}")
        return None

    def _rebuild_combobox_safely(self, saved_state):
        """安全地重建Combobox组件"""
        try:
            if not saved_state or not hasattr(self, "db_combo"):
                return True

            # 获取父容器和位置信息
            parent = self.db_combo.master
            pack_info = self.db_combo.pack_info()

            # 销毁旧的Combobox
            self.db_combo.destroy()

            # 创建新的Combobox
            self.db_combo = ttk.Combobox(
                parent,
                width=saved_state.get("width", 5),
                state=saved_state.get("state", "readonly"),
            )

            # 恢复值和选择
            if saved_state.get("values"):
                self.db_combo["values"] = saved_state["values"]

            if saved_state.get("current_value"):
                self.db_combo.set(saved_state["current_value"])

            # 重新绑定事件
            self.db_combo.bind("<<ComboboxSelected>>", self.on_database_changed)

            # 恢复布局
            self.db_combo.pack(**pack_info)

            return True

        except Exception as e:
            print(f"重建Combobox失败: {e}")
            return False

    def update_readonly_mode(self):
        """更新只读模式状态"""
        is_readonly = self.settings.is_readonly_mode()

        if is_readonly:
            # 显示只读模式指示器
            self.readonly_label.pack(side=RIGHT, padx=(0, 10))

            # 禁用相关按钮和菜单
            if hasattr(self, "add_key_btn"):
                self.add_key_btn.config(state=DISABLED)

            # 更新值编辑器的只读状态
            if hasattr(self, "value_editor"):
                self.value_editor.set_readonly_mode(True)

            # 更新键浏览器的只读状态
            if hasattr(self, "key_browser"):
                self.key_browser.set_readonly_mode(True)

        else:
            # 隐藏只读模式指示器
            self.readonly_label.pack_forget()

            # 启用相关按钮（如果已连接）
            if hasattr(self, "add_key_btn") and self.redis_client:
                self.add_key_btn.config(state=NORMAL)

            # 更新值编辑器的只读状态
            if hasattr(self, "value_editor"):
                self.value_editor.set_readonly_mode(False)

            # 更新键浏览器的只读状态
            if hasattr(self, "key_browser"):
                self.key_browser.set_readonly_mode(False)

    def show_about(self):
        """显示关于对话框"""
        showinfo(
            "关于",
            "Redis TTK Client v1.0\n\n"
            "基于 ttkbootstrap 的现代化 Redis 客户端\n"
            "作者: 涵曦\n"
            "技术栈: Python + ttkbootstrap + redis-py",
        )

    def on_closing(self):
        """窗口关闭事件"""
        if self.redis_client:
            self.redis_client.disconnect()

        # 保存窗口几何信息
        try:
            if self.root.state() == "zoomed":
                # 窗口最大化状态
                self.settings.save_window_geometry(1200, 800, 100, 100, True)
            else:
                # 正常窗口状态
                geometry = self.root.geometry()
                # 解析几何字符串 "widthxheight+x+y"
                size_pos = geometry.split("+")
                size = size_pos[0].split("x")
                width, height = int(size[0]), int(size[1])
                x, y = int(size_pos[1]), int(size_pos[2])
                self.settings.save_window_geometry(width, height, x, y, False)
        except Exception as e:
            print(f"保存窗口设置失败: {e}")

        # 立即保存所有设置
        try:
            self.settings.save_app_settings(immediate=True)
        except Exception as e:
            print(f"保存设置失败: {e}")

        self.root.quit()

    # 键操作方法
    def delete_key(self, key: str) -> bool:
        """删除指定的键"""
        if not self.redis_client or not key:
            return False

        # 检查只读模式
        if self.settings.is_readonly_mode():
            showwarning("只读模式", "当前处于只读模式，无法删除键")
            return False

        try:
            if self.redis_client.delete_key(key):
                # 刷新键列表
                self.refresh_keys()
                # 清空值编辑器
                self.value_editor.clear()
                showinfo("成功", f"键 '{key}' 已删除")
                return True
            else:
                showerror("错误", f"删除键 '{key}' 失败")
                return False
        except Exception as e:
            showerror("错误", f"删除键失败: {e}")
            return False

    def rename_key(self, old_key: str, new_key: str) -> bool:
        """重命名键"""
        if not self.redis_client or not old_key or not new_key:
            return False

        # 检查只读模式
        if self.settings.is_readonly_mode():
            showwarning("只读模式", "当前处于只读模式，无法重命名键")
            return False

        try:
            if self.redis_client.rename_key(old_key, new_key):
                # 刷新键列表
                self.refresh_keys()
                # 选中新键
                self.key_browser.select_key(new_key)
                showinfo("成功", f"键已重命名: '{old_key}' -> '{new_key}'")
                return True
            else:
                showerror("错误", "重命名键失败")
                return False
        except Exception as e:
            showerror("错误", f"重命名键失败: {e}")
            return False

    def set_key_ttl(self, key: str, ttl: int) -> bool:
        """设置键的TTL"""
        if not self.redis_client or not key:
            return False

        # 检查只读模式
        if self.settings.is_readonly_mode():
            showwarning("只读模式", "当前处于只读模式，无法修改TTL")
            return False

        try:
            if self.redis_client.set_ttl(key, ttl):
                # 刷新当前键的信息
                self.on_key_selected(key)
                showinfo("成功", f"键 '{key}' 的TTL已设置为 {ttl} 秒")
                return True
            else:
                showerror("错误", "设置TTL失败")
                return False
        except Exception as e:
            error_msg = str(e)
            if (
                "forbidden command 'EXPIRE'" in error_msg
                or "persistdb" in error_msg.lower()
            ):
                showerror(
                    "错误",
                    "设置TTL失败: 当前数据库不支持EXPIRE命令\n这可能是一个持久化数据库或受限制的Redis实例",
                )
            else:
                showerror("错误", f"设置TTL失败: {e}")
            return False

    def remove_key_ttl(self, key: str) -> bool:
        """移除键的TTL"""
        if not self.redis_client or not key:
            return False

        # 检查只读模式
        if self.settings.is_readonly_mode():
            showwarning("只读模式", "当前处于只读模式，无法修改TTL")
            return False

        try:
            if self.redis_client.remove_ttl(key):
                # 刷新当前键的信息
                self.on_key_selected(key)
                showinfo("成功", f"键 '{key}' 的TTL已移除")
                return True
            else:
                showerror("错误", "移除TTL失败")
                return False
        except Exception as e:
            error_msg = str(e)
            if (
                "forbidden command 'PERSIST'" in error_msg
                or "persistdb" in error_msg.lower()
            ):
                showerror(
                    "错误",
                    "移除TTL失败: 当前数据库不支持PERSIST命令\n这可能是一个持久化数据库或受限制的Redis实例",
                )
            else:
                showerror("错误", f"移除TTL失败: {e}")
            return False
