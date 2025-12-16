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

        # 解析可用性矩阵（支持简化格式）
        availability_spec = network_config['availability_matrix']
        availability_matrix = ConfigLoader._parse_matrix(
            availability_spec,
            num_users,
            num_channels,
            'availability'
        )

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

        # 解析干扰图（可选，支持简化格式）
        interference_matrix = None
        if 'interference' in config and 'adjacency_matrix' in config['interference']:
            adjacency_spec = config['interference']['adjacency_matrix']
            interference_matrix = ConfigLoader._parse_matrix(
                adjacency_spec,
                num_users,
                num_users,
                'adjacency'
            )
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
    def _parse_matrix(spec: Any, rows: int, cols: int, matrix_type: str) -> np.ndarray:
        """
        解析矩阵规格（支持数组或简化字符串格式）

        参数:
            spec: 矩阵规格（可以是数组或字符串）
            rows: 行数
            cols: 列数
            matrix_type: 矩阵类型（'availability'或'adjacency'）

        返回:
            numpy矩阵
        """
        # 如果是列表，直接转换
        if isinstance(spec, list):
            return np.array(spec)

        # 如果是字符串，生成相应矩阵
        if isinstance(spec, str):
            if matrix_type == 'availability':
                return ConfigLoader._generate_availability_matrix(spec, rows, cols)
            elif matrix_type == 'adjacency':
                return ConfigLoader._generate_adjacency_matrix(spec, rows)
            else:
                raise ValueError(f"未知的矩阵类型: {matrix_type}")

        raise ValueError(f"无效的矩阵规格: {spec}")

    @staticmethod
    def _generate_availability_matrix(pattern: str, rows: int, cols: int) -> np.ndarray:
        """
        根据模式生成可用性矩阵

        参数:
            pattern: 模式字符串（如 "random_sparse_0.3", "all_ones", "all_zeros"）
            rows: 行数（用户数）
            cols: 列数（信道数）

        返回:
            可用性矩阵
        """
        if pattern == "all_ones":
            return np.ones((rows, cols), dtype=int)
        elif pattern == "all_zeros":
            return np.zeros((rows, cols), dtype=int)
        elif pattern.startswith("random_sparse_"):
            # 提取稀疏度参数
            try:
                sparsity = float(pattern.split("_")[-1])
                # 生成随机稀疏矩阵（sparsity是1的概率）
                return (np.random.random((rows, cols)) < sparsity).astype(int)
            except (ValueError, IndexError):
                raise ValueError(f"无效的random_sparse格式: {pattern}")
        else:
            raise ValueError(f"不支持的可用性矩阵模式: {pattern}")

    @staticmethod
    def _generate_adjacency_matrix(pattern: str, size: int) -> np.ndarray:
        """
        根据模式生成邻接矩阵

        参数:
            pattern: 模式字符串（如 "chain", "complete", "empty", "ring"）
            size: 矩阵大小（用户数）

        返回:
            邻接矩阵
        """
        matrix = np.zeros((size, size), dtype=int)

        if pattern == "empty":
            # 空图（无边）
            return matrix
        elif pattern == "complete":
            # 完全图（所有节点互相连接）
            matrix = np.ones((size, size), dtype=int)
            np.fill_diagonal(matrix, 0)  # 对角线设为0（自己不和自己连接）
            return matrix
        elif pattern == "chain":
            # 链式图（每个节点只和相邻节点连接）
            for i in range(size - 1):
                matrix[i][i + 1] = 1
                matrix[i + 1][i] = 1
            return matrix
        elif pattern == "ring":
            # 环形图（链式图 + 首尾相连）
            for i in range(size - 1):
                matrix[i][i + 1] = 1
                matrix[i + 1][i] = 1
            if size > 2:
                matrix[0][size - 1] = 1
                matrix[size - 1][0] = 1
            return matrix
        else:
            raise ValueError(f"不支持的邻接矩阵模式: {pattern}")


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
