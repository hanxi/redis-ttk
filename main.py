#!/usr/bin/env python3
"""
Redis TTK Client - 主应用程序入口
基于 ttkbootstrap 的现代化 Redis 客户端
"""

import sys
from tkinter import messagebox

import ttkbootstrap as ttk

from gui.main_window import MainWindow


def main():
    """主函数 - 启动应用程序"""
    try:
        # 创建主窗口
        root = ttk.Window(
            title="Redis TTK Client",
            themename="superhero",  # 使用现代化主题
            size=(1200, 800),
            resizable=(True, True),
        )

        # 设置窗口图标和属性
        root.minsize(800, 600)

        # 创建主应用程序
        MainWindow(root)

        # 启动主循环
        root.mainloop()

    except ImportError as e:
        messagebox.showerror(
            "依赖错误", f"缺少必要的依赖包：{e}\n请运行 'pdm install' 安装依赖"
        )
        sys.exit(1)
    except Exception as e:
        messagebox.showerror("启动错误", f"应用程序启动失败：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
