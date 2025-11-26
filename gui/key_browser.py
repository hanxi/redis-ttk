"""
键浏览器组件
用于显示和管理 Redis 键列表
"""

import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox, simpledialog

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
    VERTICAL,
    WARNING,
    W,
    X,
)


class KeyBrowser:
    """Redis 键浏览器"""

    def __init__(self, parent, on_key_selected: Callable[[str], None]):
        """初始化键浏览器"""
        self.parent = parent
        self.on_key_selected = on_key_selected
        self.keys_data = []
        self.main_window = None  # 将在主窗口中设置
        self.readonly_mode = False  # 只读模式状态

        # 创建主框架
        self.frame = ttk.Frame(parent)

        # 创建界面
        self.create_widgets()

        # 绑定事件
        self.bind_events()

    def set_main_window(self, main_window):
        """设置主窗口引用"""
        self.main_window = main_window

    def create_widgets(self):
        """创建界面组件"""
        # 标题和工具栏
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill=X, padx=5, pady=5)

        # 标题
        title_label = ttk.Label(header_frame, text="键列表", font=("Arial", 12, "bold"))
        title_label.pack(side=LEFT)

        # 搜索框
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill=X, padx=5, pady=(0, 5))

        ttk.Label(search_frame, text="搜索:").pack(side=LEFT)
        self.search_entry = ttk.Entry(search_frame, width=20)
        self.search_entry.pack(side=LEFT, fill=X, expand=True, padx=(5, 0))

        # 绑定搜索事件
        self.search_entry.bind("<KeyRelease>", self.on_search_changed)

        # 键列表框架
        list_frame = ttk.Frame(self.frame)
        list_frame.pack(fill=BOTH, expand=True, padx=5, pady=(0, 5))

        # 创建 Treeview
        columns = ("key", "type", "ttl", "size")
        self.tree = ttk.Treeview(
            list_frame, columns=columns, show="tree headings", height=15
        )

        # 配置列
        self.tree.heading("#0", text="", anchor=W)
        self.tree.column("#0", width=0, stretch=False)

        self.tree.heading("key", text="键名", anchor=W)
        self.tree.column("key", width=200, anchor=W)

        self.tree.heading("type", text="类型", anchor=CENTER)
        self.tree.column("type", width=80, anchor=CENTER)

        self.tree.heading("ttl", text="TTL", anchor=CENTER)
        self.tree.column("ttl", width=80, anchor=CENTER)

        self.tree.heading("size", text="大小", anchor=CENTER)
        self.tree.column("size", width=80, anchor=CENTER)

        # 滚动条
        v_scrollbar = ttk.Scrollbar(
            list_frame, orient=VERTICAL, command=self.tree.yview
        )
        h_scrollbar = ttk.Scrollbar(
            list_frame, orient=HORIZONTAL, command=self.tree.xview
        )
        self.tree.configure(
            yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set
        )

        # 布局
        self.tree.grid(row=0, column=0, sticky=NSEW)
        v_scrollbar.grid(row=0, column=1, sticky=NS)
        h_scrollbar.grid(row=1, column=0, sticky=EW)

        # 配置网格权重
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        # 右键菜单
        self.create_context_menu()

        # 操作按钮框架
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill=X, padx=5, pady=5)

        # 删除按钮
        self.delete_btn = ttk.Button(
            button_frame,
            text="删除键",
            command=self.delete_selected_key,
            bootstyle=DANGER,
            state=DISABLED,
        )
        self.delete_btn.pack(side=LEFT, padx=(0, 5))

        # 重命名按钮
        self.rename_btn = ttk.Button(
            button_frame,
            text="重命名",
            command=self.rename_selected_key,
            bootstyle=WARNING,
            state=DISABLED,
        )
        self.rename_btn.pack(side=LEFT, padx=(0, 5))

        # 设置TTL按钮
        self.ttl_btn = ttk.Button(
            button_frame,
            text="设置TTL",
            command=self.set_key_ttl,
            bootstyle=INFO,
            state=DISABLED,
        )
        self.ttl_btn.pack(side=LEFT)

    def create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = tk.Menu(self.frame, tearoff=0)
        self.context_menu.add_command(label="刷新", command=self.refresh_key_info)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="复制键名", command=self.copy_key_name)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="重命名", command=self.rename_selected_key)
        self.context_menu.add_command(label="设置TTL", command=self.set_key_ttl)
        self.context_menu.add_command(label="移除TTL", command=self.remove_key_ttl)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="删除", command=self.delete_selected_key)

    def bind_events(self):
        """绑定事件"""
        # 选择事件
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # 双击事件
        self.tree.bind("<Double-1>", self.on_tree_double_click)

        # 右键菜单
        self.tree.bind("<Button-3>", self.show_context_menu)  # macOS 使用 Button-2
        self.tree.bind(
            "<Button-2>", self.show_context_menu
        )  # Windows/Linux 使用 Button-3

        # 键盘事件
        self.tree.bind("<Delete>", lambda e: self.delete_selected_key())
        self.tree.bind("<F2>", lambda e: self.rename_selected_key())
        self.tree.bind("<F5>", lambda e: self.refresh_key_info())

    def load_keys(self, keys: list[str]):
        """加载键列表"""
        # 清空现有数据
        self.clear()

        # 存储键数据
        self.keys_data = keys

        # 应用搜索过滤
        self.apply_search_filter()

    def fuzzy_match(self, pattern: str, text: str) -> tuple[bool, int, list[int]]:
        """
        模糊匹配算法，类似 fzf
        返回: (是否匹配, 匹配分数, 匹配位置列表)
        """
        if not pattern:
            return True, 0, []

        pattern = pattern.lower()
        text = text.lower()

        # 如果模式比文本长，肯定不匹配
        if len(pattern) > len(text):
            return False, 0, []

        # 尝试找到所有字符的匹配位置
        match_positions = []
        text_idx = 0

        for char in pattern:
            # 在剩余文本中查找字符
            found_idx = text.find(char, text_idx)
            if found_idx == -1:
                return False, 0, []

            match_positions.append(found_idx)
            text_idx = found_idx + 1

        # 计算匹配分数（分数越高越好）
        score = self._calculate_match_score(pattern, text, match_positions)

        return True, score, match_positions

    def _calculate_match_score(
        self, pattern: str, text: str, positions: list[int]
    ) -> int:
        """计算匹配分数"""
        if not positions:
            return 0

        score = 0

        # 基础分数：匹配的字符数
        score += len(pattern) * 100

        # 连续匹配加分
        consecutive_bonus = 0
        for i in range(1, len(positions)):
            if positions[i] == positions[i - 1] + 1:
                consecutive_bonus += 50
        score += consecutive_bonus

        # 开头匹配加分
        if positions[0] == 0:
            score += 200

        # 单词边界匹配加分（下划线、点、冒号等分隔符后）
        word_boundary_bonus = 0
        for pos in positions:
            if pos > 0 and text[pos - 1] in "_.-:":
                word_boundary_bonus += 30
        score += word_boundary_bonus

        # 匹配密度加分（匹配字符越集中分数越高）
        if len(positions) > 1:
            span = positions[-1] - positions[0] + 1
            density_bonus = max(0, 100 - span)
            score += density_bonus

        # 文本长度惩罚（较短的文本优先）
        length_penalty = len(text)
        score -= length_penalty

        return score

    def apply_search_filter(self):
        """应用搜索过滤"""
        # 清空树视图
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 获取搜索关键词
        search_term = self.search_entry.get().strip()

        if not search_term:
            # 没有搜索词时显示所有键
            for key in self.keys_data:
                self.tree.insert("", "end", values=(key, "...", "...", "..."))
            return

        # 模糊匹配和排序
        matches = []
        for key in self.keys_data:
            is_match, score, positions = self.fuzzy_match(search_term, key)
            if is_match:
                matches.append((key, score, positions))

        # 按分数排序（分数高的在前）
        matches.sort(key=lambda x: x[1], reverse=True)

        # 显示匹配结果
        for key, _score, _positions in matches:
            # 插入键项（暂时不显示详细信息）
            self.tree.insert("", "end", values=(key, "...", "...", "..."))

    def on_search_changed(self, *args):
        """搜索内容变化事件"""
        self.apply_search_filter()

    def on_tree_select(self, event):
        """树选择事件"""
        selection = self.tree.selection()

        if selection:
            # 获取选中的键
            item = selection[0]
            key = self.tree.item(item, "values")[0]

            # 通知键选择事件
            self.on_key_selected(key)

            # 更新控件状态（考虑只读模式）
            self._update_controls_state()
        else:
            # 清空选择
            self.on_key_selected("")

            # 更新控件状态（考虑只读模式）
            self._update_controls_state()

    def on_tree_double_click(self, event):
        """树双击事件"""
        # 双击时聚焦到值编辑器（如果需要的话）
        pass

    def show_context_menu(self, event):
        """显示右键菜单"""
        # 选择点击的项
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def get_selected_key(self) -> str | None:
        """获取选中的键"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            return self.tree.item(item, "values")[0]
        return None

    def select_key(self, key: str):
        """选择指定的键"""
        for item in self.tree.get_children():
            if self.tree.item(item, "values")[0] == key:
                self.tree.selection_set(item)
                self.tree.focus(item)
                self.tree.see(item)
                break

    def update_key_info(self, key: str, key_type: str, ttl: int, size: int | None):
        """更新键的信息显示"""
        for item in self.tree.get_children():
            if self.tree.item(item, "values")[0] == key:
                # 格式化 TTL
                ttl_text = str(ttl) if ttl >= 0 else "永久"

                # 格式化大小
                size_text = self.format_size(size) if size is not None else "N/A"

                # 更新显示
                self.tree.item(item, values=(key, key_type, ttl_text, size_text))
                break

    def format_size(self, size_bytes: int) -> str:
        """格式化大小显示"""
        if size_bytes < 1024:
            return f"{size_bytes}B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f}KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f}MB"

    def refresh_key_info(self):
        """刷新选中键的信息"""
        selected_key = self.get_selected_key()
        if selected_key:
            # 触发重新选择以刷新信息
            self.on_key_selected(selected_key)

    def copy_key_name(self):
        """复制键名到剪贴板"""
        selected_key = self.get_selected_key()
        if selected_key:
            self.frame.clipboard_clear()
            self.frame.clipboard_append(selected_key)
            messagebox.showinfo("成功", f"已复制键名: {selected_key}")

    def delete_selected_key(self):
        """删除选中的键"""
        selected_key = self.get_selected_key()
        if not selected_key:
            return

        if messagebox.askyesno("确认删除", f"确定要删除键 '{selected_key}' 吗？"):
            if self.main_window:
                self.main_window.delete_key(selected_key)

    def rename_selected_key(self):
        """重命名选中的键"""
        selected_key = self.get_selected_key()
        if not selected_key:
            return

        new_name = simpledialog.askstring(
            "重命名键", "请输入新的键名:", initialvalue=selected_key
        )

        if new_name and new_name != selected_key:
            if self.main_window:
                self.main_window.rename_key(selected_key, new_name)

    def set_key_ttl(self):
        """设置键的TTL"""
        selected_key = self.get_selected_key()
        if not selected_key:
            return

        ttl_str = simpledialog.askstring(
            "设置TTL", f"请输入键 '{selected_key}' 的过期时间（秒）:"
        )

        if ttl_str:
            try:
                ttl = int(ttl_str)
                if ttl > 0:
                    if self.main_window:
                        self.main_window.set_key_ttl(selected_key, ttl)
                else:
                    messagebox.showerror("错误", "TTL必须大于0")
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字")

    def remove_key_ttl(self):
        """移除键的TTL"""
        selected_key = self.get_selected_key()
        if not selected_key:
            return

        if messagebox.askyesno("确认", f"确定要移除键 '{selected_key}' 的过期时间吗？"):
            if self.main_window:
                self.main_window.remove_key_ttl(selected_key)

    def clear(self):
        """清空键列表"""
        # 清空树视图
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 清空数据
        self.keys_data = []

        # 清空搜索
        self.search_entry.delete(0, tk.END)

        # 禁用按钮
        self.delete_btn.config(state=DISABLED)
        self.rename_btn.config(state=DISABLED)
        self.ttl_btn.config(state=DISABLED)

    def set_readonly_mode(self, readonly: bool):
        """设置只读模式"""
        self.readonly_mode = readonly

        # 根据只读模式状态更新按钮和菜单
        self._update_controls_state()

    def _update_controls_state(self):
        """更新控件状态"""
        if self.readonly_mode:
            # 只读模式下禁用所有修改操作
            self.delete_btn.config(state=DISABLED)
            self.rename_btn.config(state=DISABLED)
            self.ttl_btn.config(state=DISABLED)

            # 更新右键菜单状态
            self.context_menu.entryconfig("重命名", state="disabled")
            self.context_menu.entryconfig("设置TTL", state="disabled")
            self.context_menu.entryconfig("移除TTL", state="disabled")
            self.context_menu.entryconfig("删除", state="disabled")
        else:
            # 非只读模式下，根据是否有选中项来决定按钮状态
            selection = self.tree.selection()
            if selection:
                self.delete_btn.config(state=NORMAL)
                self.rename_btn.config(state=NORMAL)
                self.ttl_btn.config(state=NORMAL)
            else:
                self.delete_btn.config(state=DISABLED)
                self.rename_btn.config(state=DISABLED)
                self.ttl_btn.config(state=DISABLED)

            # 启用右键菜单
            self.context_menu.entryconfig("重命名", state="normal")
            self.context_menu.entryconfig("设置TTL", state="normal")
            self.context_menu.entryconfig("移除TTL", state="normal")
            self.context_menu.entryconfig("删除", state="normal")
