"""
JSON配置文件加载器

从JSON文件加载网络拓扑配置
"""

import json
import numpy as np
from typing import Dict, Any
from ..models import NetworkTopology, SecondaryUser, Channel, PrimaryUser, Constraints


class ConfigLoader:
    """配置加载器"""

    @staticmethod
    def load(config_path: str) -> Dict[str, Any]:
        """
        加载JSON配置文件

        参数:
            config_path: 配置文件路径

        返回:
            配置字典
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config

    @staticmethod
    def parse_network_topology(config: Dict[str, Any]) -> NetworkTopology:
        """
        解析网络拓扑配置

        参数:
            config: 配置字典

        返回:
            NetworkTopology对象
        """
        network_config = config['network']
        num_users = network_config['num_secondary_users']
        num_channels = network_config['num_channels']

        # 解析可用性矩阵
        availability_matrix = np.array(network_config['availability_matrix'])

        # 创建次级用户
        secondary_users = []
        for i in range(num_users):
            available_channels = [j for j in range(num_channels) if availability_matrix[i][j] == 1]
            user = SecondaryUser(user_id=i, available_channels=available_channels)
            secondary_users.append(user)

        # 创建信道
        channels = [Channel(channel_id=i) for i in range(num_channels)]

        # 解析主用户（可选）
        primary_users = []
        if 'primary_users' in config and 'occupied_channels' in config['primary_users']:
            occupied = config['primary_users']['occupied_channels']
            if occupied:
                primary_user = PrimaryUser(user_id=0, occupied_channels=occupied)
                primary_users.append(primary_user)
                # 标记被占用的信道
                for ch_id in occupied:
                    if 0 <= ch_id < num_channels:
                        channels[ch_id].is_available = False

        # 解析干扰图（可选）
        interference_matrix = None
        if 'interference' in config and 'adjacency_matrix' in config['interference']:
            interference_matrix = np.array(config['interference']['adjacency_matrix'])
            # 更新用户的邻居列表
            for i in range(num_users):
                neighbors = [j for j in range(num_users) if interference_matrix[i][j] == 1]
                secondary_users[i].neighbors = neighbors

        return NetworkTopology(
            secondary_users=secondary_users,
            channels=channels,
            availability_matrix=availability_matrix,
            primary_users=primary_users,
            interference_matrix=interference_matrix
        )

    @staticmethod
    def parse_constraints(config: Dict[str, Any]) -> Constraints:
        """
        解析约束条件配置

        参数:
            config: 配置字典

        返回:
            Constraints对象
        """
        if 'constraints' not in config:
            return Constraints()

        constraints_config = config['constraints']
        return Constraints(
            enable_availability=constraints_config.get('enable_availability', True),
            enable_single_transceiver=constraints_config.get('enable_single_transceiver', True),
            enable_interference_avoidance=constraints_config.get('enable_interference_avoidance', True)
        )
