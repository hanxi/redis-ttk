"""
设置对话框
用于配置应用程序的各种选项
"""

import tkinter as tk
from tkinter import filedialog

import ttkbootstrap as ttk
from ttkbootstrap.constants import (
    BOTH,
    INFO,
    LEFT,
    PRIMARY,
    RIGHT,
    SECONDARY,
    SUCCESS,
    WARNING,
    E,
    W,
    X,
)

from config.settings import Settings
from gui.custom_dialogs import askyesno, showerror, showinfo


class SettingsDialog:
    """设置对话框类"""

    def __init__(self, parent, settings: Settings):
        """初始化设置对话框"""
        self.parent = parent
        self.settings = settings
        self.result = False  # 是否应用了设置

        # 保存原始设置用于取消时恢复
        self.original_settings = {}
        self._backup_settings()

        # 创建对话框窗口
        self.dialog = ttk.Toplevel(parent)
        self.dialog.title("设置")
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)

        # 设置模态
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 居中显示
        self.center_dialog()

        # 创建界面
        self.create_widgets()

        # 绑定事件
        self.bind_events()

        # 加载当前设置
        self.load_current_settings()

        # 等待用户操作
        self.dialog.wait_window()

    def _backup_settings(self):
        """备份当前设置"""
        self.original_settings = {
            "theme": self.settings.get_theme(),
            "font": self.settings.get_font(),
            "editor_options": self.settings.get_editor_options(),
            "connection_options": self.settings.get_connection_options(),
            "other_options": self.settings.get_other_options(),
        }

    def center_dialog(self):
        """对话框居中显示"""
        self.dialog.update_idletasks()

        # 获取父窗口位置和大小
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        # 计算对话框位置
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()

        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2

        self.dialog.geometry(f"+{x}+{y}")

    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=BOTH, expand=True)

        # 创建 Notebook 用于分页
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=BOTH, expand=True, pady=(0, 10))

        # 创建各个设置页面
        self.create_interface_page()
        self.create_editor_page()
        self.create_connection_page()
        self.create_other_page()
        self.create_import_export_page()

        # 创建按钮区域
        self.create_buttons()

    def create_interface_page(self):
        """创建界面设置页"""
        self.interface_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.interface_frame, text="界面")

        # 主题设置
        theme_frame = ttk.Labelframe(self.interface_frame, text="主题设置", padding=15)
        theme_frame.pack(fill=X, padx=10, pady=10)

        ttk.Label(theme_frame, text="主题:").grid(row=0, column=0, sticky=W, pady=5)
        self.theme_combo = ttk.Combobox(
            theme_frame,
            values=[
                "superhero",
                "darkly",
                "solar",
                "cyborg",
                "vapor",
                "flatly",
                "journal",
                "litera",
                "lumen",
                "minty",
                "pulse",
                "sandstone",
                "united",
                "yeti",
                "morph",
                "simplex",
                "cerculean",
            ],
            state="readonly",
            width=20,
        )
        self.theme_combo.grid(row=0, column=1, sticky=W + E, pady=5, padx=(10, 0))

        # 字体设置
        font_frame = ttk.Labelframe(self.interface_frame, text="字体设置", padding=15)
        font_frame.pack(fill=X, padx=10, pady=10)

        ttk.Label(font_frame, text="字体家族:").grid(row=0, column=0, sticky=W, pady=5)
        self.font_family_combo = ttk.Combobox(
            font_frame,
            values=[
                "Consolas",
                "Monaco",
                "Courier New",
                "Menlo",
                "DejaVu Sans Mono",
                "Liberation Mono",
                "Arial",
                "Helvetica",
                "Times New Roman",
                "Georgia",
            ],
            width=20,
        )
        self.font_family_combo.grid(row=0, column=1, sticky=W + E, pady=5, padx=(10, 0))

        ttk.Label(font_frame, text="字体大小:").grid(row=1, column=0, sticky=W, pady=5)
        self.font_size_var = tk.StringVar()
        self.font_size_spin = ttk.Spinbox(
            font_frame, from_=8, to=24, textvariable=self.font_size_var, width=20
        )
        self.font_size_spin.grid(row=1, column=1, sticky=W + E, pady=5, padx=(10, 0))

        # 字体预览
        preview_frame = ttk.Labelframe(
            self.interface_frame, text="字体预览", padding=15
        )
        preview_frame.pack(fill=X, padx=10, pady=10)

        self.font_preview = ttk.Label(
            preview_frame,
            text="Redis TTK Client - 字体预览\nABCDEFGHIJKLMN\n0123456789",
            font=("Consolas", 10),
        )
        self.font_preview.pack()

        # 配置列权重
        theme_frame.columnconfigure(1, weight=1)
        font_frame.columnconfigure(1, weight=1)

        # 绑定字体变化事件
        self.font_family_combo.bind("<<ComboboxSelected>>", self.update_font_preview)
        self.font_size_var.trace_add("write", self.update_font_preview)

    def create_editor_page(self):
        """创建编辑器设置页"""
        self.editor_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.editor_frame, text="编辑器")

        editor_options_frame = ttk.Labelframe(
            self.editor_frame, text="编辑器选项", padding=15
        )
        editor_options_frame.pack(fill=X, padx=10, pady=10)

        # 编辑器选项
        self.auto_save_var = tk.BooleanVar()
        self.auto_save_check = ttk.Checkbutton(
            editor_options_frame, text="自动保存", variable=self.auto_save_var
        )
        self.auto_save_check.pack(anchor=W, pady=5)

        self.auto_refresh_var = tk.BooleanVar()
        self.auto_refresh_check = ttk.Checkbutton(
            editor_options_frame, text="自动刷新", variable=self.auto_refresh_var
        )
        self.auto_refresh_check.pack(anchor=W, pady=5)

        self.show_line_numbers_var = tk.BooleanVar()
        self.show_line_numbers_check = ttk.Checkbutton(
            editor_options_frame, text="显示行号", variable=self.show_line_numbers_var
        )
        self.show_line_numbers_check.pack(anchor=W, pady=5)

        self.word_wrap_var = tk.BooleanVar()
        self.word_wrap_check = ttk.Checkbutton(
            editor_options_frame, text="自动换行", variable=self.word_wrap_var
        )
        self.word_wrap_check.pack(anchor=W, pady=5)

    def create_connection_page(self):
        """创建连接设置页"""
        self.connection_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.connection_frame, text="连接")

        connection_options_frame = ttk.Labelframe(
            self.connection_frame, text="连接选项", padding=15
        )
        connection_options_frame.pack(fill=X, padx=10, pady=10)

        # 连接选项
        self.auto_connect_last_var = tk.BooleanVar()
        self.auto_connect_last_check = ttk.Checkbutton(
            connection_options_frame,
            text="自动连接上次连接",
            variable=self.auto_connect_last_var,
        )
        self.auto_connect_last_check.pack(anchor=W, pady=5)

        # 连接超时
        timeout_frame = ttk.Frame(connection_options_frame)
        timeout_frame.pack(fill=X, pady=5)

        ttk.Label(timeout_frame, text="连接超时(秒):").pack(side=LEFT)
        self.connection_timeout_var = tk.StringVar()
        self.connection_timeout_spin = ttk.Spinbox(
            timeout_frame,
            from_=1.0,
            to=60.0,
            increment=0.5,
            textvariable=self.connection_timeout_var,
            width=10,
        )
        self.connection_timeout_spin.pack(side=LEFT, padx=(10, 0))

        # 最大键显示数量
        max_keys_frame = ttk.Frame(connection_options_frame)
        max_keys_frame.pack(fill=X, pady=5)

        ttk.Label(max_keys_frame, text="最大键显示数量:").pack(side=LEFT)
        self.max_keys_display_var = tk.StringVar()
        self.max_keys_display_spin = ttk.Spinbox(
            max_keys_frame,
            from_=100,
            to=10000,
            increment=100,
            textvariable=self.max_keys_display_var,
            width=10,
        )
        self.max_keys_display_spin.pack(side=LEFT, padx=(10, 0))

    def create_other_page(self):
        """创建其他设置页"""
        self.other_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.other_frame, text="其他")

        other_options_frame = ttk.Labelframe(
            self.other_frame, text="其他选项", padding=15
        )
        other_options_frame.pack(fill=X, padx=10, pady=10)

        # 其他选项
        self.confirm_delete_var = tk.BooleanVar()
        self.confirm_delete_check = ttk.Checkbutton(
            other_options_frame, text="删除时确认", variable=self.confirm_delete_var
        )
        self.confirm_delete_check.pack(anchor=W, pady=5)

        self.show_tooltips_var = tk.BooleanVar()
        self.show_tooltips_check = ttk.Checkbutton(
            other_options_frame, text="显示提示", variable=self.show_tooltips_var
        )
        self.show_tooltips_check.pack(anchor=W, pady=5)

        self.debug_mode_var = tk.BooleanVar()
        self.debug_mode_check = ttk.Checkbutton(
            other_options_frame, text="调试模式", variable=self.debug_mode_var
        )
        self.debug_mode_check.pack(anchor=W, pady=5)

        self.readonly_mode_var = tk.BooleanVar()
        self.readonly_mode_check = ttk.Checkbutton(
            other_options_frame,
            text="只读模式（禁止修改数据库）",
            variable=self.readonly_mode_var,
        )
        self.readonly_mode_check.pack(anchor=W, pady=5)

    def create_import_export_page(self):
        """创建导入导出页"""
        self.import_export_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.import_export_frame, text="导入导出")

        # 导入导出操作
        operations_frame = ttk.Labelframe(
            self.import_export_frame, text="设置管理", padding=15
        )
        operations_frame.pack(fill=X, padx=10, pady=10)

        # 导出设置
        export_frame = ttk.Frame(operations_frame)
        export_frame.pack(fill=X, pady=5)

        ttk.Button(
            export_frame,
            text="导出设置",
            command=self.export_settings,
            bootstyle=PRIMARY,
        ).pack(side=LEFT)

        ttk.Label(export_frame, text="将当前设置导出到文件").pack(
            side=LEFT, padx=(10, 0)
        )

        # 导入设置
        import_frame = ttk.Frame(operations_frame)
        import_frame.pack(fill=X, pady=5)

        ttk.Button(
            import_frame, text="导入设置", command=self.import_settings, bootstyle=INFO
        ).pack(side=LEFT)

        ttk.Label(import_frame, text="从文件导入设置").pack(side=LEFT, padx=(10, 0))

        # 重置设置
        reset_frame = ttk.Frame(operations_frame)
        reset_frame.pack(fill=X, pady=5)

        ttk.Button(
            reset_frame,
            text="重置为默认",
            command=self.reset_to_defaults,
            bootstyle=WARNING,
        ).pack(side=LEFT)

        ttk.Label(reset_frame, text="恢复所有设置为默认值").pack(
            side=LEFT, padx=(10, 0)
        )

    def create_buttons(self):
        """创建按钮区域"""
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=X, padx=10, pady=10)

        # 右侧按钮
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=RIGHT)

        # 取消按钮
        self.cancel_btn = ttk.Button(
            right_buttons, text="取消", command=self.cancel, bootstyle=SECONDARY
        )
        self.cancel_btn.pack(side=RIGHT, padx=(5, 0))

        # 应用按钮
        self.apply_btn = ttk.Button(
            right_buttons, text="应用", command=self.apply_settings, bootstyle=INFO
        )
        self.apply_btn.pack(side=RIGHT, padx=(5, 0))

        # 确定按钮
        self.ok_btn = ttk.Button(
            right_buttons, text="确定", command=self.ok, bootstyle=SUCCESS
        )
        self.ok_btn.pack(side=RIGHT)

        # 左侧重置按钮
        self.reset_btn = ttk.Button(
            button_frame, text="重置", command=self.reset_current, bootstyle=WARNING
        )
        self.reset_btn.pack(side=LEFT)

    def bind_events(self):
        """绑定事件"""
        self.dialog.bind("<Return>", lambda e: self.ok())
        self.dialog.bind("<Escape>", lambda e: self.cancel())

        # 绑定窗口关闭事件
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)

    def load_current_settings(self):
        """加载当前设置到界面"""
        # 界面设置
        self.theme_combo.set(self.settings.get_theme())

        font_family, font_size = self.settings.get_font()
        self.font_family_combo.set(font_family)
        self.font_size_var.set(str(font_size))

        # 编辑器设置
        editor_options = self.settings.get_editor_options()
        self.auto_save_var.set(editor_options["auto_save"])
        self.auto_refresh_var.set(editor_options["auto_refresh"])
        self.show_line_numbers_var.set(editor_options["show_line_numbers"])
        self.word_wrap_var.set(editor_options["word_wrap"])

        # 连接设置
        connection_options = self.settings.get_connection_options()
        self.auto_connect_last_var.set(connection_options["auto_connect_last"])
        self.connection_timeout_var.set(str(connection_options["connection_timeout"]))
        self.max_keys_display_var.set(str(connection_options["max_keys_display"]))

        # 其他设置
        other_options = self.settings.get_other_options()
        self.confirm_delete_var.set(other_options["confirm_delete"])
        self.show_tooltips_var.set(other_options["show_tooltips"])
        self.debug_mode_var.set(other_options["debug_mode"])
        self.readonly_mode_var.set(other_options["readonly_mode"])

        # 更新字体预览
        self.update_font_preview()

    def update_font_preview(self, *args):
        """更新字体预览"""
        try:
            family = self.font_family_combo.get()
            size = int(self.font_size_var.get())
            self.font_preview.config(font=(family, size))
        except (ValueError, tk.TclError):
            pass

    def apply_settings(self):
        """应用设置"""
        try:
            # 应用界面设置
            theme = self.theme_combo.get()
            if theme:
                # 先保存主题设置
                self.settings.set_theme(theme)

            font_family = self.font_family_combo.get()
            font_size = int(self.font_size_var.get())
            if font_family and font_size:
                self.settings.set_font(font_family, font_size)

            # 应用编辑器设置
            self.settings.set_editor_options(
                auto_save=self.auto_save_var.get(),
                auto_refresh=self.auto_refresh_var.get(),
                show_line_numbers=self.show_line_numbers_var.get(),
                word_wrap=self.word_wrap_var.get(),
            )

            # 应用连接设置
            connection_timeout = float(self.connection_timeout_var.get())
            max_keys_display = int(self.max_keys_display_var.get())
            self.settings.set_connection_options(
                auto_connect_last=self.auto_connect_last_var.get(),
                connection_timeout=connection_timeout,
                max_keys_display=max_keys_display,
            )

            # 应用其他设置
            self.settings.set_other_options(
                confirm_delete=self.confirm_delete_var.get(),
                show_tooltips=self.show_tooltips_var.get(),
                debug_mode=self.debug_mode_var.get(),
                readonly_mode=self.readonly_mode_var.get(),
            )

            self.result = True
            showinfo("成功", "设置已应用", parent=self.dialog)

        except ValueError as e:
            showerror("错误", f"设置值无效: {e}", parent=self.dialog)
        except Exception as e:
            showerror("错误", f"应用设置失败: {e}", parent=self.dialog)

    def export_settings(self):
        """导出设置"""
        try:
            file_path = filedialog.asksaveasfilename(
                parent=self.dialog,
                title="导出设置",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )

            if file_path:
                if self.settings.export_settings(file_path):
                    showinfo("成功", f"设置已导出到: {file_path}", parent=self.dialog)
                else:
                    showerror("错误", "导出设置失败", parent=self.dialog)
        except Exception as e:
            showerror("错误", f"导出设置失败: {e}", parent=self.dialog)

    def import_settings(self):
        """导入设置"""
        try:
            file_path = filedialog.askopenfilename(
                parent=self.dialog,
                title="导入设置",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )

            if file_path:
                if self.settings.import_settings(file_path):
                    # 重新加载设置到界面
                    self.load_current_settings()
                    showinfo("成功", f"设置已从 {file_path} 导入", parent=self.dialog)
                else:
                    showerror("错误", "导入设置失败", parent=self.dialog)
        except Exception as e:
            showerror("错误", f"导入设置失败: {e}", parent=self.dialog)

    def reset_to_defaults(self):
        """重置为默认设置"""
        if askyesno("确认", "确定要重置所有设置为默认值吗？", parent=self.dialog):
            try:
                self.settings.reset_to_defaults()
                self.load_current_settings()
                showinfo("成功", "设置已重置为默认值", parent=self.dialog)
            except Exception as e:
                showerror("错误", f"重置设置失败: {e}", parent=self.dialog)

    def reset_current(self):
        """重置当前设置"""
        if askyesno("确认", "确定要恢复到打开对话框时的设置吗？", parent=self.dialog):
            # 恢复原始设置
            self.settings.set_theme(self.original_settings["theme"])
            self.settings.set_font(*self.original_settings["font"])
            self.settings.set_editor_options(**self.original_settings["editor_options"])
            self.settings.set_connection_options(
                **self.original_settings["connection_options"]
            )
            self.settings.set_other_options(**self.original_settings["other_options"])

            # 重新加载界面
            self.load_current_settings()

    def ok(self):
        """确定按钮事件"""
        self.apply_settings()
        if self.result:
            self.dialog.destroy()

    def cancel(self):
        """取消按钮事件"""
        # 恢复原始设置
        self.settings.set_theme(self.original_settings["theme"])
        self.settings.set_font(*self.original_settings["font"])
        self.settings.set_editor_options(**self.original_settings["editor_options"])
        self.settings.set_connection_options(
            **self.original_settings["connection_options"]
        )
        self.settings.set_other_options(**self.original_settings["other_options"])

        self.result = False
        self.dialog.destroy()
