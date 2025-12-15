#!/usr/bin/env python3
"""
GUI主程序入口

启动交互式图形用户界面。
"""

import sys
import tkinter as tk
from pathlib import Path


def main():
    """
    主函数：初始化并启动GUI应用
    """
    # 创建Tkinter根窗口
    root = tk.Tk()
    root.title("认知无线电频谱分配系统 - GUI")

    # 设置窗口大小和位置
    root.geometry("1200x800")

    # 占位符：后续将创建主应用窗口
    label = tk.Label(
        root,
        text="认知无线电频谱分配系统\n\nGUI初始化中...",
        font=("Arial", 16)
    )
    label.pack(expand=True)

    # 启动事件循环
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已退出")
        sys.exit(0)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
