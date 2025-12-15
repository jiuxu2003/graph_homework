"""
CLI Colors Module

Provides terminal color detection, color application, and configuration management.
"""

import os
import sys
from dataclasses import dataclass
from typing import Optional

try:
    from colorama import Fore, Style, init as colorama_init
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # Define empty color constants if colorama is not installed
    class Fore:
        GREEN = ''
        RED = ''
        YELLOW = ''
        WHITE = ''
        CYAN = ''

    class Style:
        RESET_ALL = ''


def should_use_color() -> bool:
    """
    Detect whether color output should be used

    Detection logic:
    1. Check if colorama is available
    2. Check if output is redirected (sys.stdout.isatty())
    3. Check NO_COLOR environment variable (follows NO_COLOR standard)
    4. Check TERM environment variable

    Returns:
        bool: True if color should be used, False otherwise
    """
    # Disable color if colorama is not available
    if not COLORAMA_AVAILABLE:
        return False

    # Disable color if output is redirected
    if not sys.stdout.isatty():
        return False

    # Check NO_COLOR environment variable (follows https://no-color.org/ standard)
    if os.getenv('NO_COLOR'):
        return False

    # Check TERM environment variable
    term = os.getenv('TERM', '')
    if term == 'dumb':
        return False

    return True


def colorize(text: str, color: str) -> str:
    """
    Add color to text

    Args:
        text: Text to colorize
        color: Color code (colorama constant, e.g. Fore.GREEN)

    Returns:
        str: Text with color codes (automatically adds reset code)
    """
    if not should_use_color():
        return text

    return f"{color}{text}{Style.RESET_ALL}"


@dataclass
class ColorScheme:
    """
    Color scheme

    Defines color configuration for different types of information.
    """
    success: str = Fore.GREEN
    error: str = Fore.RED
    warning: str = Fore.YELLOW
    info: str = Fore.WHITE
    highlight: str = Fore.CYAN

    def apply(self, text: str, color_type: str) -> str:
        """
        Apply color to text

        Args:
            text: Text to colorize
            color_type: Color type ('success', 'error', 'warning', 'info', 'highlight')

        Returns:
            str: Text with color codes

        Raises:
            ValueError: If color_type is not a valid color type
        """
        color_map = {
            'success': self.success,
            'error': self.error,
            'warning': self.warning,
            'info': self.info,
            'highlight': self.highlight
        }

        if color_type not in color_map:
            raise ValueError(f"Invalid color type: {color_type}. Valid types: {list(color_map.keys())}")

        return colorize(text, color_map[color_type])


@dataclass
class OutputConfig:
    """
    Output configuration

    Configuration object to control output format.
    """
    verbosity_level: str = 'normal'  # 'quiet', 'normal', 'verbose'
    use_color: bool = True
    terminal_width: int = 80
    show_progress: bool = True

    def __post_init__(self):
        """Validate configuration after initialization"""
        # Validate verbosity_level
        valid_levels = ['quiet', 'normal', 'verbose']
        if self.verbosity_level not in valid_levels:
            raise ValueError(f"Invalid verbosity level: {self.verbosity_level}. Valid values: {valid_levels}")

        # Validate terminal_width
        if self.terminal_width < 40:
            raise ValueError(f"Terminal width must be >= 40, current value: {self.terminal_width}")

        # Auto-disable color and progress if output is redirected
        if not sys.stdout.isatty():
            self.use_color = False
            self.show_progress = False

        # Disable color if should_use_color() returns False
        if self.use_color and not should_use_color():
            self.use_color = False

    @classmethod
    def from_args(cls, args) -> 'OutputConfig':
        """
        Create configuration from command-line arguments

        Args:
            args: Parsed argparse arguments object

        Returns:
            OutputConfig: Configuration object
        """
        # Determine verbosity level
        if hasattr(args, 'verbose') and args.verbose:
            verbosity_level = 'verbose'
        elif hasattr(args, 'quiet') and args.quiet:
            verbosity_level = 'quiet'
        else:
            verbosity_level = 'normal'

        # Determine whether to use color
        use_color = True
        if hasattr(args, 'no_color') and args.no_color:
            use_color = False

        return cls(
            verbosity_level=verbosity_level,
            use_color=use_color,
            show_progress=sys.stdout.isatty()
        )


# Initialize colorama (if available)
if COLORAMA_AVAILABLE:
    colorama_init(autoreset=True)
