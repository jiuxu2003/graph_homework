"""
匹配问题求解器

整合匈牙利算法和约束条件，计算完整的匹配结果
"""

import time
import numpy as np
from typing import Set
from .hungarian import hungarian_algorithm
from ..models import NetworkTopology, Constraints, Matching, MatchingResult


class Matcher:
    """匹配问题求解器"""

    def __init__(self, topology: NetworkTopology, constraints: Constraints):
        """
        初始化求解器

        参数:
            topology: 网络拓扑
            constraints: 约束条件
        """
        self.topology = topology
        self.constraints = constraints

    def solve(self) -> MatchingResult:
        """
        求解匹配问题

        返回:
            MatchingResult对象
        """
        start_time = time.time()

        # 应用约束条件，构建有效的可用性矩阵
        effective_matrix = self._apply_constraints()

        # 运行匈牙利算法
        matching_dict = hungarian_algorithm(effective_matrix)

        # 计算结果
        matchings = []
        matched_users = set()
        matched_channels = set()

        for user_id, channel_id in matching_dict.items():
            matchings.append(Matching(user_id=user_id, channel_id=channel_id))
            matched_users.add(user_id)
            matched_channels.add(channel_id)

        unmatched_users = set(range(self.topology.num_users)) - matched_users
        num_matches = len(matchings)

        # 计算频谱利用率
        available_channels = sum(1 for ch in self.topology.channels if ch.is_available)
        spectrum_utilization = num_matches / available_channels if available_channels > 0 else 0

        # 计算总体频谱利用率
        total_channels = len(self.topology.channels)
        total_spectrum_utilization = num_matches / total_channels if total_channels > 0 else 0

        # 统计主用户占用的信道数
        num_primary_occupied_channels = sum(1 for ch in self.topology.channels if not ch.is_available)

        # 计算执行时间
        execution_time = time.time() - start_time

        # 验证约束条件
        constraints_satisfied = self._verify_constraints(matching_dict)

        return MatchingResult(
            matchings=matchings,
            num_matches=num_matches,
            matched_users=matched_users,
            matched_channels=matched_channels,
            unmatched_users=unmatched_users,
            spectrum_utilization=spectrum_utilization,
            execution_time=execution_time,
            constraints_satisfied=constraints_satisfied,
            total_spectrum_utilization=total_spectrum_utilization,
            num_primary_occupied_channels=num_primary_occupied_channels
        )

    def _apply_constraints(self) -> np.ndarray:
        """
        应用约束条件，构建有效的可用性矩阵

        返回:
            有效的可用性矩阵
        """
        matrix = self.topology.availability_matrix.copy()

        # 应用可用性约束（主用户占用的信道）
        if self.constraints.enable_availability:
            for channel in self.topology.channels:
                if not channel.is_available:
                    matrix[:, channel.channel_id] = 0

        return matrix

    def _verify_constraints(self, matching: dict) -> bool:
        """
        验证匹配结果是否满足所有约束条件

        参数:
            matching: 匹配字典

        返回:
            是否满足所有约束
        """
        # 验证单收发机限制（每个用户最多一个信道）
        if self.constraints.enable_single_transceiver:
            if len(matching) != len(set(matching.keys())):
                return False

        # 验证避免同频干扰约束
        if self.constraints.enable_interference_avoidance and self.topology.interference_matrix is not None:
            for user1, channel1 in matching.items():
                for user2, channel2 in matching.items():
                    if user1 != user2 and channel1 == channel2:
                        # 检查是否相邻
                        if self.topology.interference_matrix[user1][user2] == 1:
                            return False

        return True
