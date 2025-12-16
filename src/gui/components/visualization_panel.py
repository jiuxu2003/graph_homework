"""
可视化面板

使用matplotlib显示实验结果的可视化图表。
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional
import io

from ..models.gui_state import GUIState, UserPreferences


class VisualizationPanel:
    """
    结果可视化面板

    使用matplotlib生成和显示图表。
    """

    def __init__(
        self,
        parent: ttk.Notebook,
        state: GUIState,
        preferences: UserPreferences
    ):
        """
        初始化可视化面板

        Args:
            parent: 父容器（Notebook）
            state: 全局GUI状态
            preferences: 用户偏好设置
        """
        self.state = state
        self.preferences = preferences

        # 创建主框架
        self.frame = ttk.Frame(parent, padding="10")

        # 用于保存当前图表
        self.current_figure = None

        self._create_widgets()

    def _create_widgets(self):
        """创建界面组件"""
        # 标题
        title_label = ttk.Label(
            self.frame,
            text="结果可视化",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 10))

        # 图表类型选择
        control_frame = ttk.Frame(self.frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(control_frame, text="图表类型:").pack(side=tk.LEFT, padx=(0, 5))

        self.chart_type_var = tk.StringVar(value="matching")
        chart_types = [
            ("匹配矩阵", "matching"),
            ("利用率图", "utilization"),
            ("统计汇总", "summary")
        ]

        for text, value in chart_types:
            rb = ttk.Radiobutton(
                control_frame,
                text=text,
                variable=self.chart_type_var,
                value=value,
                command=self._on_chart_type_changed
            )
            rb.pack(side=tk.LEFT, padx=5)

        # 图表显示区域
        self.canvas_frame = ttk.Frame(self.frame, relief=tk.SUNKEN, borderwidth=1)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        # 占位标签
        self.placeholder_label = ttk.Label(
            self.canvas_frame,
            text="暂无可视化数据\n\n请先运行实验",
            foreground="gray",
            font=("Arial", 12)
        )
        self.placeholder_label.pack(expand=True)

        # 操作按钮
        action_frame = ttk.Frame(self.frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))

        self.save_button = ttk.Button(
            action_frame,
            text="保存图表...",
            command=self._save_chart,
            state=tk.DISABLED
        )
        self.save_button.pack(side=tk.LEFT)

        self.refresh_button = ttk.Button(
            action_frame,
            text="刷新",
            command=self._refresh_chart,
            state=tk.DISABLED
        )
        self.refresh_button.pack(side=tk.LEFT, padx=5)

    def update_visualization(self, result: dict):
        """
        更新可视化显示

        Args:
            result: 实验结果字典
        """
        # 保存结果
        self.state.current_result = result

        # 隐藏占位符
        if self.placeholder_label.winfo_exists():
            self.placeholder_label.pack_forget()

        # 生成图表
        self._generate_chart()

        # 启用按钮
        self.save_button.config(state=tk.NORMAL)
        self.refresh_button.config(state=tk.NORMAL)

    def _on_chart_type_changed(self):
        """图表类型改变"""
        if self.state.current_result:
            self._generate_chart()

    def _generate_chart(self):
        """生成图表"""
        if not self.state.current_result:
            return

        try:
            # 导入matplotlib（延迟导入）
            import matplotlib
            matplotlib.use('TkAgg')
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.figure import Figure

            # 配置中文字体支持
            plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

            # 清除旧的画布
            for widget in self.canvas_frame.winfo_children():
                widget.destroy()

            # 创建图表
            fig = Figure(figsize=(8, 6), dpi=self.preferences.viz_dpi)

            chart_type = self.chart_type_var.get()

            if chart_type == "matching":
                self._create_matching_chart(fig)
            elif chart_type == "utilization":
                self._create_utilization_chart(fig)
            elif chart_type == "summary":
                self._create_summary_chart(fig)

            # 保存当前图表
            self.current_figure = fig

            # 创建画布
            canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        except ImportError:
            messagebox.showerror("错误", "matplotlib未安装，无法显示图表")
        except Exception as e:
            messagebox.showerror("错误", f"生成图表失败:\n{e}")

    def _create_matching_chart(self, fig):
        """创建匹配矩阵图"""
        result = self.state.current_result
        config = self.state.current_config

        if not result or "matching" not in result:
            return

        import numpy as np

        # 获取维度（使用CLI格式）
        network = config.get("network", {})
        num_users = network.get("num_secondary_users") or network.get("num_users", 0)
        num_channels = network.get("num_channels", 0)

        if num_users == 0 or num_channels == 0:
            return

        # 创建匹配矩阵
        matrix = np.zeros((num_users, num_channels))

        matching = result["matching"]
        if isinstance(matching, dict):
            for user_id, channels in matching.items():
                user_idx = int(user_id)
                for channel_id in channels:
                    if user_idx < num_users and channel_id < num_channels:
                        matrix[user_idx, channel_id] = 1
        elif isinstance(matching, list):
            for user_id, channel_id in matching:
                if user_id < num_users and channel_id < num_channels:
                    matrix[user_id, channel_id] = 1

        # 绘制热力图
        ax = fig.add_subplot(111)
        im = ax.imshow(matrix, cmap='YlGn', aspect='auto', interpolation='nearest')

        # 设置标签
        ax.set_xlabel('信道 ID')
        ax.set_ylabel('用户 ID')
        ax.set_title(f'匹配矩阵 (匹配数: {result.get("num_matches", 0)})')

        # 设置刻度
        ax.set_xticks(range(num_channels))
        ax.set_yticks(range(num_users))

        # 添加颜色条
        fig.colorbar(im, ax=ax, label='匹配状态')

        fig.tight_layout()

    def _create_utilization_chart(self, fig):
        """创建利用率图"""
        result = self.state.current_result

        if not result:
            return

        # 创建子图
        ax = fig.add_subplot(111)

        utilization = result.get("spectrum_utilization", 0) * 100
        target = 100

        categories = ['频谱利用率', '剩余空间']
        values = [utilization, target - utilization]
        colors = ['#4CAF50', '#E0E0E0']

        bars = ax.barh(categories, values, color=colors)

        # 添加数值标签（避免重叠）
        for i, bar in enumerate(bars):
            width = bar.get_width()
            # 如果值太小（< 5%），不显示标签或显示在右侧
            if width < 5:
                # 值太小时，标签显示在bar右侧
                ax.text(width + 2, bar.get_y() + bar.get_height() / 2,
                       f'{width:.1f}%', ha='left', va='center', fontsize=10, color='gray')
            else:
                # 正常显示在bar中心
                ax.text(width / 2, bar.get_y() + bar.get_height() / 2,
                       f'{width:.1f}%', ha='center', va='center', fontsize=12, fontweight='bold')

        ax.set_xlim(0, target + 10)  # 增加右侧空间以容纳小值标签
        ax.set_xlabel('百分比 (%)')
        ax.set_title(f'频谱利用率: {utilization:.2f}%')

        fig.tight_layout()

    def _create_summary_chart(self, fig):
        """创建统计汇总图"""
        result = self.state.current_result

        if not result:
            return

        # 创建子图
        ax = fig.add_subplot(111)

        # 收集指标
        metrics = {
            '匹配数量': result.get('num_matches', 0),
            '频谱利用率(%)': result.get('spectrum_utilization', 0) * 100,
            '执行时间(秒)': result.get('execution_time', 0),
        }

        categories = list(metrics.keys())
        values = list(metrics.values())

        bars = ax.bar(categories, values, color=['#2196F3', '#4CAF50', '#FF9800'])

        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height,
                   f'{height:.2f}', ha='center', va='bottom', fontsize=10)

        ax.set_ylabel('数值')
        ax.set_title('实验结果汇总')

        # 旋转x轴标签
        ax.set_xticklabels(categories, rotation=15, ha='right')

        fig.tight_layout()

    def _refresh_chart(self):
        """刷新图表"""
        if self.state.current_result:
            self._generate_chart()

    def _save_chart(self):
        """保存图表到文件"""
        if not self.current_figure:
            messagebox.showwarning("警告", "当前没有可保存的图表")
            return

        # 选择保存位置
        file_path = filedialog.asksaveasfilename(
            title="保存图表",
            defaultextension=".png",
            filetypes=[("PNG图片", "*.png"), ("所有文件", "*.*")],
            initialfile="chart.png"
        )

        if file_path:
            try:
                self.current_figure.savefig(
                    file_path,
                    dpi=self.preferences.viz_dpi,
                    bbox_inches='tight'
                )

                messagebox.showinfo("成功", f"图表已保存到:\n{file_path}")

            except Exception as e:
                messagebox.showerror("错误", f"保存失败:\n{e}")
