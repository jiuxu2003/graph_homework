"""
批量实验控制器

管理批量实验的运行，包括队列管理、并发控制、进度跟踪。
"""

from typing import Optional, Callable, Dict, Any, List
from pathlib import Path
import uuid
from datetime import datetime

from ..models.gui_state import BatchExperiment, ExperimentStatus
from .experiment_controller import ExperimentController


class BatchController:
    """
    批量实验管理控制器

    负责管理批量实验队列和执行。
    """

    def __init__(
        self,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        result_callback: Optional[Callable[[BatchExperiment], None]] = None
    ):
        """
        初始化批量实验控制器

        Args:
            progress_callback: 进度更新回调，接收(当前索引, 总数)
            result_callback: 单个实验完成回调，接收BatchExperiment对象
        """
        self.progress_callback = progress_callback
        self.result_callback = result_callback
        self.experiments: List[BatchExperiment] = []
        self.current_batch_id: Optional[str] = None
        self.is_running = False
        self.is_paused = False
        self.experiment_controller = ExperimentController()

    def add_experiment(self, config_file: str) -> str:
        """
        添加实验到批量队列

        Args:
            config_file: 配置文件路径

        Returns:
            str: 实验ID（UUID）

        Raises:
            FileNotFoundError: 配置文件不存在
            ValueError: 配置文件无效
        """
        config_path = Path(config_file)

        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_file}")

        # 加载配置以验证
        try:
            config = self.experiment_controller.load_config(config_file)
            config_name = config.get('name', config_path.stem)
        except Exception as e:
            raise ValueError(f"配置文件无效: {e}")

        # 创建批量实验对象
        experiment = BatchExperiment.create(config_file, config_name)
        self.experiments.append(experiment)

        return experiment.id

    def remove_experiment(self, experiment_id: str) -> bool:
        """
        从队列中移除实验

        Args:
            experiment_id: 实验ID

        Returns:
            bool: 是否成功移除（False表示实验不存在或正在运行）
        """
        for i, exp in enumerate(self.experiments):
            if exp.id == experiment_id:
                # 只能移除PENDING状态的实验
                if exp.status == ExperimentStatus.PENDING:
                    self.experiments.pop(i)
                    return True
                else:
                    return False
        return False

    def run_batch(self, max_concurrent: int = 1) -> str:
        """
        运行批量实验

        Args:
            max_concurrent: 最大并发实验数（默认1，顺序执行）

        Returns:
            str: 批量任务ID（UUID）

        Raises:
            RuntimeError: 已有批量实验正在运行
            ValueError: 队列为空
        """
        if self.is_running:
            raise RuntimeError("已有批量实验正在运行")

        pending_experiments = [exp for exp in self.experiments if exp.status == ExperimentStatus.PENDING]
        if not pending_experiments:
            raise ValueError("队列为空，请先添加实验")

        # 创建批量任务ID
        batch_id = str(uuid.uuid4())
        self.current_batch_id = batch_id
        self.is_running = True
        self.is_paused = False

        # 注意：实际应该在后台线程中运行，这里简化处理
        # 在真实实现中，需要使用threading_utils中的BackgroundTask
        return batch_id

    def _run_batch_sequential(self):
        """顺序运行批量实验（内部方法）"""
        pending_experiments = [exp for exp in self.experiments if exp.status == ExperimentStatus.PENDING]
        total = len(pending_experiments)

        for index, experiment in enumerate(pending_experiments):
            if self.is_paused:
                break

            # 更新状态
            experiment.status = ExperimentStatus.RUNNING
            experiment.start_time = datetime.now()

            # 报告进度
            if self.progress_callback:
                self.progress_callback(index + 1, total)

            try:
                # 加载配置
                config = self.experiment_controller.load_config(experiment.config_file)

                # 运行实验
                result = self.experiment_controller.run_experiment_sync(config)

                # 保存结果
                experiment.result = result
                experiment.status = ExperimentStatus.COMPLETED

            except Exception as e:
                experiment.status = ExperimentStatus.FAILED
                experiment.error_message = str(e)

            finally:
                experiment.end_time = datetime.now()

                # 调用完成回调
                if self.result_callback:
                    self.result_callback(experiment)

        self.is_running = False

    def pause_batch(self, batch_id: str) -> bool:
        """
        暂停批量实验

        Args:
            batch_id: 批量任务ID

        Returns:
            bool: 是否成功暂停
        """
        if self.current_batch_id != batch_id:
            return False

        if self.is_running and not self.is_paused:
            self.is_paused = True
            return True

        return False

    def resume_batch(self, batch_id: str) -> bool:
        """
        恢复批量实验

        Args:
            batch_id: 批量任务ID

        Returns:
            bool: 是否成功恢复
        """
        if self.current_batch_id != batch_id:
            return False

        if self.is_running and self.is_paused:
            self.is_paused = False
            # 这里需要重新启动批量运行
            return True

        return False

    def cancel_batch(self, batch_id: str) -> bool:
        """
        取消批量实验

        Args:
            batch_id: 批量任务ID

        Returns:
            bool: 是否成功取消
        """
        if self.current_batch_id != batch_id:
            return False

        if self.is_running:
            self.is_running = False
            self.is_paused = False

            # 将所有PENDING状态的实验标记为CANCELLED
            for exp in self.experiments:
                if exp.status == ExperimentStatus.PENDING:
                    exp.status = ExperimentStatus.CANCELLED

            return True

        return False

    def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """
        获取批量实验状态

        Args:
            batch_id: 批量任务ID

        Returns:
            Dict[str, Any]: 状态信息
        """
        if self.current_batch_id != batch_id:
            raise KeyError(f"批量任务ID不存在: {batch_id}")

        completed = sum(1 for exp in self.experiments if exp.status == ExperimentStatus.COMPLETED)
        failed = sum(1 for exp in self.experiments if exp.status == ExperimentStatus.FAILED)
        pending = sum(1 for exp in self.experiments if exp.status == ExperimentStatus.PENDING)
        total = len(self.experiments)

        status = "completed" if not self.is_running else ("paused" if self.is_paused else "running")

        return {
            "status": status,
            "total": total,
            "completed": completed,
            "failed": failed,
            "pending": pending,
            "experiments": self.experiments
        }

    def get_summary_statistics(self, batch_id: str) -> Dict[str, Any]:
        """
        获取批量实验汇总统计

        Args:
            batch_id: 批量任务ID

        Returns:
            Dict[str, Any]: 汇总统计

        Raises:
            ValueError: 批量实验未完成
        """
        if self.current_batch_id != batch_id:
            raise KeyError(f"批量任务ID不存在: {batch_id}")

        if self.is_running:
            raise ValueError("批量实验尚未完成")

        completed_experiments = [exp for exp in self.experiments if exp.status == ExperimentStatus.COMPLETED]
        total = len(self.experiments)

        if total == 0:
            return {
                "success_rate": 0.0,
                "avg_matches": 0.0,
                "avg_utilization": 0.0,
                "avg_execution_time": 0.0,
                "total_time": 0.0
            }

        success_count = len(completed_experiments)
        success_rate = success_count / total

        # 计算平均值
        avg_matches = 0.0
        avg_utilization = 0.0
        avg_execution_time = 0.0

        if completed_experiments:
            matches_sum = sum(exp.result.get('num_matches', 0) for exp in completed_experiments)
            util_sum = sum(exp.result.get('spectrum_utilization', 0) for exp in completed_experiments)
            time_sum = sum(exp.result.get('execution_time', 0) for exp in completed_experiments)

            avg_matches = matches_sum / len(completed_experiments)
            avg_utilization = util_sum / len(completed_experiments)
            avg_execution_time = time_sum / len(completed_experiments)

        # 计算总耗时
        start_times = [exp.start_time for exp in self.experiments if exp.start_time]
        end_times = [exp.end_time for exp in self.experiments if exp.end_time]

        total_time = 0.0
        if start_times and end_times:
            total_time = (max(end_times) - min(start_times)).total_seconds()

        return {
            "success_rate": round(success_rate, 3),
            "avg_matches": round(avg_matches, 2),
            "avg_utilization": round(avg_utilization, 4),
            "avg_execution_time": round(avg_execution_time, 3),
            "total_time": round(total_time, 2)
        }
