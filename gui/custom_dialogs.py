"""
自定义TTK对话框组件
用于替代tkinter的messagebox和simpledialog，提供现代化的TTK样式
"""

import tkinter as tk
from collections.abc import Callable
from tkinter import filedialog

import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, LEFT, RIGHT, SECONDARY, SUCCESS, WARNING, W, X


class MessageDialog:
    """自定义消息对话框，替代messagebox"""

    # 对话框类型常量
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    QUESTION = "question"

    # 按钮类型常量
    OK = "ok"
    OK_CANCEL = "ok_cancel"
    YES_NO = "yes_no"
    YES_NO_CANCEL = "yes_no_cancel"
    RETRY_CANCEL = "retry_cancel"

    def __init__(
        self,
        parent,
        title: str,
        message: str,
        dialog_type: str = INFO,
        buttons: str = OK,
        default_button: str | None = None,
    ):
        """
        初始化消息对话框

        Args:
            parent: 父窗口
            title: 对话框标题
            message: 消息内容
            dialog_type: 对话框类型 (INFO, WARNING, ERROR, QUESTION)
            buttons: 按钮类型 (OK, OK_CANCEL, YES_NO, YES_NO_CANCEL, RETRY_CANCEL)
            default_button: 默认按钮
        """
        self.parent = parent
        self.title = title
        self.message = message
        self.dialog_type = dialog_type
        self.buttons = buttons
        self.default_button = default_button
        self.result = None

        # 创建对话框
        self.dialog = ttk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.resizable(False, False)

        # 设置模态
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 创建界面
        self.create_widgets()

        # 居中显示
        self.center_dialog()

        # 绑定事件
        self.bind_events()

        # 等待用户操作
        self.dialog.wait_window()

    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=BOTH, expand=True)

        # 内容框架
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=BOTH, expand=True, pady=(0, 20))

        # 图标
        icon_label = ttk.Label(content_frame, text=self._get_icon(), font=("Arial", 24))
        icon_label.pack(side=LEFT, padx=(0, 15))

        # 消息文本
        message_label = ttk.Label(
            content_frame, text=self.message, wraplength=400, justify=LEFT
        )
        message_label.pack(side=LEFT, fill=BOTH, expand=True)

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=X)

        # 创建按钮
        self.create_buttons(button_frame)

    def _get_icon(self) -> str:
        """获取对话框图标"""
        icons = {
            self.INFO: "ℹ️",
            self.WARNING: "⚠️",
            self.ERROR: "❌",
            self.QUESTION: "❓",
        }
        return icons.get(self.dialog_type, "ℹ️")

    def create_buttons(self, parent):
        """创建按钮"""
        button_configs = {
            self.OK: [("确定", "ok", SUCCESS)],
            self.OK_CANCEL: [("确定", "ok", SUCCESS), ("取消", "cancel", SECONDARY)],
            self.YES_NO: [("是", "yes", SUCCESS), ("否", "no", SECONDARY)],
            self.YES_NO_CANCEL: [
                ("是", "yes", SUCCESS),
                ("否", "no", SECONDARY),
                ("取消", "cancel", SECONDARY),
            ],
            self.RETRY_CANCEL: [
                ("重试", "retry", WARNING),
                ("取消", "cancel", SECONDARY),
            ],
        }

        buttons_config = button_configs.get(self.buttons, button_configs[self.OK])

        # 从右到左创建按钮
        for text, result, style in reversed(buttons_config):
            btn = ttk.Button(
                parent,
                text=text,
                command=lambda r=result: self.set_result(r),
                bootstyle=style,
                width=8,
            )
            btn.pack(side=RIGHT, padx=(5, 0))

            # 设置默认按钮
            if self.default_button == result or (
                self.default_button is None and result == "ok"
            ):
                btn.focus_set()
                self.dialog.bind("<Return>", lambda e, r=result: self.set_result(r))

        # 绑定Escape键到取消
        if any(result in ["cancel", "no"] for _, result, _ in buttons_config):
            self.dialog.bind(
                "<Escape>",
                lambda e: self.set_result(
                    "cancel" if "cancel" in [r for _, r, _ in buttons_config] else "no"
                ),
            )

    def set_result(self, result: str):
        """设置结果并关闭对话框"""
        self.result = result
        self.dialog.destroy()

    def center_dialog(self):
        """对话框居中显示"""
        self.dialog.update_idletasks()

        # 获取父窗口位置和大小
        if self.parent:
            parent_x = self.parent.winfo_rootx()
            parent_y = self.parent.winfo_rooty()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()

            # 计算对话框位置
            dialog_width = self.dialog.winfo_width()
            dialog_height = self.dialog.winfo_height()

            x = parent_x + (parent_width - dialog_width) // 2
            y = parent_y + (parent_height - dialog_height) // 2
        else:
            # 屏幕居中
            screen_width = self.dialog.winfo_screenwidth()
            screen_height = self.dialog.winfo_screenheight()
            dialog_width = self.dialog.winfo_width()
            dialog_height = self.dialog.winfo_height()

            x = (screen_width - dialog_width) // 2
            y = (screen_height - dialog_height) // 2

        self.dialog.geometry(f"+{x}+{y}")

    def bind_events(self):
        """绑定事件"""
        # 窗口关闭事件
        self.dialog.protocol("WM_DELETE_WINDOW", lambda: self.set_result("cancel"))

    @classmethod
    def show_info(cls, parent, title: str, message: str) -> str:
        """显示信息对话框"""
        dialog = cls(parent, title, message, cls.INFO, cls.OK)
        return dialog.result

    @classmethod
    def show_warning(cls, parent, title: str, message: str) -> str:
        """显示警告对话框"""
        dialog = cls(parent, title, message, cls.WARNING, cls.OK)
        return dialog.result

    @classmethod
    def show_error(cls, parent, title: str, message: str) -> str:
        """显示错误对话框"""
        dialog = cls(parent, title, message, cls.ERROR, cls.OK)
        return dialog.result

    @classmethod
    def ask_question(cls, parent, title: str, message: str) -> bool:
        """显示问题对话框，返回True/False"""
        dialog = cls(parent, title, message, cls.QUESTION, cls.YES_NO)
        return dialog.result == "yes"

    @classmethod
    def ask_ok_cancel(cls, parent, title: str, message: str) -> bool:
        """显示确定/取消对话框，返回True/False"""
        dialog = cls(parent, title, message, cls.QUESTION, cls.OK_CANCEL)
        return dialog.result == "ok"

    @classmethod
    def ask_retry_cancel(cls, parent, title: str, message: str) -> bool:
        """显示重试/取消对话框，返回True/False"""
        dialog = cls(parent, title, message, cls.WARNING, cls.RETRY_CANCEL)
        return dialog.result == "retry"


