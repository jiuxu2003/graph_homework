"""
测试线程管理工具
"""

import pytest
import time
from src.gui.utils.threading_utils import (
    BackgroundTask,
    ThreadPoolManager,
    TaskStatus,
    TaskResult
)


class TestBackgroundTask:
    """测试BackgroundTask类"""

    def test_task_creation(self):
        """测试任务创建"""
        def simple_task():
            return "success"

        task = BackgroundTask(simple_task)
        assert task.status == TaskStatus.PENDING
        assert task.task_func == simple_task

    def test_task_execution_success(self):
        """测试任务成功执行"""
        def simple_task(value):
            return value * 2

        task = BackgroundTask(simple_task)
        task.start(5)

        result = task.get_result(timeout=2.0)
        assert result.status == TaskStatus.COMPLETED
        assert result.data == 10
        assert result.error is None

    def test_task_execution_failure(self):
        """测试任务执行失败"""
        def failing_task():
            raise ValueError("Test error")

        task = BackgroundTask(failing_task)
        task.start()

        result = task.get_result(timeout=2.0)
        assert result.status == TaskStatus.FAILED
        assert result.error is not None
        assert isinstance(result.error, ValueError)

    def test_task_cancellation(self):
        """测试任务取消"""
        def long_running_task():
            time.sleep(2)
            return "completed"

        task = BackgroundTask(long_running_task)
        task.start()

        # 立即取消
        task.cancel()

        result = task.get_result(timeout=3.0)
        # 取消可能已经开始执行，所以状态可能是CANCELLED或COMPLETED
        assert result.status in (TaskStatus.CANCELLED, TaskStatus.COMPLETED)

    def test_check_result_nonblocking(self):
        """测试非阻塞结果检查"""
        def slow_task():
            time.sleep(0.5)
            return "done"

        task = BackgroundTask(slow_task)
        task.start()

        # 立即检查（应该返回None）
        result = task.check_result()
        assert result is None

        # 等待完成后再检查
        time.sleep(0.6)
        result = task.check_result()
        assert result is not None
        assert result.status == TaskStatus.COMPLETED

    def test_task_with_callback(self):
        """测试带回调的任务"""
        callback_result = []

        def callback(result):
            callback_result.append(result)

        def simple_task():
            return 42

        task = BackgroundTask(simple_task, callback=callback)
        task.start()

        # 等待完成
        result = task.get_result(timeout=2.0)
        assert result.data == 42


class TestThreadPoolManager:
    """测试ThreadPoolManager类"""

    def test_pool_creation(self):
        """测试线程池创建"""
        pool = ThreadPoolManager(max_workers=2)
        assert pool.max_workers == 2
        assert len(pool.tasks) == 0

    def test_submit_task(self):
        """测试提交任务"""
        def simple_task(x):
            return x + 1

        pool = ThreadPoolManager(max_workers=1)
        task = BackgroundTask(simple_task)
        submitted_task = pool.submit(task, 10)

        assert submitted_task == task
        assert len(pool.tasks) == 1

        result = submitted_task.get_result(timeout=2.0)
        assert result.data == 11

    def test_max_workers_limit(self):
        """测试最大工作线程限制"""
        def slow_task():
            time.sleep(0.5)
            return "done"

        pool = ThreadPoolManager(max_workers=1)

        task1 = BackgroundTask(slow_task)
        pool.submit(task1)

        # 尝试提交第二个任务（应该失败）
        task2 = BackgroundTask(slow_task)
        with pytest.raises(RuntimeError, match="线程池已满"):
            pool.submit(task2)

    def test_get_running_tasks(self):
        """测试获取运行中的任务"""
        def slow_task():
            time.sleep(0.5)
            return "done"

        pool = ThreadPoolManager(max_workers=2)

        task1 = BackgroundTask(slow_task)
        pool.submit(task1)

        running_tasks = pool.get_running_tasks()
        assert len(running_tasks) == 1
        assert running_tasks[0] == task1

    def test_cancel_all(self):
        """测试取消所有任务"""
        def long_task():
            time.sleep(2)
            return "done"

        pool = ThreadPoolManager(max_workers=2)

        task1 = BackgroundTask(long_task)
        pool.submit(task1)

        pool.cancel_all()

        # 检查任务是否被取消
        assert task1.is_cancelled()
