"""
测试GUI状态管理模型
"""

import pytest
from datetime import datetime

from src.gui.models.gui_state import (
    ExperimentStatus,
    BatchExperiment,
    GUIState,
    UserPreferences
)


class TestExperimentStatus:
    """测试ExperimentStatus枚举"""

    def test_status_values(self):
        """测试状态值"""
        assert ExperimentStatus.PENDING.value == "pending"
        assert ExperimentStatus.RUNNING.value == "running"
        assert ExperimentStatus.COMPLETED.value == "completed"
        assert ExperimentStatus.FAILED.value == "failed"
        assert ExperimentStatus.CANCELLED.value == "cancelled"


class TestBatchExperiment:
    """测试BatchExperiment数据类"""

    def test_create_experiment(self):
        """测试创建批量实验"""
        exp = BatchExperiment.create("config.json", "test_experiment")

        assert exp.config_file == "config.json"
        assert exp.config_name == "test_experiment"
        assert exp.status == ExperimentStatus.PENDING
        assert exp.result is None
        assert exp.error_message is None
        assert exp.start_time is None
        assert exp.end_time is None
        assert exp.id is not None  # UUID应该被生成

    def test_is_terminal_state(self):
        """测试终止状态检查"""
        exp = BatchExperiment.create("config.json", "test")

        # PENDING不是终止状态
        assert not exp.is_terminal_state()

        # RUNNING不是终止状态
        exp.status = ExperimentStatus.RUNNING
        assert not exp.is_terminal_state()

        # COMPLETED是终止状态
        exp.status = ExperimentStatus.COMPLETED
        assert exp.is_terminal_state()

        # FAILED是终止状态
        exp.status = ExperimentStatus.FAILED
        assert exp.is_terminal_state()

        # CANCELLED是终止状态
        exp.status = ExperimentStatus.CANCELLED
        assert exp.is_terminal_state()

    def test_experiment_lifecycle(self):
        """测试实验生命周期"""
        exp = BatchExperiment.create("config.json", "test")

        # 开始实验
        exp.status = ExperimentStatus.RUNNING
        exp.start_time = datetime.now()

        # 完成实验
        exp.status = ExperimentStatus.COMPLETED
        exp.end_time = datetime.now()
        exp.result = {"num_matches": 10}

        assert exp.is_terminal_state()
        assert exp.result is not None
        assert exp.start_time < exp.end_time


class TestGUIState:
    """测试GUIState数据类"""

    def test_initial_state(self):
        """测试初始状态"""
        state = GUIState()

        assert state.current_config_file is None
        assert state.current_config is None
        assert state.current_result is None
        assert not state.is_experiment_running
        assert len(state.batch_experiments) == 0
        assert not state.is_batch_running
        assert state.selected_history_id is None
        assert state.active_tab == "config"

    def test_reset_current_experiment(self):
        """测试重置当前实验"""
        state = GUIState()
        state.current_config_file = "config.json"
        state.current_config = {"key": "value"}
        state.current_result = {"result": "data"}
        state.is_experiment_running = True

        state.reset_current_experiment()

        assert state.current_config_file is None
        assert state.current_config is None
        assert state.current_result is None
        assert not state.is_experiment_running

    def test_add_batch_experiment(self):
        """测试添加批量实验"""
        state = GUIState()
        exp = BatchExperiment.create("config.json", "test")

        state.add_batch_experiment(exp)

        assert len(state.batch_experiments) == 1
        assert state.batch_experiments[0] == exp

    def test_remove_batch_experiment(self):
        """测试移除批量实验"""
        state = GUIState()
        exp1 = BatchExperiment.create("config1.json", "test1")
        exp2 = BatchExperiment.create("config2.json", "test2")

        state.add_batch_experiment(exp1)
        state.add_batch_experiment(exp2)

        # 移除PENDING状态的实验
        assert state.remove_batch_experiment(exp1.id)
        assert len(state.batch_experiments) == 1

        # 不能移除终止状态的实验
        exp2.status = ExperimentStatus.COMPLETED
        assert not state.remove_batch_experiment(exp2.id)

    def test_get_batch_experiment(self):
        """测试获取批量实验"""
        state = GUIState()
        exp = BatchExperiment.create("config.json", "test")
        state.add_batch_experiment(exp)

        # 查找存在的实验
        found = state.get_batch_experiment(exp.id)
        assert found == exp

        # 查找不存在的实验
        not_found = state.get_batch_experiment("nonexistent-id")
        assert not_found is None

    def test_get_pending_batch_experiments(self):
        """测试获取待运行实验"""
        state = GUIState()

        exp1 = BatchExperiment.create("config1.json", "test1")
        exp2 = BatchExperiment.create("config2.json", "test2")
        exp3 = BatchExperiment.create("config3.json", "test3")

        exp2.status = ExperimentStatus.RUNNING
        exp3.status = ExperimentStatus.COMPLETED

        state.add_batch_experiment(exp1)
        state.add_batch_experiment(exp2)
        state.add_batch_experiment(exp3)

        pending = state.get_pending_batch_experiments()
        assert len(pending) == 1
        assert pending[0] == exp1

    def test_clear_batch_experiments(self):
        """测试清空批量实验队列"""
        state = GUIState()
        exp = BatchExperiment.create("config.json", "test")
        state.add_batch_experiment(exp)
        state.is_batch_running = True

        state.clear_batch_experiments()

        assert len(state.batch_experiments) == 0
        assert not state.is_batch_running


class TestUserPreferences:
    """测试UserPreferences数据类"""

    def test_default_preferences(self):
        """测试默认偏好设置"""
        prefs = UserPreferences()

        assert prefs.window_width == 1200
        assert prefs.window_height == 800
        assert prefs.window_x is None
        assert prefs.window_y is None
        assert prefs.last_config_dir is None
        assert prefs.last_output_dir is None
        assert prefs.show_tooltips is True
        assert prefs.auto_save_history is True
        assert prefs.viz_dpi == 100
        assert prefs.viz_style == "default"

    def test_to_dict(self):
        """测试转换为字典"""
        prefs = UserPreferences(
            window_width=1024,
            window_height=768,
            show_tooltips=False
        )

        data = prefs.to_dict()

        assert data["window_width"] == 1024
        assert data["window_height"] == 768
        assert data["show_tooltips"] is False

    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "window_width": 1024,
            "window_height": 768,
            "show_tooltips": False,
            "last_config_dir": "/home/user/configs"
        }

        prefs = UserPreferences.from_dict(data)

        assert prefs.window_width == 1024
        assert prefs.window_height == 768
        assert prefs.show_tooltips is False
        assert prefs.last_config_dir == "/home/user/configs"

    def test_from_dict_with_defaults(self):
        """测试从不完整字典创建（使用默认值）"""
        data = {
            "window_width": 1024
        }

        prefs = UserPreferences.from_dict(data)

        assert prefs.window_width == 1024
        assert prefs.window_height == 800  # 默认值
        assert prefs.show_tooltips is True  # 默认值
