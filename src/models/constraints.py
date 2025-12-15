"""
约束条件模型

定义频谱分配的约束条件配置
"""

from dataclasses import dataclass


@dataclass
class Constraints:
    """约束条件模型"""
    enable_availability: bool = True
    enable_single_transceiver: bool = True
    enable_interference_avoidance: bool = True
