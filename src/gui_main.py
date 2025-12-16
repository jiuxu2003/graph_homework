#!/usr/bin/env python3
"""
GUI主程序入口

启动交互式图形用户界面。
"""

import sys
import tkinter as tk
from pathlib import Path

# 确保能导入src模块
sys.path.insert(0, str(Path(__file__).parent))

from gui.components.main_window import MainWindow


def main():
    """
    主函数：初始化并启动GUI应用
    """
    try:
        # 创建Tkinter根窗口
        root = tk.Tk()

        # 创建主应用窗口
        app = MainWindow(root)

        # 启动事件循环
        app.run()

    except ImportError as e:
        # 如果导入失败，显示错误信息
        root = tk.Tk()
        root.title("错误")
        root.geometry("400x200")

        error_label = tk.Label(
            root,
            text=f"导入模块失败:\n\n{e}\n\n请检查依赖是否已安装",
            font=("Arial", 10),
            fg="red",
            wraplength=350
        )
        error_label.pack(expand=True)

        root.mainloop()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已退出")
        sys.exit(0)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
