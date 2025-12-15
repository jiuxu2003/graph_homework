"""
GUI状态管理模型

定义GUI应用的全局状态和数据结构。
"""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum
from datetime import datetime
import uuid


class ExperimentStatus(Enum):
    """实验状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BatchExperiment:
    """
    批量实验队列中的单个实验

    Attributes:
        id: 实验唯一ID (UUID)
        config_file: 配置文件路径
        config_name: 实验名称
        status: 实验状态
        result: 实验结果（完成后）
        error_message: 错误信息（失败时）
        start_time: 开始时间
        end_time: 结束时间
    """
    id: str
    config_file: str
    config_name: str
    status: ExperimentStatus
    result: Optional[dict] = None
    error_message: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @classmethod
    def create(cls, config_file: str, config_name: str) -> "BatchExperiment":
        """
        创建新的批量实验对象

        Args:
            config_file: 配置文件路径
            config_name: 实验名称

        Returns:
            BatchExperiment: 新的批量实验对象
        """
        return cls(
            id=str(uuid.uuid4()),
            config_file=config_file,
            config_name=config_name,
            status=ExperimentStatus.PENDING
        )

    def is_terminal_state(self) -> bool:
        """检查是否处于终止状态（已完成、失败或取消）"""
        return self.status in (
            ExperimentStatus.COMPLETED,
            ExperimentStatus.FAILED,
            ExperimentStatus.CANCELLED
        )


@dataclass
class GUIState:
    """
    GUI全局状态管理

    Attributes:
        current_config_file: 当前选择的配置文件
        current_config: 当前配置对象
        current_result: 当前实验结果
        is_experiment_running: 是否有实验正在运行
        batch_experiments: 批量实验列表
        is_batch_running: 批量实验是否正在运行
        selected_history_id: 当前选择的历史记录ID
        active_tab: 当前激活的标签页
    """
    # 当前实验相关
    current_config_file: Optional[str] = None
    current_config: Optional[dict] = None
    current_result: Optional[dict] = None
    is_experiment_running: bool = False

    # 批量实验相关
    batch_experiments: List[BatchExperiment] = field(default_factory=list)
    is_batch_running: bool = False

    # 历史记录相关
    selected_history_id: Optional[int] = None

    # UI状态
    active_tab: str = "config"  # config, params, results, viz, batch, history

    def reset_current_experiment(self):
        """重置当前实验状态"""
        self.current_config_file = None
        self.current_config = None
        self.current_result = None
        self.is_experiment_running = False

    def add_batch_experiment(self, experiment: BatchExperiment):
        """添加批量实验到队列"""
        self.batch_experiments.append(experiment)

    def remove_batch_experiment(self, experiment_id: str) -> bool:
        """
        从队列中移除批量实验

        Args:
            experiment_id: 实验ID

        Returns:
            bool: 是否成功移除
        """
        for i, exp in enumerate(self.batch_experiments):
            if exp.id == experiment_id and not exp.is_terminal_state():
                self.batch_experiments.pop(i)
                return True
        return False

    def get_batch_experiment(self, experiment_id: str) -> Optional[BatchExperiment]:
        """
        根据ID获取批量实验

        Args:
            experiment_id: 实验ID

        Returns:
            Optional[BatchExperiment]: 找到的实验对象，不存在返回None
        """
        for exp in self.batch_experiments:
            if exp.id == experiment_id:
                return exp
        return None

    def get_pending_batch_experiments(self) -> List[BatchExperiment]:
        """获取所有待运行的批量实验"""
        return [exp for exp in self.batch_experiments if exp.status == ExperimentStatus.PENDING]

    def clear_batch_experiments(self):
        """清空批量实验队列"""
        self.batch_experiments.clear()
        self.is_batch_running = False


@dataclass
class UserPreferences:
    """
    用户界面偏好设置

    Attributes:
        window_width: 窗口宽度
        window_height: 窗口高度
        window_x: 窗口X坐标
        window_y: 窗口Y坐标
        last_config_dir: 上次打开的配置文件目录
        last_output_dir: 上次使用的输出目录
        show_tooltips: 是否显示工具提示
        auto_save_history: 是否自动保存历史记录
        viz_dpi: 图表DPI
        viz_style: matplotlib样式
    """
    window_width: int = 1200
    window_height: int = 800
    window_x: Optional[int] = None
    window_y: Optional[int] = None
    last_config_dir: Optional[str] = None
    last_output_dir: Optional[str] = None
    show_tooltips: bool = True
    auto_save_history: bool = True
    viz_dpi: int = 100
    viz_style: str = "default"

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "window_width": self.window_width,
            "window_height": self.window_height,
            "window_x": self.window_x,
            "window_y": self.window_y,
            "last_config_dir": self.last_config_dir,
            "last_output_dir": self.last_output_dir,
            "show_tooltips": self.show_tooltips,
            "auto_save_history": self.auto_save_history,
            "viz_dpi": self.viz_dpi,
            "viz_style": self.viz_style
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserPreferences":
        """从字典创建"""
        return cls(
            window_width=data.get("window_width", 1200),
            window_height=data.get("window_height", 800),
            window_x=data.get("window_x"),
            window_y=data.get("window_y"),
            last_config_dir=data.get("last_config_dir"),
            last_output_dir=data.get("last_output_dir"),
            show_tooltips=data.get("show_tooltips", True),
            auto_save_history=data.get("auto_save_history", True),
            viz_dpi=data.get("viz_dpi", 100),
            viz_style=data.get("viz_style", "default")
        )