class InputDialog:
    """自定义输入对话框，替代simpledialog"""

    def __init__(
        self,
        parent,
        title: str,
        prompt: str,
        initial_value: str = "",
        input_type: str = "string",
        validator: Callable[[str], bool] | None = None,
        min_value: float | None = None,
        max_value: float | None = None,
    ):
        """
        初始化输入对话框

        Args:
            parent: 父窗口
            title: 对话框标题
            prompt: 提示文本
            initial_value: 初始值
            input_type: 输入类型 ("string", "int", "float")
            validator: 自定义验证函数
            min_value: 最小值（数字类型）
            max_value: 最大值（数字类型）
        """
        self.parent = parent
        self.title = title
        self.prompt = prompt
        self.initial_value = str(initial_value)
        self.input_type = input_type
        self.validator = validator
        self.min_value = min_value
        self.max_value = max_value
        self.result = None

        # 创建对话框
        self.dialog = ttk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.resizable(False, False)

        # 设置模态
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 创建界面
        self.create_widgets()

        # 居中显示
        self.center_dialog()

        # 绑定事件
        self.bind_events()

        # 等待用户操作
        self.dialog.wait_window()

    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=BOTH, expand=True)

        # 提示标签
        prompt_label = ttk.Label(main_frame, text=self.prompt)
        prompt_label.pack(anchor=W, pady=(0, 10))

        # 输入框
        self.entry_var = tk.StringVar(value=self.initial_value)
        self.entry = ttk.Entry(main_frame, textvariable=self.entry_var, width=40)
        self.entry.pack(fill=X, pady=(0, 10))
        self.entry.select_range(0, tk.END)
        self.entry.focus_set()

        # 错误提示标签
        self.error_label = ttk.Label(main_frame, text="", foreground="red")
        self.error_label.pack(anchor=W, pady=(0, 10))

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=X)

        # 取消按钮
        cancel_btn = ttk.Button(
            button_frame, text="取消", command=self.cancel, bootstyle=SECONDARY, width=8
        )
        cancel_btn.pack(side=RIGHT, padx=(5, 0))

        # 确定按钮
        ok_btn = ttk.Button(
            button_frame, text="确定", command=self.ok, bootstyle=SUCCESS, width=8
        )
        ok_btn.pack(side=RIGHT)

    def validate_input(self, value: str) -> tuple[bool, str]:
        """验证输入值"""
        if not value.strip():
            return False, "输入不能为空"

        # 自定义验证器
        if self.validator:
            try:
                if not self.validator(value):
                    return False, "输入格式不正确"
            except Exception as e:
                return False, f"验证错误: {e}"

        # 类型验证
        if self.input_type == "int":
            try:
                int_value = int(value)
                if self.min_value is not None and int_value < self.min_value:
                    return False, f"值不能小于 {self.min_value}"
                if self.max_value is not None and int_value > self.max_value:
                    return False, f"值不能大于 {self.max_value}"
            except ValueError:
                return False, "请输入有效的整数"

        elif self.input_type == "float":
            try:
                float_value = float(value)
                if self.min_value is not None and float_value < self.min_value:
                    return False, f"值不能小于 {self.min_value}"
                if self.max_value is not None and float_value > self.max_value:
                    return False, f"值不能大于 {self.max_value}"
            except ValueError:
                return False, "请输入有效的数字"

        return True, ""

    def ok(self):
        """确定按钮事件"""
        value = self.entry_var.get()
        is_valid, error_msg = self.validate_input(value)

        if is_valid:
            # 转换类型
            if self.input_type == "int":
                self.result = int(value)
            elif self.input_type == "float":
                self.result = float(value)
            else:
                self.result = value

            self.dialog.destroy()
        else:
            self.error_label.config(text=error_msg)

    def cancel(self):
        """取消按钮事件"""
        self.result = None
        self.dialog.destroy()

    def center_dialog(self):
        """对话框居中显示"""
        self.dialog.update_idletasks()

        # 获取父窗口位置和大小
        if self.parent:
            parent_x = self.parent.winfo_rootx()
            parent_y = self.parent.winfo_rooty()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()

            # 计算对话框位置
            dialog_width = self.dialog.winfo_width()
            dialog_height = self.dialog.winfo_height()

            x = parent_x + (parent_width - dialog_width) // 2
            y = parent_y + (parent_height - dialog_height) // 2
        else:
            # 屏幕居中
            screen_width = self.dialog.winfo_screenwidth()
            screen_height = self.dialog.winfo_screenheight()
            dialog_width = self.dialog.winfo_width()
            dialog_height = self.dialog.winfo_height()

            x = (screen_width - dialog_width) // 2
            y = (screen_height - dialog_height) // 2

        self.dialog.geometry(f"+{x}+{y}")

    def bind_events(self):
        """绑定事件"""
        # 回车键确定
        self.dialog.bind("<Return>", lambda e: self.ok())
        # Escape键取消
        self.dialog.bind("<Escape>", lambda e: self.cancel())
        # 窗口关闭事件
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)

        # 实时验证
        self.entry_var.trace_add("write", self.on_text_change)

    def on_text_change(self, *args):
        """文本变化事件"""
        # 清除错误提示
        self.error_label.config(text="")

    @classmethod
    def ask_string(
        cls, parent, title: str, prompt: str, initial_value: str = ""
    ) -> str | None:
        """获取字符串输入"""
        dialog = cls(parent, title, prompt, initial_value, "string")
        return dialog.result

    @classmethod
    def ask_integer(
        cls,
        parent,
        title: str,
        prompt: str,
        initial_value: int = 0,
        min_value: int | None = None,
        max_value: int | None = None,
    ) -> int | None:
        """获取整数输入"""
        dialog = cls(
            parent,
            title,
            prompt,
            str(initial_value),
            "int",
            min_value=min_value,
            max_value=max_value,
        )
        return dialog.result

    @classmethod
    def ask_float(
        cls,
        parent,
        title: str,
        prompt: str,
        initial_value: float = 0.0,
        min_value: float | None = None,
        max_value: float | None = None,
    ) -> float | None:
        """获取浮点数输入"""
        dialog = cls(
            parent,
            title,
            prompt,
            str(initial_value),
            "float",
            min_value=min_value,
            max_value=max_value,
        )
        return dialog.result


