"""
矩阵热图可视化模块

用于绘制可用性矩阵和干扰矩阵的热图
"""

import os
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional

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


class MatrixPlotter:
    """矩阵热图绘制器"""

    def __init__(self, topology: NetworkTopology, result: Optional[MatchingResult] = None):
        """
        初始化绘制器

        参数:
            topology: 网络拓扑
            result: 匹配结果（可选）
        """
        self.topology = topology
        self.result = result

    def plot_availability_matrix(self, save_path: Optional[str] = None, show: bool = True) -> None:
        """
        绘制可用性矩阵热图

        参数:
            save_path: 保存路径（可选）
            show: 是否显示图形
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        # 创建可用性矩阵的副本
        matrix = self.topology.availability_matrix.copy()

        # 如果有匹配结果，标记匹配的位置
        if self.result:
            highlight_matrix = np.zeros_like(matrix, dtype=float)
            for matching in self.result.matchings:
                highlight_matrix[matching.user_id, matching.channel_id] = 1
        else:
            highlight_matrix = None

        # 绘制热图
        im = ax.imshow(matrix, cmap='YlGn', aspect='auto', alpha=0.8)

        # 如果有匹配结果，用红色边框标记
        if highlight_matrix is not None:
            for i in range(matrix.shape[0]):
                for j in range(matrix.shape[1]):
                    if highlight_matrix[i, j] == 1:
                        rect = plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                                           fill=False, edgecolor='red', linewidth=3)
                        ax.add_patch(rect)

        # 添加数值标注
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                text_color = 'white' if matrix[i, j] > 0.5 else 'black'
                text = ax.text(j, i, int(matrix[i, j]),
                             ha="center", va="center", color=text_color, fontsize=12)

        # 设置坐标轴
        ax.set_xticks(np.arange(matrix.shape[1]))
        ax.set_yticks(np.arange(matrix.shape[0]))
        ax.set_xticklabels([f'C{i}' for i in range(matrix.shape[1])])
        ax.set_yticklabels([f'U{i}' for i in range(matrix.shape[0])])

        # 设置标签
        ax.set_xlabel('频谱信道', fontsize=12)
        ax.set_ylabel('次级用户', fontsize=12)

        # 设置标题
        title = '可用性矩阵'
        if self.result:
            title += f'\n(红框表示匹配，共{self.result.num_matches}个)'
        ax.set_title(title, fontsize=14, fontweight='bold')

        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('可用性', rotation=270, labelpad=20)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"可用性矩阵热图已保存至: {save_path}")

        if show:
            plt.show()
        else:
            plt.close()

    def plot_interference_matrix(self, save_path: Optional[str] = None, show: bool = True) -> None:
        """
        绘制干扰矩阵热图

        参数:
            save_path: 保存路径（可选）
            show: 是否显示图形
        """
        if self.topology.interference_matrix is None:
            print("警告: 干扰矩阵不存在，跳过绘制")
            return

        fig, ax = plt.subplots(figsize=(10, 8))

        matrix = self.topology.interference_matrix

        # 绘制热图
        im = ax.imshow(matrix, cmap='Reds', aspect='auto', alpha=0.8)

        # 添加数值标注
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                text_color = 'white' if matrix[i, j] > 0.5 else 'black'
                text = ax.text(j, i, int(matrix[i, j]),
                             ha="center", va="center", color=text_color, fontsize=12)

        # 设置坐标轴
        ax.set_xticks(np.arange(matrix.shape[1]))
        ax.set_yticks(np.arange(matrix.shape[0]))
        ax.set_xticklabels([f'U{i}' for i in range(matrix.shape[1])])
        ax.set_yticklabels([f'U{i}' for i in range(matrix.shape[0])])

        # 设置标签
        ax.set_xlabel('次级用户', fontsize=12)
        ax.set_ylabel('次级用户', fontsize=12)
        ax.set_title('干扰矩阵（邻接关系）', fontsize=14, fontweight='bold')

        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('干扰关系', rotation=270, labelpad=20)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"干扰矩阵热图已保存至: {save_path}")

        if show:
            plt.show()
        else:
            plt.close()

    def plot_combined(self, save_path: Optional[str] = None, show: bool = True) -> None:
        """
        绘制组合图（可用性矩阵和干扰矩阵）

        参数:
            save_path: 保存路径（可选）
            show: 是否显示图形
        """
        if self.topology.interference_matrix is None:
            # 如果没有干扰矩阵，只绘制可用性矩阵
            self.plot_availability_matrix(save_path, show)
            return

        fig, axes = plt.subplots(1, 2, figsize=(16, 6))

        # 绘制可用性矩阵
        ax1 = axes[0]
        matrix1 = self.topology.availability_matrix.copy()
        im1 = ax1.imshow(matrix1, cmap='YlGn', aspect='auto', alpha=0.8)

        # 如果有匹配结果，标记匹配位置
        if self.result:
            for matching in self.result.matchings:
                rect = plt.Rectangle((matching.channel_id - 0.5, matching.user_id - 0.5), 1, 1,
                                   fill=False, edgecolor='red', linewidth=3)
                ax1.add_patch(rect)

        # 添加数值标注
        for i in range(matrix1.shape[0]):
            for j in range(matrix1.shape[1]):
                text_color = 'white' if matrix1[i, j] > 0.5 else 'black'
                ax1.text(j, i, int(matrix1[i, j]),
                        ha="center", va="center", color=text_color, fontsize=10)

        ax1.set_xticks(np.arange(matrix1.shape[1]))
        ax1.set_yticks(np.arange(matrix1.shape[0]))
        ax1.set_xticklabels([f'C{i}' for i in range(matrix1.shape[1])])
        ax1.set_yticklabels([f'U{i}' for i in range(matrix1.shape[0])])
        ax1.set_xlabel('频谱信道', fontsize=11)
        ax1.set_ylabel('次级用户', fontsize=11)
        ax1.set_title('可用性矩阵', fontsize=12, fontweight='bold')
        plt.colorbar(im1, ax=ax1)

        # 绘制干扰矩阵
        ax2 = axes[1]
        matrix2 = self.topology.interference_matrix
        im2 = ax2.imshow(matrix2, cmap='Reds', aspect='auto', alpha=0.8)

        # 添加数值标注
        for i in range(matrix2.shape[0]):
            for j in range(matrix2.shape[1]):
                text_color = 'white' if matrix2[i, j] > 0.5 else 'black'
                ax2.text(j, i, int(matrix2[i, j]),
                        ha="center", va="center", color=text_color, fontsize=10)

        ax2.set_xticks(np.arange(matrix2.shape[1]))
        ax2.set_yticks(np.arange(matrix2.shape[0]))
        ax2.set_xticklabels([f'U{i}' for i in range(matrix2.shape[1])])
        ax2.set_yticklabels([f'U{i}' for i in range(matrix2.shape[0])])
        ax2.set_xlabel('次级用户', fontsize=11)
        ax2.set_ylabel('次级用户', fontsize=11)
        ax2.set_title('干扰矩阵', fontsize=12, fontweight='bold')
        plt.colorbar(im2, ax=ax2)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"组合矩阵图已保存至: {save_path}")

        if show:
            plt.show()
        else:
            plt.close()
