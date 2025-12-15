"""
输入验证器

验证JSON配置文件的格式和数据有效性
"""

import numpy as np
from typing import Dict, Any, List, Tuple


class Validator:
    """输入验证器"""

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证配置文件

        参数:
            config: 配置字典

        返回:
            (是否有效, 错误消息列表)
        """
        errors = []

        # 验证必需字段
        if 'network' not in config:
            errors.append("缺少必需字段: network")
            return False, errors

        network = config['network']

        # 验证用户数和信道数
        if 'num_secondary_users' not in network:
            errors.append("缺少必需字段: network.num_secondary_users")
        elif not isinstance(network['num_secondary_users'], int) or network['num_secondary_users'] <= 0:
            errors.append("num_secondary_users必须是正整数")

        if 'num_channels' not in network:
            errors.append("缺少必需字段: network.num_channels")
        elif not isinstance(network['num_channels'], int) or network['num_channels'] <= 0:
            errors.append("num_channels必须是正整数")

        # 验证可用性矩阵
        if 'availability_matrix' not in network:
            errors.append("缺少必需字段: network.availability_matrix")
        else:
            matrix = np.array(network['availability_matrix'])
            expected_shape = (network['num_secondary_users'], network['num_channels'])
            if matrix.shape != expected_shape:
                errors.append(f"可用性矩阵维度错误: 期望{expected_shape}, 实际{matrix.shape}")

        # 验证干扰矩阵（如果存在）
        if 'interference' in config and 'adjacency_matrix' in config['interference']:
            interference = np.array(config['interference']['adjacency_matrix'])
            expected_shape = (network['num_secondary_users'], network['num_secondary_users'])
            if interference.shape != expected_shape:
                errors.append(f"干扰矩阵维度错误: 期望{expected_shape}, 实际{interference.shape}")
            elif not np.allclose(interference, interference.T):
                errors.append("干扰矩阵必须是对称矩阵")

        # 验证主用户占用信道（如果存在）
        if 'primary_users' in config and 'occupied_channels' in config['primary_users']:
            occupied = config['primary_users']['occupied_channels']
            for ch_id in occupied:
                if not isinstance(ch_id, int) or ch_id < 0 or ch_id >= network['num_channels']:
                    errors.append(f"无效的信道ID: {ch_id}")

        return len(errors) == 0, errors