class FileDialog:
    """文件对话框包装器，保持与原有filedialog的兼容性"""

    @staticmethod
    def askopenfilename(parent=None, **kwargs):
        """打开文件对话框"""
        return filedialog.askopenfilename(parent=parent, **kwargs)

    @staticmethod
    def asksaveasfilename(parent=None, **kwargs):
        """保存文件对话框"""
        return filedialog.asksaveasfilename(parent=parent, **kwargs)

    @staticmethod
    def askdirectory(parent=None, **kwargs):
        """选择目录对话框"""
        return filedialog.askdirectory(parent=parent, **kwargs)

    @staticmethod
    def askopenfilenames(parent=None, **kwargs):
        """打开多个文件对话框"""
        return filedialog.askopenfilenames(parent=parent, **kwargs)


# 便捷函数，兼容原有的messagebox和simpledialog接口
def showinfo(title: str, message: str, parent=None):
    """显示信息对话框"""
    return MessageDialog.show_info(parent, title, message)


def showwarning(title: str, message: str, parent=None):
    """显示警告对话框"""
    return MessageDialog.show_warning(parent, title, message)


def showerror(title: str, message: str, parent=None):
    """显示错误对话框"""
    return MessageDialog.show_error(parent, title, message)


def askquestion(title: str, message: str, parent=None):
    """显示问题对话框"""
    return "yes" if MessageDialog.ask_question(parent, title, message) else "no"


def askyesno(title: str, message: str, parent=None):
    """显示是/否对话框"""
    return MessageDialog.ask_question(parent, title, message)


def askokcancel(title: str, message: str, parent=None):
    """显示确定/取消对话框"""
    return MessageDialog.ask_ok_cancel(parent, title, message)


def askretrycancel(title: str, message: str, parent=None):
    """显示重试/取消对话框"""
    return MessageDialog.ask_retry_cancel(parent, title, message)


def askstring(title: str, prompt: str, parent=None, initialvalue: str = ""):
    """获取字符串输入"""
    return InputDialog.ask_string(parent, title, prompt, initialvalue)


def askinteger(
    title: str,
    prompt: str,
    parent=None,
    initialvalue: int = 0,
    minvalue: int | None = None,
    maxvalue: int | None = None,
):
    """获取整数输入"""
    return InputDialog.ask_integer(
        parent, title, prompt, initialvalue, minvalue, maxvalue
    )


def askfloat(
    title: str,
    prompt: str,
    parent=None,
    initialvalue: float = 0.0,
    minvalue: float | None = None,
    maxvalue: float | None = None,
):
    """获取浮点数输入"""
    return InputDialog.ask_float(
        parent, title, prompt, initialvalue, minvalue, maxvalue
    )
