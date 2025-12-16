"""
二部图可视化模块

用于绘制次级用户和频谱信道之间的二部图匹配关系
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import Optional
import numpy as np

from ..models import NetworkTopology, MatchingResult

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


class BipartiteGraphPlotter:
    """二部图绘制器"""

    def __init__(self, topology: NetworkTopology, result: MatchingResult):
        """
        初始化绘制器

        参数:
            topology: 网络拓扑
            result: 匹配结果
        """
        self.topology = topology
        self.result = result

    def plot(self, save_path: Optional[str] = None, show: bool = True) -> None:
        """
        绘制二部图

        参数:
            save_path: 保存路径（可选）
            show: 是否显示图形
        """
        fig, ax = plt.subplots(figsize=(12, 8))

        num_users = self.topology.num_users
        num_channels = self.topology.num_channels

        # 计算节点位置
        user_positions = self._compute_positions(num_users, x=1)
        channel_positions = self._compute_positions(num_channels, x=3)

        # 绘制可用边（浅灰色虚线）
        self._draw_available_edges(ax, user_positions, channel_positions)

        # 绘制匹配边（红色实线）
        self._draw_matching_edges(ax, user_positions, channel_positions)

        # 绘制用户节点
        self._draw_user_nodes(ax, user_positions)

        # 绘制信道节点
        self._draw_channel_nodes(ax, channel_positions)

        # 设置图形属性
        ax.set_xlim(0, 4)
        ax.set_ylim(-0.5, max(num_users, num_channels) + 0.5)
        ax.set_aspect('equal')
        ax.axis('off')

        # 添加标题和图例
        title = f'二部图匹配结果\n匹配数: {self.result.num_matches}, 频谱利用率: {self.result.spectrum_utilization:.2%}'
        ax.set_title(title, fontsize=14, fontweight='bold')

        # 创建图例
        legend_elements = [
            mpatches.Patch(color='lightblue', label='次级用户'),
            mpatches.Patch(color='lightgreen', label='频谱信道'),
            plt.Line2D([0], [0], color='red', linewidth=2, label='匹配边'),
            plt.Line2D([0], [0], color='lightgray', linewidth=1, linestyle='--', label='可用边')
        ]
        ax.legend(handles=legend_elements, loc='upper right')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"二部图已保存至: {save_path}")

        if show:
            plt.show()
        else:
            plt.close()

    def _compute_positions(self, n: int, x: float) -> np.ndarray:
        """
        计算节点位置

        参数:
            n: 节点数量
            x: x坐标

        返回:
            位置数组 (n, 2)
        """
        y_positions = np.linspace(0, n - 1, n)
        positions = np.column_stack([np.full(n, x), y_positions])
        return positions

    def _draw_available_edges(self, ax, user_positions: np.ndarray, channel_positions: np.ndarray) -> None:
        """
        绘制可用边

        参数:
            ax: matplotlib轴对象
            user_positions: 用户节点位置
            channel_positions: 信道节点位置
        """
        for i in range(self.topology.num_users):
            for j in range(self.topology.num_channels):
                if self.topology.availability_matrix[i, j] == 1:
                    x_coords = [user_positions[i, 0], channel_positions[j, 0]]
                    y_coords = [user_positions[i, 1], channel_positions[j, 1]]
                    ax.plot(x_coords, y_coords, 'lightgray', linestyle='--', linewidth=1, alpha=0.5)

    def _draw_matching_edges(self, ax, user_positions: np.ndarray, channel_positions: np.ndarray) -> None:
        """
        绘制匹配边

        参数:
            ax: matplotlib轴对象
            user_positions: 用户节点位置
            channel_positions: 信道节点位置
        """
        for matching in self.result.matchings:
            user_id = matching.user_id
            channel_id = matching.channel_id
            x_coords = [user_positions[user_id, 0], channel_positions[channel_id, 0]]
            y_coords = [user_positions[user_id, 1], channel_positions[channel_id, 1]]
            ax.plot(x_coords, y_coords, 'red', linewidth=2, alpha=0.8)

    def _draw_user_nodes(self, ax, positions: np.ndarray) -> None:
        """
        绘制用户节点

        参数:
            ax: matplotlib轴对象
            positions: 节点位置
        """
        for i, pos in enumerate(positions):
            # 判断是否已匹配
            color = 'lightblue' if i in self.result.matched_users else 'white'
            edge_color = 'blue' if i in self.result.matched_users else 'gray'

            # 绘制节点
            circle = plt.Circle(pos, 0.15, color=color, ec=edge_color, linewidth=2, zorder=3)
            ax.add_patch(circle)

            # 添加标签
            ax.text(pos[0], pos[1], f'U{i}', ha='center', va='center',
                   fontsize=10, fontweight='bold', zorder=4)

            # 添加节点ID标签
            ax.text(pos[0] - 0.3, pos[1], f'{i}', ha='right', va='center',
                   fontsize=8, color='gray')

    def _draw_channel_nodes(self, ax, positions: np.ndarray) -> None:
        """
        绘制信道节点

        参数:
            ax: matplotlib轴对象
            positions: 节点位置
        """
        for i, pos in enumerate(positions):
            # 判断是否已匹配
            color = 'lightgreen' if i in self.result.matched_channels else 'white'
            edge_color = 'green' if i in self.result.matched_channels else 'gray'

            # 绘制节点
            square = mpatches.Rectangle((pos[0] - 0.15, pos[1] - 0.15), 0.3, 0.3,
                                       color=color, ec=edge_color, linewidth=2, zorder=3)
            ax.add_patch(square)

            # 添加标签
            ax.text(pos[0], pos[1], f'C{i}', ha='center', va='center',
                   fontsize=10, fontweight='bold', zorder=4)

            # 添加节点ID标签
            ax.text(pos[0] + 0.3, pos[1], f'{i}', ha='left', va='center',
                   fontsize=8, color='gray')
