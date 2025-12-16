"""
线程管理工具

提供后台线程运行和队列消息传递功能，避免阻塞UI。
"""

import threading
import queue
from typing import Callable, Any, Optional
from dataclasses import dataclass
from enum import Enum


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskResult:
    """任务结果"""
    status: TaskStatus
    data: Any = None
    error: Optional[Exception] = None


class BackgroundTask:
    """
    后台任务管理器

    在后台线程中执行任务，通过队列向主线程传递结果。
    """

    def __init__(self, task_func: Callable, callback: Optional[Callable] = None):
        """
        初始化后台任务

        Args:
            task_func: 要在后台执行的函数
            callback: 任务完成后的回调函数（在主线程中调用）
        """
        self.task_func = task_func
        self.callback = callback
        self.result_queue = queue.Queue()
        self.thread: Optional[threading.Thread] = None
        self.status = TaskStatus.PENDING
        self._cancel_flag = threading.Event()

    def start(self, *args, **kwargs):
        """
        启动后台任务

        Args:
            *args: 传递给task_func的位置参数
            **kwargs: 传递给task_func的关键字参数
        """
        if self.status == TaskStatus.RUNNING:
            raise RuntimeError("任务已在运行中")

        self.status = TaskStatus.RUNNING
        self._cancel_flag.clear()

        self.thread = threading.Thread(
            target=self._run_task,
            args=args,
            kwargs=kwargs,
            daemon=True
        )
        self.thread.start()

    def _run_task(self, *args, **kwargs):
        """在后台线程中执行任务"""
        try:
            # 执行任务
            result = self.task_func(*args, **kwargs)

            # 检查是否被取消
            if self._cancel_flag.is_set():
                self.status = TaskStatus.CANCELLED
                self.result_queue.put(TaskResult(
                    status=TaskStatus.CANCELLED,
                    data=None
                ))
            else:
                self.status = TaskStatus.COMPLETED
                self.result_queue.put(TaskResult(
                    status=TaskStatus.COMPLETED,
                    data=result
                ))

        except Exception as e:
            self.status = TaskStatus.FAILED
            self.result_queue.put(TaskResult(
                status=TaskStatus.FAILED,
                error=e
            ))

    def cancel(self):
        """取消任务"""
        self._cancel_flag.set()

    def is_cancelled(self) -> bool:
        """检查任务是否被取消"""
        return self._cancel_flag.is_set()

    def get_result(self, timeout: Optional[float] = None) -> TaskResult:
        """
        获取任务结果（阻塞）

        Args:
            timeout: 超时时间（秒），None表示无限等待

        Returns:
            TaskResult: 任务结果
        """
        try:
            return self.result_queue.get(timeout=timeout)
        except queue.Empty:
            raise TimeoutError("获取结果超时")

    def check_result(self) -> Optional[TaskResult]:
        """
        检查任务结果（非阻塞）

        Returns:
            Optional[TaskResult]: 如果有结果返回TaskResult，否则返回None
        """
        try:
            return self.result_queue.get_nowait()
        except queue.Empty:
            return None


class ThreadPoolManager:
    """
    简单的线程池管理器

    用于管理多个后台任务。
    """

    def __init__(self, max_workers: int = 1):
        """
        初始化线程池

        Args:
            max_workers: 最大工作线程数
        """
        self.max_workers = max_workers
        self.tasks: list[BackgroundTask] = []
        self._lock = threading.Lock()

    def submit(self, task: BackgroundTask, *args, **kwargs) -> BackgroundTask:
        """
        提交任务到线程池

        Args:
            task: 后台任务对象
            *args: 任务参数
            **kwargs: 任务关键字参数

        Returns:
            BackgroundTask: 提交的任务对象
        """
        with self._lock:
            # 检查是否超过最大工作线程数
            running_count = sum(1 for t in self.tasks if t.status == TaskStatus.RUNNING)
            if running_count >= self.max_workers:
                raise RuntimeError(f"线程池已满（最大{self.max_workers}个任务）")

            # 启动任务
            task.start(*args, **kwargs)
            self.tasks.append(task)

        return task

    def get_running_tasks(self) -> list[BackgroundTask]:
        """获取正在运行的任务列表"""
        with self._lock:
            return [t for t in self.tasks if t.status == TaskStatus.RUNNING]

    def cancel_all(self):
        """取消所有运行中的任务"""
        with self._lock:
            for task in self.tasks:
                if task.status == TaskStatus.RUNNING:
                    task.cancel()
