"""
结果显示面板

显示实验运行结果的详细信息。
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import json

from ..models.gui_state import GUIState


class ResultsPanel:
    """
    实验结果显示面板

    显示实验运行结果，包括匹配数、利用率、执行时间等。
    """

    def __init__(self, parent: ttk.Notebook, state: GUIState):
        """
        初始化结果面板

        Args:
            parent: 父容器（Notebook）
            state: 全局GUI状态
        """
        self.state = state

        # 创建主框架
        self.frame = ttk.Frame(parent, padding="10")

        self._create_widgets()

    def _create_widgets(self):
        """创建界面组件"""
        # 标题
        title_label = ttk.Label(
            self.frame,
            text="实验结果",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 10))

        # 关键指标区域
        metrics_frame = ttk.LabelFrame(self.frame, text="关键指标", padding="10")
        metrics_frame.pack(fill=tk.X, pady=(0, 10))

        # 创建指标显示网格
        self.metrics_labels = {}

        metrics = [
            ("num_matches", "匹配数量"),
            ("spectrum_utilization", "频谱利用率"),
            ("execution_time", "执行时间（秒）"),
            ("constraints_satisfied", "约束满足")
        ]

        for i, (key, label) in enumerate(metrics):
            # 标签
            ttk.Label(
                metrics_frame,
                text=f"{label}:",
                font=("Arial", 10)
            ).grid(row=i, column=0, sticky=tk.W, pady=5, padx=5)

            # 值
            value_label = ttk.Label(
                metrics_frame,
                text="--",
                font=("Arial", 10, "bold"),
                foreground="blue"
            )
            value_label.grid(row=i, column=1, sticky=tk.W, pady=5, padx=5)

            self.metrics_labels[key] = value_label

        # 匹配详情区域
        details_frame = ttk.LabelFrame(self.frame, text="匹配详情", padding="10")
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 创建文本框显示详细信息
        text_frame = ttk.Frame(details_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.details_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            height=15,
            state=tk.DISABLED,
            yscrollcommand=scrollbar.set,
            font=("Courier", 9)
        )
        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.details_text.yview)

        # 操作按钮
        action_frame = ttk.Frame(self.frame)
        action_frame.pack(fill=tk.X)

        self.export_button = ttk.Button(
            action_frame,
            text="导出结果...",
            command=self._export_results,
            state=tk.DISABLED
        )
        self.export_button.pack(side=tk.LEFT)

        self.viz_button = ttk.Button(
            action_frame,
            text="查看可视化 →",
            command=self._on_view_viz,
            state=tk.DISABLED
        )
        self.viz_button.pack(side=tk.RIGHT)

        # 占位提示
        self.placeholder_label = ttk.Label(
            self.frame,
            text="暂无实验结果\n\n请先运行实验",
            foreground="gray",
            font=("Arial", 12)
        )
        self.placeholder_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def update_results(self, result: dict):
        """
        更新结果显示

        Args:
            result: 实验结果字典
        """
        # 隐藏占位符
        self.placeholder_label.place_forget()

        # 更新关键指标
        metrics_format = {
            "num_matches": lambda x: str(x),
            "spectrum_utilization": lambda x: f"{x:.2%}",
            "execution_time": lambda x: f"{x:.3f}",
            "constraints_satisfied": lambda x: "是" if x else "否"
        }

        for key, label_widget in self.metrics_labels.items():
            if key in result:
                formatter = metrics_format.get(key, str)
                label_widget.config(text=formatter(result[key]))

                # 根据值设置颜色
                if key == "constraints_satisfied":
                    color = "green" if result[key] else "red"
                    label_widget.config(foreground=color)
                else:
                    label_widget.config(foreground="blue")
            else:
                label_widget.config(text="--", foreground="gray")

        # 更新详细信息
        self._display_details(result)

        # 启用按钮
        self.export_button.config(state=tk.NORMAL)
        self.viz_button.config(state=tk.NORMAL)

    def _display_details(self, result: dict):
        """
        显示详细信息

        Args:
            result: 结果字典
        """
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete("1.0", tk.END)

        lines = []

        lines.append("=" * 60)
        lines.append("实验结果详情")
        lines.append("=" * 60)
        lines.append("")

        # 汇总信息
        lines.append("【汇总信息】")
        lines.append(f"  匹配数量: {result.get('num_matches', 'N/A')}")
        lines.append(f"  频谱利用率: {result.get('spectrum_utilization', 0):.2%}")
        lines.append(f"  执行时间: {result.get('execution_time', 0):.3f} 秒")
        lines.append(f"  约束满足: {'是' if result.get('constraints_satisfied', False) else '否'}")
        lines.append("")

        # 匹配详情
        if "matching" in result:
            lines.append("【匹配详情】")

            matching = result["matching"]
            if isinstance(matching, dict):
                # 字典格式：{user: [channels]}
                for user_id, channels in sorted(matching.items(), key=lambda x: int(x[0])):
                    if channels:
                        channels_str = ", ".join(map(str, channels))
                        lines.append(f"  用户 {user_id}: 信道 [{channels_str}]")
                    else:
                        lines.append(f"  用户 {user_id}: 未分配")
            elif isinstance(matching, list):
                # 列表格式：[(user, channel), ...]
                for user_id, channel_id in matching:
                    lines.append(f"  用户 {user_id} -> 信道 {channel_id}")

            lines.append("")

        # 统计信息
        if "statistics" in result:
            lines.append("【统计信息】")
            stats = result["statistics"]

            for key, value in stats.items():
                lines.append(f"  {key}: {value}")

            lines.append("")

        # 其他信息
        lines.append("【其他信息】")
        for key, value in result.items():
            if key not in ["num_matches", "spectrum_utilization", "execution_time",
                          "constraints_satisfied", "matching", "statistics"]:
                lines.append(f"  {key}: {value}")

        self.details_text.insert("1.0", "\n".join(lines))
        self.details_text.config(state=tk.DISABLED)

    def _export_results(self):
        """导出结果到JSON文件"""
        if not self.state.current_result:
            messagebox.showwarning("警告", "当前没有可导出的结果")
            return

        # 选择保存位置
        file_path = filedialog.asksaveasfilename(
            title="导出结果",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
            initialfile="result.json"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.state.current_result, f, indent=2, ensure_ascii=False)

                messagebox.showinfo("成功", f"结果已导出到:\n{file_path}")

            except Exception as e:
                messagebox.showerror("错误", f"导出失败:\n{e}")

    def _on_view_viz(self):
        """查看可视化按钮点击"""
        # 由主窗口处理（切换标签页）
        pass
