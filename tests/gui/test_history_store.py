"""
测试实验历史记录存储
"""

import pytest
from datetime import datetime
from pathlib import Path

from src.gui.models.history_store import (
    ExperimentHistory,
    HistoryStore
)


class TestExperimentHistory:
    """测试ExperimentHistory数据类"""

    def test_create_history(self):
        """测试创建历史记录"""
        history = ExperimentHistory(
            id=1,
            timestamp="2025-01-01T12:00:00",
            config_file="config.json",
            config_name="test_experiment",
            config={"key": "value"},
            result={"num_matches": 10},
            success=True
        )

        assert history.id == 1
        assert history.timestamp == "2025-01-01T12:00:00"
        assert history.config_file == "config.json"
        assert history.config_name == "test_experiment"
        assert history.config == {"key": "value"}
        assert history.result == {"num_matches": 10}
        assert history.success is True
        assert history.error_message is None
        assert history.created_at is not None  # 自动生成

    def test_failed_history(self):
        """测试失败的历史记录"""
        history = ExperimentHistory(
            id=1,
            timestamp="2025-01-01T12:00:00",
            config_file="config.json",
            config_name="test_experiment",
            config={"key": "value"},
            result=None,
            success=False,
            error_message="Test error"
        )

        assert not history.success
        assert history.result is None
        assert history.error_message == "Test error"


class TestHistoryStore:
    """测试HistoryStore类"""

    @pytest.fixture
    def store(self):
        """创建内存数据库存储"""
        store = HistoryStore(":memory:")
        yield store
        store.close()

    def test_store_initialization(self, store):
        """测试存储初始化"""
        assert store.conn is not None
        assert store.db_path == ":memory:"

    def test_insert_and_query_by_id(self, store):
        """测试插入和按ID查询"""
        history = ExperimentHistory(
            id=0,
            timestamp="2025-01-01T12:00:00",
            config_file="config.json",
            config_name="test",
            config={"key": "value"},
            result={"num_matches": 10},
            success=True
        )

        # 插入记录
        history_id = store.insert(history)
        assert history_id > 0

        # 查询记录
        retrieved = store.query_by_id(history_id)
        assert retrieved is not None
        assert retrieved.id == history_id
        assert retrieved.config_file == "config.json"
        assert retrieved.config == {"key": "value"}

    def test_query_all(self, store):
        """测试查询所有记录"""
        # 插入多条记录
        for i in range(5):
            history = ExperimentHistory(
                id=0,
                timestamp=f"2025-01-0{i+1}T12:00:00",
                config_file=f"config{i}.json",
                config_name=f"test{i}",
                config={"index": i},
                result={"num_matches": i * 10},
                success=True
            )
            store.insert(history)

        # 查询所有记录
        all_records = store.query_all(limit=100)
        assert len(all_records) == 5

        # 验证顺序（按created_at倒序）
        for i, record in enumerate(all_records):
            # 最新的记录应该在前面
            assert record.config["index"] == 4 - i

    def test_query_with_pagination(self, store):
        """测试分页查询"""
        # 插入10条记录
        for i in range(10):
            history = ExperimentHistory(
                id=0,
                timestamp=f"2025-01-01T{i:02d}:00:00",
                config_file=f"config{i}.json",
                config_name=f"test{i}",
                config={"index": i},
                result={},
                success=True
            )
            store.insert(history)

        # 第一页（3条）
        page1 = store.query_all(limit=3, offset=0)
        assert len(page1) == 3

        # 第二页（3条）
        page2 = store.query_all(limit=3, offset=3)
        assert len(page2) == 3

        # 验证不重复
        page1_ids = {r.id for r in page1}
        page2_ids = {r.id for r in page2}
        assert len(page1_ids & page2_ids) == 0

    def test_query_by_filter_config_file(self, store):
        """测试按配置文件过滤查询"""
        # 插入不同配置文件的记录
        for name in ["exp1.json", "exp2.json", "test1.json"]:
            history = ExperimentHistory(
                id=0,
                timestamp="2025-01-01T12:00:00",
                config_file=name,
                config_name="test",
                config={},
                result={},
                success=True
            )
            store.insert(history)

        # 查询包含"exp"的配置文件
        results = store.query_by_filter(config_file="exp")
        assert len(results) == 2

    def test_query_by_filter_success(self, store):
        """测试按成功状态过滤查询"""
        # 插入成功和失败的记录
        for success in [True, True, False, True, False]:
            history = ExperimentHistory(
                id=0,
                timestamp="2025-01-01T12:00:00",
                config_file="config.json",
                config_name="test",
                config={},
                result={} if success else None,
                success=success,
                error_message=None if success else "Error"
            )
            store.insert(history)

        # 查询成功的记录
        success_records = store.query_by_filter(success=True)
        assert len(success_records) == 3

        # 查询失败的记录
        failed_records = store.query_by_filter(success=False)
        assert len(failed_records) == 2

    def test_delete_by_id(self, store):
        """测试按ID删除"""
        history = ExperimentHistory(
            id=0,
            timestamp="2025-01-01T12:00:00",
            config_file="config.json",
            config_name="test",
            config={},
            result={},
            success=True
        )

        history_id = store.insert(history)

        # 删除记录
        assert store.delete_by_id(history_id)

        # 验证已删除
        retrieved = store.query_by_id(history_id)
        assert retrieved is None

        # 删除不存在的记录
        assert not store.delete_by_id(99999)

    def test_delete_all(self, store):
        """测试删除所有记录"""
        # 插入多条记录
        for i in range(5):
            history = ExperimentHistory(
                id=0,
                timestamp="2025-01-01T12:00:00",
                config_file=f"config{i}.json",
                config_name="test",
                config={},
                result={},
                success=True
            )
            store.insert(history)

        # 删除所有记录
        deleted_count = store.delete_all()
        assert deleted_count == 5

        # 验证已清空
        assert store.get_count() == 0

    def test_get_count(self, store):
        """测试获取记录总数"""
        assert store.get_count() == 0

        # 插入记录
        for i in range(3):
            history = ExperimentHistory(
                id=0,
                timestamp="2025-01-01T12:00:00",
                config_file=f"config{i}.json",
                config_name="test",
                config={},
                result={},
                success=True
            )
            store.insert(history)

        assert store.get_count() == 3

    def test_get_statistics(self, store):
        """测试获取统计信息"""
        # 插入成功和失败的记录
        for i in range(5):
            success = i % 2 == 0
            history = ExperimentHistory(
                id=0,
                timestamp="2025-01-01T12:00:00",
                config_file=f"config{i}.json",
                config_name="test",
                config={},
                result={
                    "num_matches": i * 10,
                    "spectrum_utilization": i * 0.1
                } if success else None,
                success=success,
                error_message=None if success else "Error"
            )
            store.insert(history)

        stats = store.get_statistics()

        assert stats["total_count"] == 5
        assert stats["success_count"] == 3
        assert stats["failed_count"] == 2
        # 平均值计算（0, 20, 40）
        assert stats["avg_matches"] == 20.0
        assert stats["avg_utilization"] == 0.2

    def test_empty_statistics(self, store):
        """测试空数据库的统计信息"""
        stats = store.get_statistics()

        assert stats["total_count"] == 0
        assert stats["success_count"] == 0
        assert stats["failed_count"] == 0
        assert stats["avg_matches"] == 0.0
        assert stats["avg_utilization"] == 0.0
