"""
性能指标可视化模块

用于绘制批量实验的性能指标对比图
"""

import os
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Optional

from ..models import BatchExperimentResults, ExperimentResult

# 配置matplotlib支持中文显示
# 获取项目根目录
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_FONT_PATH = os.path.join(_PROJECT_ROOT, 'fonts', 'SourceHanSansSC-Regular.otf')

# 如果思源黑体字体文件存在，注册并使用它
if os.path.exists(_FONT_PATH):
    from matplotlib.font_manager import fontManager
    fontManager.addfont(_FONT_PATH)
    plt.rcParams['font.sans-serif'] = ['Source Han Sans SC', 'DejaVu Sans', 'sans-serif']
else:
    # 回退到系统字体
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'sans-serif']

plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


class MetricsPlotter:
    """性能指标绘制器"""

    def __init__(self, batch_results: BatchExperimentResults):
        """
        初始化绘制器

        参数:
            batch_results: 批量实验结果
        """
        self.batch_results = batch_results

    def plot_comparison(self, save_path: Optional[str] = None, show: bool = True) -> None:
        """
        绘制多个实验的性能指标对比图

        参数:
            save_path: 保存路径（可选）
            show: 是否显示图形
        """
        experiments = [e for e in self.batch_results.experiments if e.success]

        if len(experiments) == 0:
            print("警告: 没有成功的实验结果，无法绘制对比图")
            return

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # 提取数据
        names = [e.config.name for e in experiments]
        num_matches = [e.matching_result.num_matches for e in experiments]
        utilization = [e.matching_result.spectrum_utilization * 100 for e in experiments]
        exec_time = [e.matching_result.execution_time * 1000 for e in experiments]  # 转换为毫秒
        matched_users = [len(e.matching_result.matched_users) for e in experiments]

        x_pos = np.arange(len(names))

        # 1. 匹配数对比
        ax1 = axes[0, 0]
        bars1 = ax1.bar(x_pos, num_matches, color='steelblue', alpha=0.8)
        ax1.set_xlabel('实验', fontsize=11)
        ax1.set_ylabel('匹配数', fontsize=11)
        ax1.set_title('匹配数对比', fontsize=12, fontweight='bold')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(names, rotation=45, ha='right')
        ax1.grid(axis='y', alpha=0.3)
        # 添加数值标签
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom', fontsize=9)

        # 2. 频谱利用率对比
        ax2 = axes[0, 1]
        bars2 = ax2.bar(x_pos, utilization, color='seagreen', alpha=0.8)
        ax2.set_xlabel('实验', fontsize=11)
        ax2.set_ylabel('频谱利用率 (%)', fontsize=11)
        ax2.set_title('频谱利用率对比', fontsize=12, fontweight='bold')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(names, rotation=45, ha='right')
        ax2.set_ylim(0, 110)
        ax2.grid(axis='y', alpha=0.3)
        # 添加数值标签
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=9)

        # 3. 执行时间对比
        ax3 = axes[1, 0]
        bars3 = ax3.bar(x_pos, exec_time, color='coral', alpha=0.8)
        ax3.set_xlabel('实验', fontsize=11)
        ax3.set_ylabel('执行时间 (ms)', fontsize=11)
        ax3.set_title('执行时间对比', fontsize=12, fontweight='bold')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(names, rotation=45, ha='right')
        ax3.grid(axis='y', alpha=0.3)
        # 添加数值标签
        for bar in bars3:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', ha='center', va='bottom', fontsize=9)

        # 4. 已匹配用户数对比
        ax4 = axes[1, 1]
        bars4 = ax4.bar(x_pos, matched_users, color='mediumpurple', alpha=0.8)
        ax4.set_xlabel('实验', fontsize=11)
        ax4.set_ylabel('已匹配用户数', fontsize=11)
        ax4.set_title('已匹配用户数对比', fontsize=12, fontweight='bold')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(names, rotation=45, ha='right')
        ax4.grid(axis='y', alpha=0.3)
        # 添加数值标签
        for bar in bars4:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom', fontsize=9)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"性能指标对比图已保存至: {save_path}")

        if show:
            plt.show()
        else:
            plt.close()

    def plot_summary(self, save_path: Optional[str] = None, show: bool = True) -> None:
        """
        绘制汇总统计图

        参数:
            save_path: 保存路径（可选）
            show: 是否显示图形
        """
        summary = self.batch_results.summary

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # 1. 实验成功率饼图
        ax1 = axes[0]
        sizes = [summary['successful_experiments'], summary['failed_experiments']]
        labels = ['成功', '失败']
        colors = ['lightgreen', 'lightcoral']
        explode = (0.1, 0)

        if summary['failed_experiments'] == 0:
            # 如果没有失败的实验，只显示成功
            sizes = [summary['successful_experiments']]
            labels = ['成功']
            colors = ['lightgreen']
            explode = (0,)

        ax1.pie(sizes, explode=explode, labels=labels, colors=colors,
               autopct='%1.1f%%', shadow=True, startangle=90)
        ax1.set_title(f'实验成功率\n(总计: {summary["total_experiments"]}个)',
                     fontsize=12, fontweight='bold')

        # 2. 平均性能指标柱状图
        ax2 = axes[1]
        metrics = ['平均匹配数', '平均利用率(%)', '平均时间(ms)']
        values = [
            summary['average_matches'],
            summary['average_spectrum_utilization'] * 100,
            summary['average_execution_time'] * 1000
        ]
        colors_bar = ['steelblue', 'seagreen', 'coral']

        bars = ax2.bar(metrics, values, color=colors_bar, alpha=0.8)
        ax2.set_ylabel('数值', fontsize=11)
        ax2.set_title('平均性能指标', fontsize=12, fontweight='bold')
        ax2.set_xticklabels(metrics)
        ax2.grid(axis='y', alpha=0.3)

        # 添加数值标签
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:.2f}', ha='center', va='bottom', fontsize=10)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"汇总统计图已保存至: {save_path}")

        if show:
            plt.show()
        else:
            plt.close()

    def plot_trend(self, metric: str = 'num_matches', save_path: Optional[str] = None, show: bool = True) -> None:
        """
        绘制指标趋势图

        参数:
            metric: 指标名称 ('num_matches', 'spectrum_utilization', 'execution_time')
            save_path: 保存路径（可选）
            show: 是否显示图形
        """
        experiments = [e for e in self.batch_results.experiments if e.success]

        if len(experiments) == 0:
            print("警告: 没有成功的实验结果，无法绘制趋势图")
            return

        fig, ax = plt.subplots(figsize=(12, 6))

        names = [e.config.name for e in experiments]
        x_pos = np.arange(len(names))

        # 根据指标类型提取数据
        if metric == 'num_matches':
            values = [e.matching_result.num_matches for e in experiments]
            ylabel = '匹配数'
            title = '匹配数趋势'
            color = 'steelblue'
        elif metric == 'spectrum_utilization':
            values = [e.matching_result.spectrum_utilization * 100 for e in experiments]
            ylabel = '频谱利用率 (%)'
            title = '频谱利用率趋势'
            color = 'seagreen'
        elif metric == 'execution_time':
            values = [e.matching_result.execution_time * 1000 for e in experiments]
            ylabel = '执行时间 (ms)'
            title = '执行时间趋势'
            color = 'coral'
        else:
            print(f"警告: 未知的指标类型 '{metric}'")
            return

        # 绘制折线图
        ax.plot(x_pos, values, marker='o', linewidth=2, markersize=8, color=color, alpha=0.8)

        # 添加数据点标签
        for i, value in enumerate(values):
            ax.text(i, value, f'{value:.2f}', ha='center', va='bottom', fontsize=9)

        ax.set_xlabel('实验', fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(names, rotation=45, ha='right')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"趋势图已保存至: {save_path}")

        if show:
            plt.show()
        else:
            plt.close()
