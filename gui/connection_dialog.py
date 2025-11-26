"""
连接对话框
用于配置 Redis 连接参数
"""

import tkinter as tk

import ttkbootstrap as ttk
from ttkbootstrap.constants import (
    BOTH,
    DANGER,
    DISABLED,
    INFO,
    LEFT,
    NORMAL,
    RIGHT,
    SECONDARY,
    SUCCESS,
    WARNING,
    E,
    W,
    X,
)

from gui.custom_dialogs import askyesno, showerror, showinfo
from redis_client import RedisConfig


class ConnectionDialog:
    """Redis 连接配置对话框"""

    def __init__(self, parent, settings=None):
        """初始化连接对话框"""
        self.parent = parent
        self.settings = settings
        self.result: RedisConfig | None = None
        self.connection_name: str | None = None

        # 创建对话框窗口
        self.dialog = ttk.Toplevel(parent)
        self.dialog.title("Redis 连接配置")
        self.dialog.resizable(True, True)

        # 先不设置几何尺寸，让窗口根据内容自适应

        # 设置模态
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 创建界面
        self.create_widgets()

        # 绑定事件
        self.bind_events()

        # 自动调整窗口大小并居中显示
        self.auto_resize_and_center()

        # 等待用户操作
        self.dialog.wait_window()

    def auto_resize_and_center(self):
        """自动调整窗口大小并居中显示"""
        # 更新所有组件的几何信息
        self.dialog.update_idletasks()

        # 获取窗口所需的最小尺寸
        req_width = self.dialog.winfo_reqwidth()
        req_height = self.dialog.winfo_reqheight()

        # 设置合理的最小和最大尺寸
        min_width = max(500, req_width + 50)  # 至少500px宽度，留50px边距
        min_height = max(450, req_height + 50)  # 至少450px高度，留50px边距

        # 获取屏幕尺寸
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()

        # 限制最大尺寸不超过屏幕的80%
        max_width = int(screen_width * 0.8)
        max_height = int(screen_height * 0.8)

        # 计算最终窗口尺寸
        final_width = min(min_width, max_width)
        final_height = min(min_height, max_height)

        # 设置最小尺寸
        self.dialog.minsize(min_width, min_height)

        # 获取父窗口位置和大小
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        # 计算居中位置
        x = parent_x + (parent_width - final_width) // 2
        y = parent_y + (parent_height - final_height) // 2

        # 确保窗口不会超出屏幕边界
        x = max(0, min(x, screen_width - final_width))
        y = max(0, min(y, screen_height - final_height))

        # 设置窗口几何信息
        self.dialog.geometry(f"{final_width}x{final_height}+{x}+{y}")

        # 再次更新以确保布局正确
        self.dialog.update_idletasks()

    def on_tab_changed(self, event=None):
        """标签页切换事件处理"""
        # 延迟调整窗口大小，确保新标签页内容已经渲染
        self.dialog.after(50, self.adjust_window_size_for_current_tab)

    def adjust_window_size_for_current_tab(self):
        """根据当前标签页调整窗口大小"""
        # 更新布局
        self.dialog.update_idletasks()

        # 获取当前窗口尺寸
        current_width = self.dialog.winfo_width()
        current_height = self.dialog.winfo_height()

        # 获取所需的最小尺寸
        req_width = self.dialog.winfo_reqwidth()
        req_height = self.dialog.winfo_reqheight()

        # 计算新的尺寸（保持一定的边距）
        new_width = max(current_width, req_width + 50)
        new_height = max(450, req_height + 50)  # 保持最小高度

        # 获取屏幕尺寸限制
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        max_width = int(screen_width * 0.8)
        max_height = int(screen_height * 0.8)

        # 应用尺寸限制
        new_width = min(new_width, max_width)
        new_height = min(new_height, max_height)

        # 只有当尺寸发生变化时才调整
        if new_width != current_width or new_height != current_height:
            # 获取当前位置
            current_x = self.dialog.winfo_x()
            current_y = self.dialog.winfo_y()

            # 调整位置以保持居中（如果窗口变大）
            if new_width > current_width:
                current_x -= (new_width - current_width) // 2
            if new_height > current_height:
                current_y -= (new_height - current_height) // 2

            # 确保窗口不会超出屏幕边界
            current_x = max(0, min(current_x, screen_width - new_width))
            current_y = max(0, min(current_y, screen_height - new_height))

            # 应用新的几何信息
            self.dialog.geometry(f"{new_width}x{new_height}+{current_x}+{current_y}")

    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding=15)
        main_frame.pack(fill=BOTH, expand=True)

        # 创建 Notebook 用于分页
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=BOTH, expand=True, pady=(0, 15))

        # 绑定标签页切换事件
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # 创建各个页面
        self.create_basic_page()
        self.create_advanced_page()
        self.create_management_page()

        # 创建按钮区域
        self.create_buttons(main_frame)

        # 设置焦点
        self.host_entry.focus()

    def bind_events(self):
        """绑定事件"""
        self.dialog.bind("<Return>", lambda e: self.ok())
        self.dialog.bind("<Escape>", lambda e: self.cancel())

        # 绑定窗口关闭事件
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)

    def validate_input(self) -> bool:
        """验证输入参数"""
        # 验证主机地址
        host = self.host_entry.get().strip()
        if not host:
            showerror("错误", "请输入主机地址", parent=self.dialog)
            self.notebook.select(0)  # 切换到基本连接页面
            self.host_entry.focus()
            return False

        # 验证端口
        try:
            port = int(self.port_entry.get())
            if not (1 <= port <= 65535):
                raise ValueError()
        except ValueError:
            showerror("错误", "请输入有效的端口号 (1-65535)", parent=self.dialog)
            self.notebook.select(0)  # 切换到基本连接页面
            self.port_entry.focus()
            return False

        # 验证数据库编号
        try:
            db = int(self.db_entry.get())
            if db < 0:
                raise ValueError()
        except ValueError:
            showerror("错误", "请输入有效的数据库编号 (≥0)", parent=self.dialog)
            self.notebook.select(0)  # 切换到基本连接页面
            self.db_entry.focus()
            return False

        # 验证超时时间
        try:
            timeout = float(self.timeout_entry.get())
            if timeout <= 0:
                raise ValueError()
        except ValueError:
            showerror("错误", "请输入有效的超时时间 (>0)", parent=self.dialog)
            self.notebook.select(1)  # 切换到高级选项页面
            self.timeout_entry.focus()
            return False

        return True

    def get_config(self) -> RedisConfig:
        """获取连接配置"""
        password = self.password_entry.get().strip()
        if not password:
            password = None

        return RedisConfig(
            host=self.host_entry.get().strip(),
            port=int(self.port_entry.get()),
            password=password,
            db=int(self.db_entry.get()),
            decode_responses=self.decode_var.get(),
            socket_timeout=float(self.timeout_entry.get()),
            socket_connect_timeout=float(self.timeout_entry.get()),
            retry_on_timeout=self.retry_var.get(),
        )

    def test_connection(self):
        """测试连接"""
        if not self.validate_input():
            return

        # 禁用按钮
        self.test_btn.config(state=DISABLED, text="测试中...")
        self.dialog.update()

        try:
            # 创建临时客户端测试连接
            from redis_client import RedisClient

            config = self.get_config()
            client = RedisClient(config)

            if client.connect():
                client.disconnect()
                showinfo("成功", "连接测试成功！", parent=self.dialog)
            else:
                showerror("失败", "连接测试失败！", parent=self.dialog)

        except Exception as e:
            showerror("错误", f"连接测试失败: {e}", parent=self.dialog)

        finally:
            # 恢复按钮
            self.test_btn.config(state=NORMAL, text="测试连接")

    def load_history_connections(self):
        """加载历史连接列表"""
        if not self.settings:
            return

        recent_connections = self.settings.get_recent_connections()
        connection_names = [conn["name"] for conn in recent_connections]

        self.history_combo["values"] = connection_names
        if connection_names:
            self.history_combo.set("")  # 不默认选择任何连接

    def on_history_selected(self, event=None):
        """历史连接选择事件"""
        selected_name = self.history_combo.get()
        if not selected_name or not self.settings:
            self.update_connection_preview()
            return

        config = self.settings.get_connection(selected_name)
        if config:
            # 填充连接参数
            self.host_entry.delete(0, tk.END)
            self.host_entry.insert(0, config.host)

            self.port_entry.delete(0, tk.END)
            self.port_entry.insert(0, str(config.port))

            self.password_entry.delete(0, tk.END)
            if config.password:
                self.password_entry.insert(0, config.password)

            self.db_entry.delete(0, tk.END)
            self.db_entry.insert(0, str(config.db))

            self.timeout_entry.delete(0, tk.END)
            self.timeout_entry.insert(0, str(config.socket_timeout))

            self.decode_var.set(config.decode_responses)
            self.retry_var.set(config.retry_on_timeout)

            # 设置连接名称
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, selected_name)

            # 更新连接预览
            self.update_connection_preview(selected_name)

    def delete_selected_connection(self):
        """删除选中的连接"""
        selected_name = self.history_combo.get()
        if not selected_name or not self.settings:
            return

        if askyesno(
            "确认删除", f"确定要删除连接 '{selected_name}' 吗？", parent=self.dialog
        ):
            self.settings.delete_connection(selected_name)
            self.load_history_connections()
            # 清空表单
            self.clear_form()

    def clear_form(self):
        """清空表单"""
        self.host_entry.delete(0, tk.END)
        self.host_entry.insert(0, "localhost")

        self.port_entry.delete(0, tk.END)
        self.port_entry.insert(0, "6379")

        self.password_entry.delete(0, tk.END)

        self.db_entry.delete(0, tk.END)
        self.db_entry.insert(0, "0")

        self.timeout_entry.delete(0, tk.END)
        self.timeout_entry.insert(0, "5.0")

        self.decode_var.set(True)
        self.retry_var.set(True)

        self.name_entry.delete(0, tk.END)

        if hasattr(self, "history_combo"):
            self.history_combo.set("")

    def ok(self):
        """确定按钮事件"""
        if self.validate_input():
            self.result = self.get_config()

            # 保存连接配置
            if self.settings and self.save_connection_var.get():
                connection_name = self.name_entry.get().strip()
                if not connection_name:
                    # 如果没有输入名称，生成默认名称
                    connection_name = f"{self.result.host}:{self.result.port}"

                self.connection_name = connection_name
                self.settings.save_connection(connection_name, self.result)

            self.dialog.destroy()

    def cancel(self):
        """取消按钮事件"""
        self.result = None
        self.dialog.destroy()

    def create_basic_page(self):
        """创建基本连接页面"""
        self.basic_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.basic_frame, text="基本连接")

        # 连接参数框架
        params_frame = ttk.Labelframe(self.basic_frame, text="连接参数", padding=15)
        params_frame.pack(fill=X, padx=10, pady=10)

        # 主机地址
        ttk.Label(params_frame, text="主机地址:").grid(
            row=0, column=0, sticky=W, pady=8
        )
        self.host_entry = ttk.Entry(params_frame, width=25)
        self.host_entry.insert(0, "localhost")
        self.host_entry.grid(row=0, column=1, sticky=W + E, pady=8, padx=(10, 0))

        # 端口
        ttk.Label(params_frame, text="端口:").grid(row=1, column=0, sticky=W, pady=8)
        self.port_entry = ttk.Entry(params_frame, width=25)
        self.port_entry.insert(0, "6379")
        self.port_entry.grid(row=1, column=1, sticky=W + E, pady=8, padx=(10, 0))

        # 密码
        ttk.Label(params_frame, text="密码:").grid(row=2, column=0, sticky=W, pady=8)
        password_frame = ttk.Frame(params_frame)
        password_frame.grid(row=2, column=1, sticky=W + E, pady=8, padx=(10, 0))

        self.password_entry = ttk.Entry(password_frame, show="*", width=20)
        self.password_entry.pack(side=LEFT, fill=X, expand=True)

        # 显示/隐藏密码按钮
        self.show_password_var = tk.BooleanVar()
        self.show_password_btn = ttk.Checkbutton(
            password_frame,
            text="显示",
            variable=self.show_password_var,
            command=self.toggle_password_visibility,
        )
        self.show_password_btn.pack(side=RIGHT, padx=(5, 0))

        # 数据库
        ttk.Label(params_frame, text="数据库:").grid(row=3, column=0, sticky=W, pady=8)
        self.db_entry = ttk.Entry(params_frame, width=25)
        self.db_entry.insert(0, "0")
        self.db_entry.grid(row=3, column=1, sticky=W + E, pady=8, padx=(10, 0))

        # 配置列权重
        params_frame.columnconfigure(1, weight=1)
        password_frame.columnconfigure(0, weight=1)

        # 连接名称框架
        name_frame = ttk.Labelframe(self.basic_frame, text="连接名称", padding=15)
        name_frame.pack(fill=X, padx=10, pady=(0, 10))

        ttk.Label(name_frame, text="名称:").grid(row=0, column=0, sticky=W, pady=5)
        self.name_entry = ttk.Entry(name_frame, width=25)
        self.name_entry.grid(row=0, column=1, sticky=W + E, pady=5, padx=(10, 0))

        # 保存连接选项
        self.save_connection_var = tk.BooleanVar(value=True)
        self.save_connection_check = ttk.Checkbutton(
            name_frame, text="保存此连接配置", variable=self.save_connection_var
        )
        self.save_connection_check.grid(row=1, column=0, columnspan=2, sticky=W, pady=5)

        # 配置列权重
        name_frame.columnconfigure(1, weight=1)

    def create_advanced_page(self):
        """创建高级选项页面"""
        self.advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.advanced_frame, text="高级选项")

        # 高级选项框架
        options_frame = ttk.Labelframe(self.advanced_frame, text="连接选项", padding=15)
        options_frame.pack(fill=X, padx=10, pady=10)

        # 连接超时
        ttk.Label(options_frame, text="连接超时(秒):").grid(
            row=0, column=0, sticky=W, pady=8
        )
        self.timeout_entry = ttk.Entry(options_frame, width=25)
        self.timeout_entry.insert(0, "5.0")
        self.timeout_entry.grid(row=0, column=1, sticky=W + E, pady=8, padx=(10, 0))

        # 解码响应
        self.decode_var = tk.BooleanVar(value=True)
        self.decode_check = ttk.Checkbutton(
            options_frame, text="解码响应为字符串", variable=self.decode_var
        )
        self.decode_check.grid(row=1, column=0, columnspan=2, sticky=W, pady=8)

        # 超时重试
        self.retry_var = tk.BooleanVar(value=True)
        self.retry_check = ttk.Checkbutton(
            options_frame, text="超时时重试连接", variable=self.retry_var
        )
        self.retry_check.grid(row=2, column=0, columnspan=2, sticky=W, pady=8)

        # 配置列权重
        options_frame.columnconfigure(1, weight=1)

    def create_management_page(self):
        """创建连接管理页面"""
        self.management_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.management_frame, text="连接管理")

        # 历史连接框架
        if self.settings:
            history_frame = ttk.Labelframe(
                self.management_frame, text="历史连接", padding=15
            )
            history_frame.pack(fill=X, padx=10, pady=10)

            # 历史连接选择
            select_frame = ttk.Frame(history_frame)
            select_frame.pack(fill=X, pady=(0, 10))

            ttk.Label(select_frame, text="选择连接:").pack(anchor=W, pady=(0, 5))

            combo_frame = ttk.Frame(select_frame)
            combo_frame.pack(fill=X)

            self.history_combo = ttk.Combobox(combo_frame, state="readonly", width=30)
            self.history_combo.pack(side=LEFT, fill=X, expand=True)
            self.history_combo.bind("<<ComboboxSelected>>", self.on_history_selected)

            # 删除连接按钮
            self.delete_btn = ttk.Button(
                combo_frame,
                text="删除",
                command=self.delete_selected_connection,
                bootstyle=DANGER,
                width=8,
            )
            self.delete_btn.pack(side=RIGHT, padx=(10, 0))

            # 连接预览框架
            preview_frame = ttk.Labelframe(history_frame, text="连接预览", padding=10)
            preview_frame.pack(fill=X, pady=(10, 0))

            self.preview_text = tk.Text(
                preview_frame,
                height=6,
                wrap=tk.WORD,
                font=("Consolas", 9),
                state=tk.DISABLED,
            )
            self.preview_text.pack(fill=X)

            # 加载历史连接
            self.load_history_connections()

        # 操作按钮框架
        actions_frame = ttk.Labelframe(self.management_frame, text="操作", padding=15)
        actions_frame.pack(fill=X, padx=10, pady=(0, 10))

        # 清空表单按钮
        clear_btn = ttk.Button(
            actions_frame,
            text="清空表单",
            command=self.clear_form,
            bootstyle=WARNING,
            width=12,
        )
        clear_btn.pack(side=LEFT, padx=(0, 10))

        # 测试连接按钮
        self.test_btn = ttk.Button(
            actions_frame,
            text="测试连接",
            command=self.test_connection,
            bootstyle=INFO,
            width=12,
        )
        self.test_btn.pack(side=LEFT)

    def create_buttons(self, parent):
        """创建按钮区域"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=X, pady=(10, 0))

        # 右侧按钮
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=RIGHT)

        # 取消按钮
        self.cancel_btn = ttk.Button(
            right_buttons,
            text="取消",
            command=self.cancel,
            bootstyle=SECONDARY,
            width=8,
        )
        self.cancel_btn.pack(side=RIGHT, padx=(10, 0))

        # 确定按钮
        self.ok_btn = ttk.Button(
            right_buttons, text="连接", command=self.ok, bootstyle=SUCCESS, width=8
        )
        self.ok_btn.pack(side=RIGHT)

    def toggle_password_visibility(self):
        """切换密码显示/隐藏"""
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

    def update_connection_preview(self, config_name: str = ""):
        """更新连接预览"""
        if not hasattr(self, "preview_text"):
            return

        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)

        if config_name and self.settings:
            config = self.settings.get_connection(config_name)
            if config:
                preview_text = f"连接名称: {config_name}\n"
                preview_text += f"主机地址: {config.host}\n"
                preview_text += f"端口: {config.port}\n"
                preview_text += f"数据库: {config.db}\n"
                preview_text += f"密码: {'是' if config.password else '否'}\n"
                preview_text += f"超时时间: {config.socket_timeout}秒"

                self.preview_text.insert(1.0, preview_text)
        else:
            self.preview_text.insert(1.0, "请选择一个历史连接查看详情")

        self.preview_text.config(state=tk.DISABLED)
