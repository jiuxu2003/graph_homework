"""
测试批量实验控制器
"""

import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path
import tempfile
import json

from src.gui.controllers.batch_controller import BatchController
from src.gui.models.gui_state import BatchExperiment, ExperimentStatus


class TestBatchController:
    """测试BatchController类"""

    @pytest.fixture
    def controller(self):
        """创建控制器实例"""
        progress_callback = Mock()
        result_callback = Mock()
        return BatchController(
            progress_callback=progress_callback,
            result_callback=result_callback
        )

    @pytest.fixture
    def valid_config_file(self):
        """创建有效的配置文件"""
        config = {
            "name": "test_experiment",
            "network_topology": {
                "num_users": 10,
                "num_channels": 5,
                "availability_matrix": [[1, 0], [0, 1]]
            },
            "constraints": {
                "max_channels_per_user": 2
            },
            "output": {
                "save_result": True
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_path = f.name

        yield temp_path

        Path(temp_path).unlink()

    def test_controller_initialization(self, controller):
        """测试控制器初始化"""
        assert controller.progress_callback is not None
        assert controller.result_callback is not None
        assert len(controller.experiments) == 0
        assert not controller.is_running
        assert not controller.is_paused

    def test_add_experiment_valid(self, controller, valid_config_file):
        """测试添加有效实验"""
        experiment_id = controller.add_experiment(valid_config_file)

        assert experiment_id is not None
        assert len(controller.experiments) == 1
        assert controller.experiments[0].id == experiment_id
        assert controller.experiments[0].status == ExperimentStatus.PENDING

    def test_add_experiment_file_not_found(self, controller):
        """测试添加不存在的配置文件"""
        with pytest.raises(FileNotFoundError):
            controller.add_experiment("/nonexistent/config.json")

    def test_add_multiple_experiments(self, controller, valid_config_file):
        """测试添加多个实验"""
        id1 = controller.add_experiment(valid_config_file)
        id2 = controller.add_experiment(valid_config_file)

        assert len(controller.experiments) == 2
        assert id1 != id2

    def test_remove_experiment_pending(self, controller, valid_config_file):
        """测试移除PENDING状态的实验"""
        experiment_id = controller.add_experiment(valid_config_file)

        # 移除实验
        assert controller.remove_experiment(experiment_id)
        assert len(controller.experiments) == 0

    def test_remove_experiment_running(self, controller, valid_config_file):
        """测试无法移除RUNNING状态的实验"""
        experiment_id = controller.add_experiment(valid_config_file)
        controller.experiments[0].status = ExperimentStatus.RUNNING

        # 不能移除正在运行的实验
        assert not controller.remove_experiment(experiment_id)
        assert len(controller.experiments) == 1

    def test_remove_nonexistent_experiment(self, controller):
        """测试移除不存在的实验"""
        assert not controller.remove_experiment("nonexistent-id")

    def test_run_batch_success(self, controller, valid_config_file):
        """测试运行批量实验"""
        controller.add_experiment(valid_config_file)

        batch_id = controller.run_batch()

        assert batch_id is not None
        assert controller.current_batch_id == batch_id
        assert controller.is_running

    def test_run_batch_already_running(self, controller, valid_config_file):
        """测试已有批量实验正在运行时不能启动新的"""
        controller.add_experiment(valid_config_file)
        controller.run_batch()

        # 尝试再次运行
        with pytest.raises(RuntimeError, match="已有批量实验正在运行"):
            controller.run_batch()

    def test_run_batch_empty_queue(self, controller):
        """测试空队列时不能运行"""
        with pytest.raises(ValueError, match="队列为空"):
            controller.run_batch()

    def test_pause_batch(self, controller, valid_config_file):
        """测试暂停批量实验"""
        controller.add_experiment(valid_config_file)
        batch_id = controller.run_batch()

        # 暂停批量实验
        assert controller.pause_batch(batch_id)
        assert controller.is_paused

    def test_pause_batch_wrong_id(self, controller, valid_config_file):
        """测试使用错误ID暂停批量实验"""
        controller.add_experiment(valid_config_file)
        batch_id = controller.run_batch()

        # 使用错误的batch_id
        assert not controller.pause_batch("wrong-batch-id")

    def test_resume_batch(self, controller, valid_config_file):
        """测试恢复批量实验"""
        controller.add_experiment(valid_config_file)
        batch_id = controller.run_batch()
        controller.pause_batch(batch_id)

        # 恢复批量实验
        assert controller.resume_batch(batch_id)
        assert not controller.is_paused

    def test_cancel_batch(self, controller, valid_config_file):
        """测试取消批量实验"""
        controller.add_experiment(valid_config_file)
        controller.add_experiment(valid_config_file)
        batch_id = controller.run_batch()

        # 取消批量实验
        assert controller.cancel_batch(batch_id)
        assert not controller.is_running
        assert not controller.is_paused

        # 验证所有PENDING实验被标记为CANCELLED
        cancelled_count = sum(
            1 for exp in controller.experiments
            if exp.status == ExperimentStatus.CANCELLED
        )
        assert cancelled_count > 0

    def test_get_batch_status(self, controller, valid_config_file):
        """测试获取批量实验状态"""
        controller.add_experiment(valid_config_file)
        controller.add_experiment(valid_config_file)
        batch_id = controller.run_batch()

        status = controller.get_batch_status(batch_id)

        assert status["status"] == "running"
        assert status["total"] == 2
        assert status["pending"] == 2
        assert status["completed"] == 0
        assert status["failed"] == 0

    def test_get_batch_status_invalid_id(self, controller):
        """测试获取不存在的批量任务状态"""
        with pytest.raises(KeyError, match="批量任务ID不存在"):
            controller.get_batch_status("nonexistent-id")

    def test_get_summary_statistics_not_running(self, controller, valid_config_file):
        """测试获取汇总统计（批量实验已完成）"""
        controller.add_experiment(valid_config_file)
        batch_id = controller.run_batch()

        # 模拟实验完成
        controller.is_running = False
        controller.experiments[0].status = ExperimentStatus.COMPLETED
        controller.experiments[0].result = {
            "num_matches": 10,
            "spectrum_utilization": 0.85,
            "execution_time": 1.5
        }

        stats = controller.get_summary_statistics(batch_id)

        assert "success_rate" in stats
        assert "avg_matches" in stats
        assert "avg_utilization" in stats
        assert "avg_execution_time" in stats
        assert "total_time" in stats

    def test_get_summary_statistics_still_running(self, controller, valid_config_file):
        """测试批量实验正在运行时不能获取统计"""
        controller.add_experiment(valid_config_file)
        batch_id = controller.run_batch()

        with pytest.raises(ValueError, match="批量实验尚未完成"):
            controller.get_summary_statistics(batch_id)

    def test_get_summary_statistics_empty(self, controller):
        """测试空批量实验的统计"""
        batch_id = "test-batch-id"
        controller.current_batch_id = batch_id
        controller.is_running = False

        stats = controller.get_summary_statistics(batch_id)

        assert stats["success_rate"] == 0.0
        assert stats["avg_matches"] == 0.0
        assert stats["avg_utilization"] == 0.0
