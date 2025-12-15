"""
匹配结果模型

定义匹配关系、匹配结果、实验配置和实验结果
"""

from dataclasses import dataclass, field
from typing import List, Set, Optional, Dict
from datetime import datetime
import numpy as np


@dataclass
class Matching:
    """匹配关系模型"""
    user_id: int
    channel_id: int
    weight: float = 1.0

    def __post_init__(self):
        """初始化后验证"""
        assert self.user_id >= 0, "用户ID必须非负"
        assert self.channel_id >= 0, "信道ID必须非负"
        assert self.weight >= 0, "权重必须非负"


@dataclass
class MatchingResult:
    """匹配结果模型"""
    matchings: List[Matching]
    num_matches: int
    matched_users: Set[int]
    matched_channels: Set[int]
    unmatched_users: Set[int]
    spectrum_utilization: float
    execution_time: float
    constraints_satisfied: bool = True

    def __post_init__(self):
        """初始化后验证"""
        assert self.num_matches == len(self.matchings), "匹配数与匹配列表长度不一致"
        assert self.num_matches == len(self.matched_users), "匹配数与已匹配用户数不一致"
        assert self.num_matches == len(self.matched_channels), "匹配数与已匹配信道数不一致"
        assert 0 <= self.spectrum_utilization <= 1, "频谱利用率必须在[0, 1]范围内"
        assert self.execution_time >= 0, "执行时间必须非负"

    def to_dict(self) -> Dict:
        """转换为字典格式（用于JSON导出）"""
        return {
            'num_matches': self.num_matches,
            'matchings': [
                {'user_id': m.user_id, 'channel_id': m.channel_id, 'weight': m.weight}
                for m in self.matchings
            ],
            'matched_users': list(self.matched_users),
            'matched_channels': list(self.matched_channels),
            'unmatched_users': list(self.unmatched_users),
            'spectrum_utilization': self.spectrum_utilization,
            'execution_time': self.execution_time,
            'constraints_satisfied': self.constraints_satisfied
        }


@dataclass
class ExperimentConfig:
    """实验配置模型"""
    name: str
    description: str = ""
    output_dir: str = "results/"
    save_results: bool = True
    generate_visualization: bool = True

    def __post_init__(self):
        """初始化后验证"""
        assert len(self.name) > 0, "实验名称不能为空"


@dataclass
class ExperimentResult:
    """实验结果模型"""
    config: ExperimentConfig
    matching_result: MatchingResult
    timestamp: str
    success: bool = True
    error_message: Optional[str] = None

    @classmethod
    def create(cls, config: ExperimentConfig, matching_result: MatchingResult):
        """创建实验结果实例"""
        return cls(
            config=config,
            matching_result=matching_result,
            timestamp=datetime.now().isoformat(),
            success=True
        )

    def to_dict(self) -> Dict:
        """转换为字典格式（用于JSON导出）"""
        return {
            'experiment_name': self.config.name,
            'timestamp': self.timestamp,
            'results': self.matching_result.to_dict(),
            'success': self.success,
            'error_message': self.error_message
        }


@dataclass
class BatchExperimentResults:
    """批量实验结果模型"""
    experiments: List[ExperimentResult]
    summary: Dict
    timestamp: str

    @classmethod
    def create(cls, experiments: List[ExperimentResult]):
        """创建批量实验结果实例"""
        summary = cls._compute_summary(experiments)
        return cls(
            experiments=experiments,
            summary=summary,
            timestamp=datetime.now().isoformat()
        )

    @staticmethod
    def _compute_summary(experiments: List[ExperimentResult]) -> Dict:
        """计算汇总统计"""
        total = len(experiments)
        successful = sum(1 for e in experiments if e.success)

        if successful > 0:
            avg_matches = np.mean([
                e.matching_result.num_matches
                for e in experiments if e.success
            ])
            avg_utilization = np.mean([
                e.matching_result.spectrum_utilization
                for e in experiments if e.success
            ])
            avg_time = np.mean([
                e.matching_result.execution_time
                for e in experiments if e.success
            ])
        else:
            avg_matches = avg_utilization = avg_time = 0

        return {
            'total_experiments': total,
            'successful_experiments': successful,
            'failed_experiments': total - successful,
            'average_matches': float(avg_matches),
            'average_spectrum_utilization': float(avg_utilization),
            'average_execution_time': float(avg_time)
        }

    def to_dict(self) -> Dict:
        """转换为字典格式（用于JSON导出）"""
        return {
            'timestamp': self.timestamp,
            'summary': self.summary,
            'experiments': [e.to_dict() for e in self.experiments]
        }
