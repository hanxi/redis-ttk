"""
值编辑器组件
用于显示和编辑 Redis 键值
"""

import json
import tkinter as tk
from collections.abc import Callable
from typing import Any

import ttkbootstrap as ttk
from ttkbootstrap.constants import (
    BOTH,
    CENTER,
    DANGER,
    DISABLED,
    EW,
    HORIZONTAL,
    INFO,
    LEFT,
    NORMAL,
    NS,
    NSEW,
    PRIMARY,
    SECONDARY,
    SUCCESS,
    VERTICAL,
    WARNING,
    W,
    X,
)

from gui.custom_dialogs import askstring, showerror, showwarning


class ValueEditor:
    """Redis 值编辑器"""

    def __init__(self, parent, on_value_changed: Callable[[str, Any, str], None]):
        """初始化值编辑器"""
        self.parent = parent
        self.on_value_changed = on_value_changed
        self.on_refresh_callback = None  # 刷新回调函数
        self.current_key = ""
        self.current_key_info = {}
        self.current_value = None
        self.current_type = "string"
        self.readonly_mode = False

        # 创建主框架
        self.frame = ttk.Frame(parent)

        # 创建界面
        self.create_widgets()

        # 绑定事件
        self.bind_events()

    def create_widgets(self):
        """创建界面组件"""
        # 标题框架
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill=X, padx=5, pady=5)

        # 标题
        title_label = ttk.Label(
            header_frame, text="值编辑器", font=("Arial", 12, "bold")
        )
        title_label.pack(side=LEFT)

        # 键信息框架
        info_frame = ttk.Labelframe(self.frame, text="键信息", padding=10)
        info_frame.pack(fill=X, padx=5, pady=(0, 5))

        # 键名
        key_frame = ttk.Frame(info_frame)
        key_frame.pack(fill=X, pady=2)
        ttk.Label(key_frame, text="键名:", width=8).pack(side=LEFT)
        self.key_label = ttk.Label(key_frame, text="", foreground="blue")
        self.key_label.pack(side=LEFT, fill=X, expand=True)

        # 类型和TTL
        type_ttl_frame = ttk.Frame(info_frame)
        type_ttl_frame.pack(fill=X, pady=2)

        ttk.Label(type_ttl_frame, text="类型:", width=8).pack(side=LEFT)
        self.type_label = ttk.Label(type_ttl_frame, text="", width=10)
        self.type_label.pack(side=LEFT)

        ttk.Label(type_ttl_frame, text="TTL:", width=8).pack(side=LEFT, padx=(20, 0))
        self.ttl_label = ttk.Label(type_ttl_frame, text="", width=10)
        self.ttl_label.pack(side=LEFT)

        ttk.Label(type_ttl_frame, text="大小:", width=8).pack(side=LEFT, padx=(20, 0))
        self.size_label = ttk.Label(type_ttl_frame, text="", width=10)
        self.size_label.pack(side=LEFT)

        # 值编辑区域
        self.create_value_editor()

        # 操作按钮框架
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill=X, padx=5, pady=5)

        # 保存按钮
        self.save_btn = ttk.Button(
            button_frame,
            text="保存",
            command=self.save_value,
            bootstyle=SUCCESS,
            state=DISABLED,
        )
        self.save_btn.pack(side=LEFT, padx=(0, 5))

        # 刷新按钮
        self.refresh_btn = ttk.Button(
            button_frame,
            text="刷新",
            command=self.refresh_value,
            bootstyle=INFO,
            state=DISABLED,
        )
        self.refresh_btn.pack(side=LEFT, padx=(0, 5))

        # 只读模式提示
        self.readonly_warning = ttk.Label(
            button_frame, text="只读模式 - 无法修改数据", bootstyle=WARNING
        )
        # 初始时隐藏
        self.refresh_btn.pack(side=LEFT, padx=(0, 5))

        # 格式化按钮（仅对JSON有效）
        self.format_btn = ttk.Button(
            button_frame,
            text="格式化JSON",
            command=self.format_json,
            bootstyle=SECONDARY,
            state=DISABLED,
        )
        self.format_btn.pack(side=LEFT)

    def create_value_editor(self):
        """创建值编辑区域"""
        # 值编辑框架
        editor_frame = ttk.Labelframe(self.frame, text="值内容", padding=5)
        editor_frame.pack(fill=BOTH, expand=True, padx=5, pady=(0, 5))

        # 创建 Notebook 用于不同类型的编辑器
        self.notebook = ttk.Notebook(editor_frame)
        self.notebook.pack(fill=BOTH, expand=True)

        # 字符串编辑器
        self.create_string_editor()

        # 列表编辑器
        self.create_list_editor()

        # 集合编辑器
        self.create_set_editor()

        # 有序集合编辑器
        self.create_zset_editor()

        # 哈希编辑器
        self.create_hash_editor()

    def create_string_editor(self):
        """创建字符串编辑器"""
        self.string_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.string_frame, text="字符串")

        # 文本编辑区
        text_frame = ttk.Frame(self.string_frame)
        text_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)

        self.string_text = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))

        # 滚动条
        string_scrollbar_v = ttk.Scrollbar(
            text_frame, orient=VERTICAL, command=self.string_text.yview
        )
        string_scrollbar_h = ttk.Scrollbar(
            text_frame, orient=HORIZONTAL, command=self.string_text.xview
        )
        self.string_text.configure(
            yscrollcommand=string_scrollbar_v.set, xscrollcommand=string_scrollbar_h.set
        )

        # 布局
        self.string_text.grid(row=0, column=0, sticky=NSEW)
        string_scrollbar_v.grid(row=0, column=1, sticky=NS)
        string_scrollbar_h.grid(row=1, column=0, sticky=EW)

        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

    def create_list_editor(self):
        """创建列表编辑器"""
        self.list_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.list_frame, text="列表")

        # 工具栏
        list_toolbar = ttk.Frame(self.list_frame)
        list_toolbar.pack(fill=X, padx=5, pady=5)

        ttk.Button(
            list_toolbar, text="添加", command=self.add_list_item, bootstyle=PRIMARY
        ).pack(side=LEFT, padx=(0, 5))
        ttk.Button(
            list_toolbar, text="删除", command=self.delete_list_item, bootstyle=DANGER
        ).pack(side=LEFT, padx=(0, 5))
        ttk.Button(
            list_toolbar, text="编辑", command=self.edit_list_item, bootstyle=WARNING
        ).pack(side=LEFT)

        # 列表视图
        list_view_frame = ttk.Frame(self.list_frame)
        list_view_frame.pack(fill=BOTH, expand=True, padx=5, pady=(0, 5))

        self.list_tree = ttk.Treeview(
            list_view_frame, columns=("index", "value"), show="headings", height=10
        )
        self.list_tree.heading("index", text="索引")
        self.list_tree.heading("value", text="值")
        self.list_tree.column("index", width=80, anchor=CENTER)
        self.list_tree.column("value", width=300, anchor=W)

        list_scrollbar = ttk.Scrollbar(
            list_view_frame, orient=VERTICAL, command=self.list_tree.yview
        )
        self.list_tree.configure(yscrollcommand=list_scrollbar.set)

        self.list_tree.grid(row=0, column=0, sticky=NSEW)
        list_scrollbar.grid(row=0, column=1, sticky=NS)

        list_view_frame.grid_rowconfigure(0, weight=1)
        list_view_frame.grid_columnconfigure(0, weight=1)

    def create_set_editor(self):
        """创建集合编辑器"""
        self.set_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.set_frame, text="集合")

        # 工具栏
        set_toolbar = ttk.Frame(self.set_frame)
        set_toolbar.pack(fill=X, padx=5, pady=5)

        ttk.Button(
            set_toolbar, text="添加", command=self.add_set_member, bootstyle=PRIMARY
        ).pack(side=LEFT, padx=(0, 5))
        ttk.Button(
            set_toolbar, text="删除", command=self.delete_set_member, bootstyle=DANGER
        ).pack(side=LEFT)

        # 集合视图
        set_view_frame = ttk.Frame(self.set_frame)
        set_view_frame.pack(fill=BOTH, expand=True, padx=5, pady=(0, 5))

        self.set_tree = ttk.Treeview(
            set_view_frame, columns=("member",), show="headings", height=10
        )
        self.set_tree.heading("member", text="成员")
        self.set_tree.column("member", width=400, anchor=W)

        set_scrollbar = ttk.Scrollbar(
            set_view_frame, orient=VERTICAL, command=self.set_tree.yview
        )
        self.set_tree.configure(yscrollcommand=set_scrollbar.set)

        self.set_tree.grid(row=0, column=0, sticky=NSEW)
        set_scrollbar.grid(row=0, column=1, sticky=NS)

        set_view_frame.grid_rowconfigure(0, weight=1)
        set_view_frame.grid_columnconfigure(0, weight=1)

    def create_zset_editor(self):
        """创建有序集合编辑器"""
        self.zset_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.zset_frame, text="有序集合")

        # 工具栏
        zset_toolbar = ttk.Frame(self.zset_frame)
        zset_toolbar.pack(fill=X, padx=5, pady=5)

        ttk.Button(
            zset_toolbar, text="添加", command=self.add_zset_member, bootstyle=PRIMARY
        ).pack(side=LEFT, padx=(0, 5))
        ttk.Button(
            zset_toolbar, text="删除", command=self.delete_zset_member, bootstyle=DANGER
        ).pack(side=LEFT, padx=(0, 5))
        ttk.Button(
            zset_toolbar, text="编辑", command=self.edit_zset_member, bootstyle=WARNING
        ).pack(side=LEFT)

        # 有序集合视图
        zset_view_frame = ttk.Frame(self.zset_frame)
        zset_view_frame.pack(fill=BOTH, expand=True, padx=5, pady=(0, 5))

        self.zset_tree = ttk.Treeview(
            zset_view_frame, columns=("member", "score"), show="headings", height=10
        )
        self.zset_tree.heading("member", text="成员")
        self.zset_tree.heading("score", text="分数")
        self.zset_tree.column("member", width=300, anchor=W)
        self.zset_tree.column("score", width=100, anchor=CENTER)

        zset_scrollbar = ttk.Scrollbar(
            zset_view_frame, orient=VERTICAL, command=self.zset_tree.yview
        )
        self.zset_tree.configure(yscrollcommand=zset_scrollbar.set)

        self.zset_tree.grid(row=0, column=0, sticky=NSEW)
        zset_scrollbar.grid(row=0, column=1, sticky=NS)

        zset_view_frame.grid_rowconfigure(0, weight=1)
        zset_view_frame.grid_columnconfigure(0, weight=1)

    def create_hash_editor(self):
        """创建哈希编辑器"""
        self.hash_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.hash_frame, text="哈希")

        # 工具栏
        hash_toolbar = ttk.Frame(self.hash_frame)
        hash_toolbar.pack(fill=X, padx=5, pady=5)

        ttk.Button(
            hash_toolbar, text="添加", command=self.add_hash_field, bootstyle=PRIMARY
        ).pack(side=LEFT, padx=(0, 5))
        ttk.Button(
            hash_toolbar, text="删除", command=self.delete_hash_field, bootstyle=DANGER
        ).pack(side=LEFT, padx=(0, 5))
        ttk.Button(
            hash_toolbar, text="编辑", command=self.edit_hash_field, bootstyle=WARNING
        ).pack(side=LEFT)

        # 哈希视图
        hash_view_frame = ttk.Frame(self.hash_frame)
        hash_view_frame.pack(fill=BOTH, expand=True, padx=5, pady=(0, 5))

        self.hash_tree = ttk.Treeview(
            hash_view_frame, columns=("field", "value"), show="headings", height=10
        )
        self.hash_tree.heading("field", text="字段")
        self.hash_tree.heading("value", text="值")
        self.hash_tree.column("field", width=150, anchor=W)
        self.hash_tree.column("value", width=250, anchor=W)

        hash_scrollbar = ttk.Scrollbar(
            hash_view_frame, orient=VERTICAL, command=self.hash_tree.yview
        )
        self.hash_tree.configure(yscrollcommand=hash_scrollbar.set)

        self.hash_tree.grid(row=0, column=0, sticky=NSEW)
        hash_scrollbar.grid(row=0, column=1, sticky=NS)

        hash_view_frame.grid_rowconfigure(0, weight=1)
        hash_view_frame.grid_columnconfigure(0, weight=1)

    def bind_events(self):
        """绑定事件"""
        # 文本变化事件
        self.string_text.bind("<KeyRelease>", self.on_text_changed)
        self.string_text.bind("<Button-1>", self.on_text_changed)

        # 双击编辑事件
        self.list_tree.bind("<Double-1>", lambda e: self.edit_list_item())
        self.zset_tree.bind("<Double-1>", lambda e: self.edit_zset_member())
        self.hash_tree.bind("<Double-1>", lambda e: self.edit_hash_field())

    def on_text_changed(self, event=None):
        """文本变化事件"""
        if self.current_key:
            self.save_btn.config(state=NORMAL)

    def load_key_value(self, key: str, key_info: dict[str, Any], value: Any):
        """加载键值数据"""
        self.current_key = key
        self.current_key_info = key_info
        self.current_value = value
        self.current_type = key_info.get("type", "string")

        # 更新键信息显示
        self.update_key_info_display()

        # 根据类型切换到相应的编辑器
        self.switch_editor_by_type()

        # 加载值到编辑器
        self.load_value_to_editor()

        # 启用按钮
        self.save_btn.config(state=NORMAL)
        self.refresh_btn.config(state=NORMAL)

    def update_key_info_display(self):
        """更新键信息显示"""
        self.key_label.config(text=self.current_key)
        self.type_label.config(text=self.current_type)

        ttl = self.current_key_info.get("ttl", -1)
        ttl_text = str(ttl) if ttl >= 0 else "永久"
        self.ttl_label.config(text=ttl_text)

        size = self.current_key_info.get("size")
        size_text = self.format_size(size) if size is not None else "N/A"
        self.size_label.config(text=size_text)

    def format_size(self, size_bytes: int) -> str:
        """格式化大小显示"""
        if size_bytes < 1024:
            return f"{size_bytes}B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f}KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f}MB"

    def switch_editor_by_type(self):
        """根据类型切换编辑器"""
        type_to_tab = {"string": 0, "list": 1, "set": 2, "zset": 3, "hash": 4}

        tab_index = type_to_tab.get(self.current_type, 0)
        self.notebook.select(tab_index)

        # 更新格式化按钮状态
        if self.current_type == "string":
            self.format_btn.config(state=NORMAL)
        else:
            self.format_btn.config(state=DISABLED)

    def load_value_to_editor(self):
        """加载值到编辑器"""
        if self.current_type == "string":
            self.load_string_value()
        elif self.current_type == "list":
            self.load_list_value()
        elif self.current_type == "set":
            self.load_set_value()
        elif self.current_type == "zset":
            self.load_zset_value()
        elif self.current_type == "hash":
            self.load_hash_value()

    def load_string_value(self):
        """加载字符串值"""
        self.string_text.delete(1.0, tk.END)
        if self.current_value is not None:
            self.string_text.insert(1.0, str(self.current_value))

    def load_list_value(self):
        """加载列表值"""
        # 清空现有数据
        for item in self.list_tree.get_children():
            self.list_tree.delete(item)

        # 加载列表数据
        if isinstance(self.current_value, list):
            for i, value in enumerate(self.current_value):
                self.list_tree.insert("", "end", values=(i, str(value)))

    def load_set_value(self):
        """加载集合值"""
        # 清空现有数据
        for item in self.set_tree.get_children():
            self.set_tree.delete(item)

        # 加载集合数据
        if isinstance(self.current_value, (list, set)):
            for member in self.current_value:
                self.set_tree.insert("", "end", values=(str(member),))

    def load_zset_value(self):
        """加载有序集合值"""
        # 清空现有数据
        for item in self.zset_tree.get_children():
            self.zset_tree.delete(item)

        # 加载有序集合数据
        if isinstance(self.current_value, list):
            for member, score in self.current_value:
                self.zset_tree.insert("", "end", values=(str(member), str(score)))

    def load_hash_value(self):
        """加载哈希值"""
        # 清空现有数据
        for item in self.hash_tree.get_children():
            self.hash_tree.delete(item)

        # 加载哈希数据
        if isinstance(self.current_value, dict):
            for field, value in self.current_value.items():
                self.hash_tree.insert("", "end", values=(str(field), str(value)))

    def save_value(self):
        """保存值"""
        if not self.current_key:
            return

        # 检查只读模式
        if self.readonly_mode:
            showwarning("只读模式", "当前处于只读模式，无法保存数据")
            return

        try:
            # 根据类型获取值
            new_value = self.get_value_from_editor()

            # 通知主窗口保存
            self.on_value_changed(self.current_key, new_value, self.current_type)

            # 禁用保存按钮
            self.save_btn.config(state=DISABLED)

        except Exception as e:
            showerror("错误", f"保存失败: {e}")

    def get_value_from_editor(self) -> Any:
        """从编辑器获取值"""
        if self.current_type == "string":
            return self.string_text.get(1.0, tk.END).rstrip("\n")
        elif self.current_type == "list":
            return [
                self.list_tree.item(item, "values")[1]
                for item in self.list_tree.get_children()
            ]
        elif self.current_type == "set":
            return [
                self.set_tree.item(item, "values")[0]
                for item in self.set_tree.get_children()
            ]
        elif self.current_type == "zset":
            result = []
            for item in self.zset_tree.get_children():
                values = self.zset_tree.item(item, "values")
                result.append((values[0], float(values[1])))
            return result
        elif self.current_type == "hash":
            result = {}
            for item in self.hash_tree.get_children():
                values = self.hash_tree.item(item, "values")
                result[values[0]] = values[1]
            return result

        return None

    def refresh_value(self):
        """刷新值"""
        # 通过回调函数重新加载当前键的数据
        if self.current_key and self.on_refresh_callback:
            try:
                self.on_refresh_callback(self.current_key)
            except Exception as e:
                showerror("错误", f"刷新失败: {e}")
        elif self.current_key:
            showwarning("提示", "刷新功能暂不可用")

    def format_json(self):
        """格式化JSON"""
        if self.current_type != "string":
            return

        try:
            # 获取当前文本
            text = self.string_text.get(1.0, tk.END).strip()

            # 尝试解析JSON
            parsed = json.loads(text)

            # 格式化JSON
            formatted = json.dumps(parsed, indent=2, ensure_ascii=False)

            # 更新文本
            self.string_text.delete(1.0, tk.END)
            self.string_text.insert(1.0, formatted)

            # 启用保存按钮
            self.save_btn.config(state=NORMAL)

        except json.JSONDecodeError as e:
            showerror("错误", f"JSON格式错误: {e}")
        except Exception as e:
            showerror("错误", f"格式化失败: {e}")

    # 列表操作方法
    def add_list_item(self):
        """添加列表项"""
        value = askstring("添加列表项", "请输入值:")
        if value is not None:
            index = len(self.list_tree.get_children())
            self.list_tree.insert("", "end", values=(index, value))
            self.save_btn.config(state=NORMAL)

    def delete_list_item(self):
        """删除列表项"""
        selection = self.list_tree.selection()
        if selection:
            self.list_tree.delete(selection[0])
            self.update_list_indices()
            self.save_btn.config(state=NORMAL)

    def edit_list_item(self):
        """编辑列表项"""
        selection = self.list_tree.selection()
        if selection:
            item = selection[0]
            current_value = self.list_tree.item(item, "values")[1]
            new_value = askstring(
                "编辑列表项", "请输入新值:", initialvalue=current_value
            )
            if new_value is not None:
                index = self.list_tree.item(item, "values")[0]
                self.list_tree.item(item, values=(index, new_value))
                self.save_btn.config(state=NORMAL)

    def update_list_indices(self):
        """更新列表索引"""
        for i, item in enumerate(self.list_tree.get_children()):
            current_values = list(self.list_tree.item(item, "values"))
            current_values[0] = i
            self.list_tree.item(item, values=current_values)

    # 集合操作方法
    def add_set_member(self):
        """添加集合成员"""
        member = askstring("添加集合成员", "请输入成员:")
        if member is not None:
            # 检查是否已存在
            for item in self.set_tree.get_children():
                if self.set_tree.item(item, "values")[0] == member:
                    showwarning("警告", "成员已存在")
                    return

            self.set_tree.insert("", "end", values=(member,))
            self.save_btn.config(state=NORMAL)

    def delete_set_member(self):
        """删除集合成员"""
        selection = self.set_tree.selection()
        if selection:
            self.set_tree.delete(selection[0])
            self.save_btn.config(state=NORMAL)

    # 有序集合操作方法
    def add_zset_member(self):
        """添加有序集合成员"""
        member = askstring("添加有序集合成员", "请输入成员:")
        if member is not None:
            score_str = askstring("设置分数", "请输入分数:")
            if score_str is not None:
                try:
                    score = float(score_str)
                    self.zset_tree.insert("", "end", values=(member, score))
                    self.save_btn.config(state=NORMAL)
                except ValueError:
                    showerror("错误", "分数必须是数字")

    def delete_zset_member(self):
        """删除有序集合成员"""
        selection = self.zset_tree.selection()
        if selection:
            self.zset_tree.delete(selection[0])
            self.save_btn.config(state=NORMAL)

    def edit_zset_member(self):
        """编辑有序集合成员"""
        selection = self.zset_tree.selection()
        if selection:
            item = selection[0]
            current_values = self.zset_tree.item(item, "values")
            current_member = current_values[0]
            current_score = current_values[1]

            new_member = askstring(
                "编辑成员", "请输入成员:", initialvalue=current_member
            )
            if new_member is not None:
                new_score_str = askstring(
                    "编辑分数", "请输入分数:", initialvalue=str(current_score)
                )
                if new_score_str is not None:
                    try:
                        new_score = float(new_score_str)
                        self.zset_tree.item(item, values=(new_member, new_score))
                        self.save_btn.config(state=NORMAL)
                    except ValueError:
                        showerror("错误", "分数必须是数字")

    # 哈希操作方法
    def add_hash_field(self):
        """添加哈希字段"""
        field = askstring("添加哈希字段", "请输入字段名:")
        if field is not None:
            # 检查是否已存在
            for item in self.hash_tree.get_children():
                if self.hash_tree.item(item, "values")[0] == field:
                    showwarning("警告", "字段已存在")
                    return

            value = askstring("设置值", "请输入值:")
            if value is not None:
                self.hash_tree.insert("", "end", values=(field, value))
                self.save_btn.config(state=NORMAL)

    def delete_hash_field(self):
        """删除哈希字段"""
        selection = self.hash_tree.selection()
        if selection:
            self.hash_tree.delete(selection[0])
            self.save_btn.config(state=NORMAL)

    def edit_hash_field(self):
        """编辑哈希字段"""
        selection = self.hash_tree.selection()
        if selection:
            item = selection[0]
            current_values = self.hash_tree.item(item, "values")
            current_field = current_values[0]
            current_value = current_values[1]

            new_field = askstring(
                "编辑字段", "请输入字段名:", initialvalue=current_field
            )
            if new_field is not None:
                new_value = askstring("编辑值", "请输入值:", initialvalue=current_value)
                if new_value is not None:
                    self.hash_tree.item(item, values=(new_field, new_value))
                    self.save_btn.config(state=NORMAL)

    def clear(self):
        """清空编辑器"""
        self.current_key = ""
        self.current_key_info = {}
        self.current_value = None
        self.current_type = "string"

        # 清空显示
        self.key_label.config(text="")
        self.type_label.config(text="")
        self.ttl_label.config(text="")
        self.size_label.config(text="")

        # 清空编辑器
        self.string_text.delete(1.0, tk.END)

        for item in self.list_tree.get_children():
            self.list_tree.delete(item)

        for item in self.set_tree.get_children():
            self.set_tree.delete(item)

        for item in self.zset_tree.get_children():
            self.zset_tree.delete(item)

        for item in self.hash_tree.get_children():
            self.hash_tree.delete(item)

        # 禁用按钮
        self.save_btn.config(state=DISABLED)
        self.refresh_btn.config(state=DISABLED)
        self.format_btn.config(state=DISABLED)

    def set_refresh_callback(self, callback: Callable[[str], None]):
        """设置刷新回调函数"""
        self.on_refresh_callback = callback

    def set_readonly_mode(self, readonly: bool):
        """设置只读模式"""
        self.readonly_mode = readonly

        if readonly:
            # 显示只读模式警告
            self.readonly_warning.pack(side=tk.LEFT, padx=(10, 0))

            # 禁用所有编辑功能
            self._disable_editors()

        else:
            # 隐藏只读模式警告
            self.readonly_warning.pack_forget()

            # 启用编辑功能（如果有键被选中）
            if self.current_key:
                self._enable_editors()

    def _disable_editors(self):
        """禁用所有编辑器"""
        # 禁用保存按钮
        self.save_btn.config(state=tk.DISABLED)

        # 禁用文本编辑器
        self.string_text.config(state=tk.DISABLED)

        # 禁用格式化按钮
        self.format_btn.config(state=tk.DISABLED)

        # 禁用所有编辑操作的方法（通过重写方法为空操作）
        self._original_methods = {}

        # 保存原始方法并替换为空操作
        edit_methods = [
            "add_list_item",
            "delete_list_item",
            "edit_list_item",
            "add_set_member",
            "delete_set_member",
            "add_zset_member",
            "delete_zset_member",
            "edit_zset_member",
            "add_hash_field",
            "delete_hash_field",
            "edit_hash_field",
        ]

        for method_name in edit_methods:
            if hasattr(self, method_name):
                self._original_methods[method_name] = getattr(self, method_name)
                setattr(self, method_name, self._readonly_warning)

    def _enable_editors(self):
        """启用所有编辑器"""
        if not self.readonly_mode:
            # 启用保存按钮（如果有键被选中）
            if self.current_key:
                self.save_btn.config(state=tk.NORMAL)

            # 启用文本编辑器
            self.string_text.config(state=tk.NORMAL)

            # 启用格式化按钮
            if self.current_type == "string":
                self.format_btn.config(state=tk.NORMAL)

            # 恢复原始编辑方法
            if hasattr(self, "_original_methods"):
                for method_name, original_method in self._original_methods.items():
                    setattr(self, method_name, original_method)
                delattr(self, "_original_methods")

    def _readonly_warning(self):
        """只读模式警告"""
        showwarning("只读模式", "当前处于只读模式，无法执行此操作")
