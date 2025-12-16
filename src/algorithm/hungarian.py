"""
匈牙利算法实现

使用增广路径方法求解二部图最大匹配问题
"""

import numpy as np
from typing import List, Set, Optional


class HungarianAlgorithm:
    """匈牙利算法实现类"""

    def __init__(self, availability_matrix: np.ndarray):
        """
        初始化匈牙利算法

        参数:
            availability_matrix: 可用性矩阵 (n_users × n_channels)
        """
        self.matrix = availability_matrix.copy()
        self.n_users, self.n_channels = self.matrix.shape
        self.matching = {}  # 用户 -> 信道的匹配
        self.reverse_matching = {}  # 信道 -> 用户的反向匹配

    def find_augmenting_path(self, user: int, visited: Set[int]) -> bool:
        """
        使用DFS寻找增广路径

        参数:
            user: 当前用户ID
            visited: 已访问的信道集合

        返回:
            是否找到增广路径
        """
        # 遍历该用户可用的所有信道
        for channel in range(self.n_channels):
            # 如果该信道可用且未被访问
            if self.matrix[user][channel] == 1 and channel not in visited:
                visited.add(channel)

                # 如果该信道未被匹配，或者可以为已匹配的用户找到新的增广路径
                if channel not in self.reverse_matching or \
                   self.find_augmenting_path(self.reverse_matching[channel], visited):
                    # 更新匹配
                    self.matching[user] = channel
                    self.reverse_matching[channel] = user
                    return True

        return False

    def solve(self) -> int:
        """
        求解最大匹配

        返回:
            最大匹配数
        """
        self.matching = {}
        self.reverse_matching = {}

        # 对每个用户尝试寻找增广路径
        for user in range(self.n_users):
            visited = set()
            self.find_augmenting_path(user, visited)

        return len(self.matching)

    def get_matching(self) -> dict:
        """
        获取匹配结果

        返回:
            用户到信道的匹配字典
        """
        return self.matching.copy()


def hungarian_algorithm(availability_matrix: np.ndarray) -> dict:
    """
    匈牙利算法求解二部图最大匹配

    参数:
        availability_matrix: 可用性矩阵 (n_users × n_channels)

    返回:
        匹配结果字典 {user_id: channel_id}

    时间复杂度: O(n³)
    """
    algo = HungarianAlgorithm(availability_matrix)
    algo.solve()
    return algo.get_matching()
