"""
实验控制器

管理单个实验的运行，包括配置加载、参数验证、实验执行、结果处理。
"""

from typing import Optional, Callable, Dict, Any, List
from pathlib import Path
import uuid
import json
from datetime import datetime

from ..utils.threading_utils import BackgroundTask, TaskStatus, TaskResult
from ..utils.validation import validate_experiment_config, ValidationError


class ExperimentController:
    """
    实验运行控制器

    负责管理实验的整个生命周期。
    """

    def __init__(
        self,
        result_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        error_callback: Optional[Callable[[Exception], None]] = None
    ):
        """
        初始化实验控制器

        Args:
            result_callback: 实验完成时的回调函数，接收结果字典
            error_callback: 实验失败时的回调函数，接收异常对象
        """
        self.result_callback = result_callback
        self.error_callback = error_callback
        self.current_task: Optional[BackgroundTask] = None
        self.current_task_id: Optional[str] = None

    def load_config(self, config_file: str) -> Dict[str, Any]:
        """
        从文件加载实验配置

        Args:
            config_file: 配置文件路径

        Returns:
            Dict[str, Any]: 加载的配置字典

        Raises:
            FileNotFoundError: 配置文件不存在
            ValueError: 配置文件格式错误或内容无效
        """
        config_path = Path(config_file)

        # 验证配置文件
        config, errors = validate_experiment_config(config_path)

        if errors:
            raise ValueError(f"配置文件验证失败:\n" + "\n".join(f"- {e}" for e in errors))

        return config

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """
        验证实验配置的有效性

        Args:
            config: 要验证的配置字典

        Returns:
            List[str]: 错误列表，如果为空则配置有效
        """
        errors = []

        # 验证network_topology
        if 'network_topology' not in config:
            errors.append("缺少network_topology字段")
        else:
            topology = config['network_topology']
            if topology.get('num_users', 0) <= 0:
                errors.append("num_users必须大于0")
            if topology.get('num_channels', 0) <= 0:
                errors.append("num_channels必须大于0")

        # 验证constraints
        if 'constraints' not in config:
            errors.append("缺少constraints字段")
        else:
            constraints = config['constraints']
            # 至少需要一个约束条件
            has_constraint = any([
                constraints.get('availability', False),
                constraints.get('single_transceiver', False),
                constraints.get('avoid_interference', False)
            ])
            if not has_constraint:
                errors.append("至少需要启用一个约束条件")

        return errors

    def run_experiment_sync(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        同步运行实验（阻塞调用）

        Args:
            config: 实验配置字典

        Returns:
            Dict[str, Any]: 实验结果字典

        Raises:
            ValueError: 配置无效
            RuntimeError: 实验运行失败

        Warning:
            此方法会阻塞UI线程，仅用于测试或小规模实验
        """
        # 验证配置
        errors = self.validate_config(config)
        if errors:
            raise ValueError(f"配置无效:\n" + "\n".join(f"- {e}" for e in errors))

        # 调用CLI核心算法
        try:
            result = self._run_cli_algorithm(config)
            return result
        except Exception as e:
            raise RuntimeError(f"实验运行失败: {e}") from e

    def run_experiment_async(self, config: Dict[str, Any]) -> str:
        """
        异步运行实验（非阻塞调用）

        Args:
            config: 实验配置字典

        Returns:
            str: 实验任务ID（UUID），用于查询状态或取消实验

        Raises:
            ValueError: 配置无效
            RuntimeError: 已有实验正在运行
        """
        # 验证配置
        errors = self.validate_config(config)
        if errors:
            raise ValueError(f"配置无效:\n" + "\n".join(f"- {e}" for e in errors))

        # 检查是否已有实验在运行
        if self.current_task and self.current_task.status == TaskStatus.RUNNING:
            raise RuntimeError("已有实验正在运行")

        # 创建任务ID
        task_id = str(uuid.uuid4())
        self.current_task_id = task_id

        # 创建后台任务
        self.current_task = BackgroundTask(
            task_func=self._run_cli_algorithm,
            callback=self._handle_task_result
        )

        # 启动任务
        self.current_task.start(config)

        return task_id

    def _run_cli_algorithm(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用CLI核心算法运行实验

        Args:
            config: 实验配置

        Returns:
            Dict[str, Any]: 实验结果
        """
        # TODO: 这里需要调用实际的src.algorithm.Matcher
        # 目前返回模拟结果
        import time
        time.sleep(0.5)  # 模拟计算时间

        # 模拟结果
        num_users = config.get('network_topology', {}).get('num_users', 0)
        num_channels = config.get('network_topology', {}).get('num_channels', 0)
        num_matches = min(num_users, num_channels)

        result = {
            'num_matches': num_matches,
            'matching_pairs': [(i, i) for i in range(num_matches)],
            'spectrum_utilization': num_matches / max(num_channels, 1),
            'execution_time': 0.5,
            'constraints_satisfied': True,
            'matched_users': list(range(num_matches)),
            'matched_channels': list(range(num_matches)),
            'unmatched_users': list(range(num_matches, num_users))
        }

        return result

    def _handle_task_result(self):
        """处理后台任务结果"""
        if not self.current_task:
            return

        task_result = self.current_task.check_result()
        if not task_result:
            return

        if task_result.status == TaskStatus.COMPLETED:
            if self.result_callback:
                self.result_callback(task_result.data)
        elif task_result.status == TaskStatus.FAILED:
            if self.error_callback:
                self.error_callback(task_result.error)

    def cancel_experiment(self, task_id: str) -> bool:
        """
        取消正在运行的实验

        Args:
            task_id: 实验任务ID

        Returns:
            bool: 是否成功取消
        """
        if self.current_task_id != task_id:
            return False

        if self.current_task and self.current_task.status == TaskStatus.RUNNING:
            self.current_task.cancel()
            return True

        return False

    def get_experiment_status(self, task_id: str) -> Dict[str, Any]:
        """
        查询实验运行状态

        Args:
            task_id: 实验任务ID

        Returns:
            Dict[str, Any]: 状态信息字典

        Raises:
            KeyError: 任务ID不存在
        """
        if self.current_task_id != task_id:
            raise KeyError(f"任务ID不存在: {task_id}")

        if not self.current_task:
            return {
                "status": "unknown",
                "progress": 0.0,
                "result": None,
                "error": None
            }

        # 检查是否有结果
        task_result = self.current_task.check_result()

        status_map = {
            TaskStatus.PENDING: "pending",
            TaskStatus.RUNNING: "running",
            TaskStatus.COMPLETED: "completed",
            TaskStatus.FAILED: "failed",
            TaskStatus.CANCELLED: "cancelled"
        }

        return {
            "status": status_map.get(self.current_task.status, "unknown"),
            "progress": 1.0 if task_result and task_result.status == TaskStatus.COMPLETED else 0.5,
            "result": task_result.data if task_result and task_result.status == TaskStatus.COMPLETED else None,
            "error": str(task_result.error) if task_result and task_result.error else None
        }
