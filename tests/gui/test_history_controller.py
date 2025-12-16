"""
测试历史记录控制器
"""

import pytest
from datetime import datetime
from pathlib import Path
import tempfile
import json

from src.gui.controllers.history_controller import HistoryController
from src.gui.models.history_store import ExperimentHistory


class TestHistoryController:
    """测试HistoryController类"""

    @pytest.fixture
    def controller(self):
        """创建使用内存数据库的控制器"""
        controller = HistoryController(db_path=":memory:")
        yield controller
        controller.close()

    @pytest.fixture
    def sample_config(self):
        """创建示例配置"""
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

    @pytest.fixture
    def sample_result(self):
        """创建示例结果"""
        return {
            "num_matches": 10,
            "spectrum_utilization": 0.85,
            "execution_time": 1.5,
            "constraints_satisfied": True
        }

    def test_controller_initialization(self, controller):
        """测试控制器初始化"""
        assert controller.store is not None
        assert controller.store.conn is not None

    # ==================== 查询功能测试 ====================

    def test_query_all_empty(self, controller):
        """测试查询空数据库"""
        results = controller.query_all()
        assert len(results) == 0

    def test_query_all_with_records(self, controller, sample_config, sample_result):
        """测试查询所有记录"""
        # 插入多条记录
        for i in range(5):
            controller.save_experiment(
                config_file=f"config{i}.json",
                config=sample_config,
                result=sample_result,
                success=True
            )

        results = controller.query_all()
        assert len(results) == 5

    def test_query_all_pagination(self, controller, sample_config, sample_result):
        """测试分页查询"""
        # 插入10条记录
        for i in range(10):
            controller.save_experiment(
                config_file=f"config{i}.json",
                config=sample_config,
                result=sample_result,
                success=True
            )

        # 第一页
        page1 = controller.query_all(limit=3, offset=0)
        assert len(page1) == 3

        # 第二页
        page2 = controller.query_all(limit=3, offset=3)
        assert len(page2) == 3

    def test_query_by_config_file(self, controller, sample_config, sample_result):
        """测试按配置文件查询"""
        controller.save_experiment("exp1.json", sample_config, sample_result, True)
        controller.save_experiment("exp2.json", sample_config, sample_result, True)
        controller.save_experiment("test1.json", sample_config, sample_result, True)

        results = controller.query_by_config_file("exp")
        assert len(results) == 2

    def test_query_by_date_range(self, controller, sample_config, sample_result):
        """测试按日期范围查询"""
        # 插入不同日期的记录
        dates = [
            "2025-01-01T12:00:00",
            "2025-01-02T12:00:00",
            "2025-01-03T12:00:00"
        ]

        for date in dates:
            controller.save_experiment(
                config_file="config.json",
                config=sample_config,
                result=sample_result,
                success=True,
                timestamp=date
            )

        # 查询特定日期范围
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 2)

        results = controller.query_by_date_range(start_date=start, end_date=end)
        # 应该包含1月1日和1月2日的记录
        assert len(results) >= 2

    def test_query_successful(self, controller, sample_config, sample_result):
        """测试查询成功的实验"""
        controller.save_experiment("config1.json", sample_config, sample_result, True)
        controller.save_experiment("config2.json", sample_config, None, False, "Error")
        controller.save_experiment("config3.json", sample_config, sample_result, True)

        results = controller.query_successful()
        assert len(results) == 2

    def test_query_failed(self, controller, sample_config):
        """测试查询失败的实验"""
        controller.save_experiment("config1.json", sample_config, sample_result, True)
        controller.save_experiment("config2.json", sample_config, None, False, "Error1")
        controller.save_experiment("config3.json", sample_config, None, False, "Error2")

        results = controller.query_failed()
        assert len(results) == 2

    def test_get_by_id(self, controller, sample_config, sample_result):
        """测试按ID获取记录"""
        history_id = controller.save_experiment(
            config_file="config.json",
            config=sample_config,
            result=sample_result,
            success=True
        )

        record = controller.get_by_id(history_id)
        assert record is not None
        assert record.id == history_id
        assert record.config_file == "config.json"

    def test_get_by_id_not_found(self, controller):
        """测试获取不存在的记录"""
        record = controller.get_by_id(99999)
        assert record is None

    def test_get_count(self, controller, sample_config, sample_result):
        """测试获取记录总数"""
        assert controller.get_count() == 0

        for i in range(3):
            controller.save_experiment(
                config_file=f"config{i}.json",
                config=sample_config,
                result=sample_result,
                success=True
            )

        assert controller.get_count() == 3

    def test_get_statistics(self, controller, sample_config, sample_result):
        """测试获取统计信息"""
        # 插入成功和失败的记录
        controller.save_experiment("config1.json", sample_config, sample_result, True)
        controller.save_experiment("config2.json", sample_config, None, False, "Error")
        controller.save_experiment("config3.json", sample_config, sample_result, True)

        stats = controller.get_statistics()

        assert stats["total_count"] == 3
        assert stats["success_count"] == 2
        assert stats["failed_count"] == 1

    # ==================== 管理功能测试 ====================

    def test_save_experiment_success(self, controller, sample_config, sample_result):
        """测试保存成功的实验"""
        history_id = controller.save_experiment(
            config_file="config.json",
            config=sample_config,
            result=sample_result,
            success=True
        )

        assert history_id > 0

        # 验证保存的数据
        record = controller.get_by_id(history_id)
        assert record.success is True
        assert record.result == sample_result
        assert record.error_message is None

    def test_save_experiment_failure(self, controller, sample_config):
        """测试保存失败的实验"""
        history_id = controller.save_experiment(
            config_file="config.json",
            config=sample_config,
            result=None,
            success=False,
            error_message="Test error"
        )

        assert history_id > 0

        # 验证保存的数据
        record = controller.get_by_id(history_id)
        assert record.success is False
        assert record.result is None
        assert record.error_message == "Test error"

    def test_save_experiment_validation(self, controller, sample_config):
        """测试保存实验的参数验证"""
        # 配置文件为空
        with pytest.raises(ValueError, match="config_file不能为空"):
            controller.save_experiment("", sample_config, None, True)

        # 配置为空
        with pytest.raises(ValueError, match="config不能为空"):
            controller.save_experiment("config.json", {}, None, True)

        # 成功但没有结果
        with pytest.raises(ValueError, match="成功的实验必须提供result"):
            controller.save_experiment("config.json", sample_config, None, True)

        # 失败但没有错误消息
        with pytest.raises(ValueError, match="失败的实验必须提供error_message"):
            controller.save_experiment("config.json", sample_config, None, False)

    def test_delete_by_id(self, controller, sample_config, sample_result):
        """测试删除记录"""
        history_id = controller.save_experiment(
            config_file="config.json",
            config=sample_config,
            result=sample_result,
            success=True
        )

        # 删除记录
        assert controller.delete_by_id(history_id)

        # 验证已删除
        assert controller.get_by_id(history_id) is None

    def test_delete_by_id_not_found(self, controller):
        """测试删除不存在的记录"""
        assert not controller.delete_by_id(99999)

    def test_delete_all(self, controller, sample_config, sample_result):
        """测试删除所有记录"""
        # 插入多条记录
        for i in range(5):
            controller.save_experiment(
                config_file=f"config{i}.json",
                config=sample_config,
                result=sample_result,
                success=True
            )

        # 删除所有记录
        deleted_count = controller.delete_all()
        assert deleted_count == 5
        assert controller.get_count() == 0

    # ==================== 导出功能测试 ====================

    def test_export_to_json_all(self, controller, sample_config, sample_result):
        """测试导出所有记录到JSON"""
        # 插入记录
        for i in range(3):
            controller.save_experiment(
                config_file=f"config{i}.json",
                config=sample_config,
                result=sample_result,
                success=True
            )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "export.json"

            # 导出
            count = controller.export_to_json(str(output_file))
            assert count == 3

            # 验证文件内容
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            assert len(data) == 3
            assert all("config" in item for item in data)
            assert all("result" in item for item in data)

    def test_export_to_json_specific_ids(self, controller, sample_config, sample_result):
        """测试导出指定ID的记录"""
        # 插入记录
        id1 = controller.save_experiment("config1.json", sample_config, sample_result, True)
        id2 = controller.save_experiment("config2.json", sample_config, sample_result, True)
        id3 = controller.save_experiment("config3.json", sample_config, sample_result, True)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "export.json"

            # 只导出id1和id3
            count = controller.export_to_json(str(output_file), history_ids=[id1, id3])
            assert count == 2

    def test_export_to_json_no_config(self, controller, sample_config, sample_result):
        """测试导出时不包含配置"""
        controller.save_experiment("config.json", sample_config, sample_result, True)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "export.json"

            controller.export_to_json(str(output_file), include_config=False)

            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            assert "config" not in data[0]

    def test_export_to_json_empty(self, controller):
        """测试导出空记录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "export.json"

            with pytest.raises(ValueError, match="没有找到要导出的记录"):
                controller.export_to_json(str(output_file))

    def test_export_summary_to_json(self, controller, sample_config, sample_result):
        """测试导出汇总统计"""
        # 插入记录
        controller.save_experiment("config1.json", sample_config, sample_result, True)
        controller.save_experiment("config2.json", sample_config, None, False, "Error")

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "summary.json"

            stats = controller.export_summary_to_json(str(output_file))

            assert "total_count" in stats
            assert "success_count" in stats
            assert "exported_at" in stats

            # 验证文件
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            assert data["total_count"] == 2
            assert data["success_count"] == 1
