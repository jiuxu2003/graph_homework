"""
测试实验控制器
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import tempfile
import json

from src.gui.controllers.experiment_controller import ExperimentController


class TestExperimentController:
    """测试ExperimentController类"""

    @pytest.fixture
    def controller(self):
        """创建控制器实例"""
        result_callback = Mock()
        error_callback = Mock()
        return ExperimentController(
            result_callback=result_callback,
            error_callback=error_callback
        )

    @pytest.fixture
    def valid_config(self):
        """创建有效配置"""
        return {
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

    def test_controller_initialization(self, controller):
        """测试控制器初始化"""
        assert controller.result_callback is not None
        assert controller.error_callback is not None
        assert len(controller.active_tasks) == 0

    def test_load_config_valid(self, controller, valid_config):
        """测试加载有效配置"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(valid_config, f)
            temp_path = f.name

        try:
            config = controller.load_config(temp_path)
            assert config == valid_config
            assert config["name"] == "test_experiment"
        finally:
            Path(temp_path).unlink()

    def test_load_config_file_not_found(self, controller):
        """测试加载不存在的配置文件"""
        with pytest.raises(FileNotFoundError):
            controller.load_config("/nonexistent/config.json")

    def test_load_config_invalid_json(self, controller):
        """测试加载无效JSON配置"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json")
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="配置文件格式错误"):
                controller.load_config(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_validate_config_valid(self, controller, valid_config):
        """测试验证有效配置"""
        errors = controller.validate_config(valid_config)
        assert errors == []

    def test_validate_config_missing_fields(self, controller):
        """测试验证缺少字段的配置"""
        invalid_config = {
            "name": "test",
            "network_topology": {
                "num_users": 10
            }
        }

        errors = controller.validate_config(invalid_config)
        assert len(errors) > 0

    @patch('src.gui.controllers.experiment_controller.ExperimentController._run_cli_algorithm')
    def test_run_experiment_sync_success(self, mock_run, controller, valid_config):
        """测试同步运行实验（成功）"""
        mock_result = {
            "num_matches": 10,
            "spectrum_utilization": 0.85,
            "execution_time": 1.5,
            "constraints_satisfied": True
        }
        mock_run.return_value = mock_result

        result = controller.run_experiment_sync(valid_config)

        assert result == mock_result
        mock_run.assert_called_once_with(valid_config)

    @patch('src.gui.controllers.experiment_controller.ExperimentController._run_cli_algorithm')
    def test_run_experiment_sync_failure(self, mock_run, controller, valid_config):
        """测试同步运行实验（失败）"""
        mock_run.side_effect = RuntimeError("Algorithm error")

        with pytest.raises(RuntimeError, match="Algorithm error"):
            controller.run_experiment_sync(valid_config)

    def test_run_experiment_async(self, controller, valid_config):
        """测试异步运行实验"""
        task_id = controller.run_experiment_async(valid_config)

        assert task_id is not None
        assert task_id in controller.active_tasks
        assert len(controller.active_tasks) == 1

    def test_get_experiment_status_running(self, controller, valid_config):
        """测试获取运行中实验的状态"""
        task_id = controller.run_experiment_async(valid_config)

        status = controller.get_experiment_status(task_id)

        assert status["task_id"] == task_id
        assert status["status"] in ["running", "completed", "failed"]

    def test_get_experiment_status_not_found(self, controller):
        """测试获取不存在的任务状态"""
        with pytest.raises(KeyError, match="任务ID不存在"):
            controller.get_experiment_status("nonexistent-task-id")

    def test_cancel_experiment(self, controller, valid_config):
        """测试取消实验"""
        task_id = controller.run_experiment_async(valid_config)

        # 取消任务
        assert controller.cancel_experiment(task_id)

        # 验证任务被取消
        task = controller.active_tasks[task_id]
        assert task.is_cancelled()

    def test_cancel_nonexistent_experiment(self, controller):
        """测试取消不存在的实验"""
        assert not controller.cancel_experiment("nonexistent-task-id")

    def test_multiple_async_experiments(self, controller, valid_config):
        """测试运行多个异步实验"""
        task_id1 = controller.run_experiment_async(valid_config)
        task_id2 = controller.run_experiment_async(valid_config)

        assert task_id1 != task_id2
        assert len(controller.active_tasks) == 2
