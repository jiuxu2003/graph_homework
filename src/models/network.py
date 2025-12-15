"""
网络拓扑模型

定义次级用户、频谱信道、主用户和网络拓扑结构
"""

from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np


@dataclass
class SecondaryUser:
    """次级用户模型"""
    user_id: int
    available_channels: List[int]
    neighbors: List[int] = field(default_factory=list)
    assigned_channel: Optional[int] = None
    is_matched: bool = False

    def __post_init__(self):
        """初始化后验证"""
        assert self.user_id >= 0, "用户ID必须非负"
        assert len(self.available_channels) > 0, "可用信道列表不能为空"
        assert len(set(self.available_channels)) == len(self.available_channels), \
            "可用信道列表不能有重复"


@dataclass
class Channel:
    """频谱信道模型"""
    channel_id: int
    is_available: bool = True
    assigned_user: Optional[int] = None

    def __post_init__(self):
        """初始化后验证"""
        assert self.channel_id >= 0, "信道ID必须非负"


@dataclass
class PrimaryUser:
    """主用户模型"""
    user_id: int
    occupied_channels: List[int]

    def __post_init__(self):
        """初始化后验证"""
        assert self.user_id >= 0, "用户ID必须非负"
        assert len(set(self.occupied_channels)) == len(self.occupied_channels), \
            "占用信道列表不能有重复"


@dataclass
class NetworkTopology:
    """网络拓扑模型"""
    secondary_users: List[SecondaryUser]
    channels: List[Channel]
    availability_matrix: np.ndarray
    primary_users: List[PrimaryUser] = field(default_factory=list)
    interference_matrix: Optional[np.ndarray] = None

    def __post_init__(self):
        """初始化后验证"""
        n_users = len(self.secondary_users)
        n_channels = len(self.channels)

        # 验证可用性矩阵维度
        assert self.availability_matrix.shape == (n_users, n_channels), \
            f"可用性矩阵维度错误：期望{(n_users, n_channels)}，实际{self.availability_matrix.shape}"

        # 验证干扰矩阵维度和对称性
        if self.interference_matrix is not None:
            assert self.interference_matrix.shape == (n_users, n_users), \
                f"干扰矩阵维度错误：期望{(n_users, n_users)}，实际{self.interference_matrix.shape}"
            assert np.allclose(self.interference_matrix, self.interference_matrix.T), \
                "干扰矩阵必须是对称矩阵"

    @property
    def num_users(self) -> int:
        """次级用户数量"""
        return len(self.secondary_users)

    @property
    def num_channels(self) -> int:
        """信道数量"""
        return len(self.channels)
