"""
Progress Tracker Module

Provides progress tracking and display functionality for batch experiments.
"""

import time
from dataclasses import dataclass, field
from .colors import OutputConfig, ColorScheme


@dataclass
class ProgressState:
    """
    Progress state

    Tracks the state of batch experiment progress.
    """
    current: int
    total: int
    description: str
    start_time: float = field(default_factory=time.time)

    def update(self, current: int, description: str):
        """
        Update progress

        Args:
            current: Current progress
            description: Task description
        """
        self.current = current
        self.description = description

    def percentage(self) -> float:
        """
        Calculate percentage

        Returns:
            float: Progress percentage (0-100)
        """
        return (self.current / self.total) * 100 if self.total > 0 else 0

    def elapsed_time(self) -> float:
        """
        Calculate elapsed time

        Returns:
            float: Elapsed time in seconds
        """
        return time.time() - self.start_time


class ProgressTracker:
    """
    Progress tracker

    Tracks and displays progress for batch experiments.
    """

    def __init__(self, total: int, config: OutputConfig):
        """
        Initialize progress tracker

        Args:
            total: Total number of tasks
            config: Output configuration
        """
        self.state = ProgressState(current=0, total=total, description="")
        self.config = config
        self.colors = ColorScheme() if config.use_color else None

    def update(self, current: int, description: str) -> None:
        """
        Update and display current progress

        Args:
            current: Current progress (1-based)
            description: Task description
        """
        self.state.update(current, description)
        if self.config.show_progress:
            self._print_progress()

    def _print_progress(self):
        """Print progress information"""
        progress_text = f"[{self.state.current}/{self.state.total}] {self.state.description}"
        print(progress_text)

    def complete(self):
        """Mark progress as complete"""
        if self.config.show_progress:
            elapsed = self.state.elapsed_time()
            complete_text = f"\nBatch experiment completed in {elapsed:.2f}s"
            if self.colors:
                complete_text = self.colors.apply(complete_text, 'success')
            print(complete_text)
