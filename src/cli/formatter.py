"""
Output Formatter Module

Provides formatted output functionality for experiment results.
"""

import math
from typing import List, Tuple
from .colors import OutputConfig, ColorScheme


class OutputFormatter:
    """
    Output formatter

    Responsible for formatting experiment results into user-friendly output.
    """

    def __init__(self, config: OutputConfig):
        """
        Initialize formatter

        Args:
            config: Output configuration object
        """
        self.config = config
        self.colors = ColorScheme() if config.use_color else None

    def _format_number(self, value: float, decimals: int = 0, use_separator: bool = True) -> str:
        """
        Format number with thousand separators and decimal control

        Args:
            value: Number to format
            decimals: Number of decimal places (default: 0 for integers)
            use_separator: Whether to use thousand separators (default: True)

        Returns:
            str: Formatted number string
        """
        if use_separator:
            if decimals == 0:
                return f"{value:,.0f}"
            else:
                return f"{value:,.{decimals}f}"
        else:
            if decimals == 0:
                return f"{value:.0f}"
            else:
                return f"{value:.{decimals}f}"

    def _safe_format_utilization(self, utilization: float) -> Tuple[str, str]:
        """
        Safely format spectrum utilization, handling edge cases

        Args:
            utilization: Spectrum utilization value (0.0 to 1.0)

        Returns:
            Tuple of (formatted_string, color_type)
            color_type is one of: 'success', 'warning', 'error'
        """
        # Handle NaN
        if math.isnan(utilization):
            return "N/A (Invalid)", "error"

        # Handle infinity
        if math.isinf(utilization):
            return "∞ (Invalid)", "error"

        # Handle negative values
        if utilization < 0:
            return f"{utilization * 100:.2f}% (Invalid)", "error"

        # Handle abnormally high values (> 100%)
        utilization_pct = utilization * 100
        if utilization_pct > 100:
            return f"{utilization_pct:.2f}% (Exceeds 100%)", "warning"

        # Handle zero utilization
        if utilization_pct == 0:
            return "0.00%", "warning"

        # Handle perfect match
        if utilization_pct >= 100:
            return f"{utilization_pct:.2f}% (Perfect Match)", "success"

        # Normal case
        return f"{utilization_pct:.2f}%", "success"

    def format_metrics(self, result) -> str:
        """
        Format key performance metrics

        Args:
            result: MatchingResult object

        Returns:
            str: Formatted metrics string
        """
        lines = []

        # Title
        lines.append("=" * 50)
        lines.append("Matching Results")
        lines.append("=" * 50)

        # Format number of matches
        match_text = f"✓ Maximum Matches: {result.num_matches}"
        if self.colors:
            match_text = self.colors.apply(match_text, 'success')
        lines.append(match_text)

        # Format spectrum utilization
        utilization_pct = result.spectrum_utilization * 100
        if utilization_pct >= 100:
            # Perfect match, use special marker
            util_text = f"✓ Spectrum Utilization: {utilization_pct:.2f}% (Perfect Match)"
            if self.colors:
                util_text = self.colors.apply(util_text, 'success')
        else:
            util_text = f"✓ Spectrum Utilization: {utilization_pct:.2f}%"
            if self.colors:
                util_text = self.colors.apply(util_text, 'success')
        lines.append(util_text)

        # Format execution time (convert to milliseconds)
        time_ms = result.execution_time * 1000
        time_text = f"⏱ Algorithm Runtime: {time_ms:.3f}ms"
        lines.append(time_text)

        # Format constraints satisfaction
        if result.constraints_satisfied:
            constraint_text = "✓ Constraints Satisfied: Yes"
            if self.colors:
                constraint_text = self.colors.apply(constraint_text, 'success')
        else:
            constraint_text = "✗ Constraints Satisfied: No"
            if self.colors:
                constraint_text = self.colors.apply(constraint_text, 'error')
        lines.append(constraint_text)

        # Add matched and unmatched user counts (if not in quiet mode)
        if self.config.verbosity_level != 'quiet':
            lines.append("")
            lines.append(f"Matched Users: {len(result.matched_users)}")
            lines.append(f"Unmatched Users: {len(result.unmatched_users)}")

        lines.append("=" * 50)

        return "\n".join(lines)

    def format_matching_table(self, matchings: List) -> str:
        """
        Format matching scheme as a table

        Args:
            matchings: List of Matching objects

        Returns:
            str: Formatted table string
        """
        if not matchings:
            return "No matches found"

        lines = []
        lines.append("\nMatching Scheme:")
        lines.append("-" * 40)

        # Format each matching as a row
        for matching in matchings:
            line = f"  User {matching.user_id:3d} -> Channel {matching.channel_id:3d}"
            lines.append(line)

        lines.append("-" * 40)
        return "\n".join(lines)

    def format_result(self, result) -> str:
        """
        Format complete experiment result

        Args:
            result: MatchingResult object

        Returns:
            str: Formatted result string including metrics and matching scheme
        """
        # Handle different verbosity levels
        if self.config.verbosity_level == 'quiet':
            return self._format_result_quiet(result)
        elif self.config.verbosity_level == 'verbose':
            return self._format_result_verbose(result)
        else:
            return self._format_result_normal(result)

    def _format_result_quiet(self, result) -> str:
        """Format result in quiet mode - minimal output"""
        util_str, _ = self._safe_format_utilization(result.spectrum_utilization)
        time_ms = result.execution_time * 1000
        return f"Matches: {result.num_matches}, Utilization: {util_str}, Time: {time_ms:.3f}ms"

    def _format_result_normal(self, result) -> str:
        """Format result in normal mode - standard output"""
        lines = []

        # Title with separator
        lines.append("\n" + "=" * 50)
        lines.append("MATCHING RESULTS")
        lines.append("=" * 50)

        # Format key metrics - handle zero matches
        if result.num_matches == 0:
            match_text = f"⚠ Maximum Matches: {result.num_matches}"
            if self.colors:
                match_text = self.colors.apply(match_text, 'warning')
        else:
            match_text = f"✓ Maximum Matches: {result.num_matches}"
            if self.colors:
                match_text = self.colors.apply(match_text, 'success')
        lines.append(match_text)

        # Format spectrum utilization with edge case handling
        util_str, util_color = self._safe_format_utilization(result.spectrum_utilization)
        util_text = f"✓ Spectrum Utilization: {util_str}"
        if self.colors:
            util_text = self.colors.apply(util_text, util_color)
        lines.append(util_text)

        time_ms = result.execution_time * 1000
        time_text = f"⏱ Algorithm Runtime: {time_ms:.3f}ms"
        lines.append(time_text)

        if result.constraints_satisfied:
            constraint_text = "✓ Constraints Satisfied: Yes"
            if self.colors:
                constraint_text = self.colors.apply(constraint_text, 'success')
        else:
            constraint_text = "✗ Constraints Satisfied: No"
            if self.colors:
                constraint_text = self.colors.apply(constraint_text, 'error')
        lines.append(constraint_text)

        # Add separator before matching table
        lines.append("")
        lines.append("=" * 50)

        # Add matching table
        if result.matchings:
            lines.append(self.format_matching_table(result.matchings))
        else:
            warning_text = "⚠ No matches found"
            if self.colors:
                warning_text = self.colors.apply(warning_text, 'warning')
            lines.append(warning_text)

        # Add unmatched users if any
        if result.unmatched_users:
            lines.append("")
            unmatched_list = sorted(result.unmatched_users)
            lines.append(f"Unmatched Users: {unmatched_list}")

        lines.append("=" * 50)

        return "\n".join(lines)

    def _format_result_verbose(self, result) -> str:
        """Format result in verbose mode - detailed output"""
        lines = []

        # Title with separator
        lines.append("\n" + "=" * 50)
        lines.append("MATCHING RESULTS (VERBOSE MODE)")
        lines.append("=" * 50)

        # Format key metrics with additional details - handle zero matches
        if result.num_matches == 0:
            match_text = f"⚠ Maximum Matches: {result.num_matches}"
            if self.colors:
                match_text = self.colors.apply(match_text, 'warning')
        else:
            match_text = f"✓ Maximum Matches: {result.num_matches}"
            if self.colors:
                match_text = self.colors.apply(match_text, 'success')
        lines.append(match_text)
        lines.append(f"  - Matched Users: {len(result.matched_users)}")
        lines.append(f"  - Matched Channels: {len(result.matched_channels)}")
        lines.append(f"  - Unmatched Users: {len(result.unmatched_users)}")

        # Format spectrum utilization with edge case handling
        util_str, util_color = self._safe_format_utilization(result.spectrum_utilization)
        util_text = f"✓ Spectrum Utilization: {util_str}"
        if self.colors:
            util_text = self.colors.apply(util_text, util_color)
        lines.append(util_text)

        time_ms = result.execution_time * 1000
        time_text = f"⏱ Algorithm Runtime: {time_ms:.3f}ms ({result.execution_time:.6f}s)"
        lines.append(time_text)

        if result.constraints_satisfied:
            constraint_text = "✓ Constraints Satisfied: Yes"
            if self.colors:
                constraint_text = self.colors.apply(constraint_text, 'success')
        else:
            constraint_text = "✗ Constraints Satisfied: No"
            if self.colors:
                constraint_text = self.colors.apply(constraint_text, 'error')
        lines.append(constraint_text)

        # Add detailed user/channel information
        lines.append("")
        lines.append("Detailed Information:")
        lines.append(f"  Matched User IDs: {sorted(result.matched_users)}")
        lines.append(f"  Matched Channel IDs: {sorted(result.matched_channels)}")
        if result.unmatched_users:
            lines.append(f"  Unmatched User IDs: {sorted(result.unmatched_users)}")

        # Add separator before matching table
        lines.append("")
        lines.append("=" * 50)

        # Add matching table
        if result.matchings:
            lines.append(self.format_matching_table(result.matchings))
        else:
            warning_text = "⚠ No matches found"
            if self.colors:
                warning_text = self.colors.apply(warning_text, 'warning')
            lines.append(warning_text)

        lines.append("=" * 50)

        return "\n".join(lines)

    def format_summary(self, results: List) -> str:
        """
        Format batch experiment summary

        Args:
            results: List of ExperimentResult objects

        Returns:
            str: Formatted summary string with statistics
        """
        lines = []

        # Title
        lines.append("\n" + "=" * 50)
        lines.append("BATCH EXPERIMENT SUMMARY")
        lines.append("=" * 50)

        # Calculate statistics
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful

        # Overall statistics
        lines.append(f"Total Experiments: {total}")

        success_text = f"Successful: {successful}"
        if self.colors and successful == total:
            success_text = self.colors.apply(success_text, 'success')
        lines.append(success_text)

        if failed > 0:
            fail_text = f"Failed: {failed}"
            if self.colors:
                fail_text = self.colors.apply(fail_text, 'error')
            lines.append(fail_text)
        else:
            lines.append("Failed: 0")

        # Calculate averages from successful experiments
        if successful > 0:
            successful_results = [r for r in results if r.success]

            avg_matches = sum(r.matching_result.num_matches for r in successful_results) / successful
            avg_utilization = sum(r.matching_result.spectrum_utilization for r in successful_results) / successful
            avg_time = sum(r.matching_result.execution_time for r in successful_results) / successful

            lines.append("")
            lines.append("Average Metrics (Successful Experiments):")
            lines.append(f"  Average Matches: {self._format_number(avg_matches, decimals=2)}")
            lines.append(f"  Average Spectrum Utilization: {self._format_number(avg_utilization * 100, decimals=2)}%")
            lines.append(f"  Average Execution Time: {self._format_number(avg_time * 1000, decimals=3)}ms")

        lines.append("=" * 50)

        return "\n".join(lines)

    def format_error(self, error_type: str, error_message: str, suggestion: str = None) -> str:
        """
        Format error message with optional suggestion

        Args:
            error_type: Type of error (e.g., "Configuration Error", "File Not Found")
            error_message: Detailed error message
            suggestion: Optional suggestion for fixing the error

        Returns:
            str: Formatted error message
        """
        lines = []

        # Error header
        error_header = f"✗ {error_type}"
        if self.colors:
            error_header = self.colors.apply(error_header, 'error')
        lines.append(error_header)

        # Error message
        lines.append(f"  {error_message}")

        # Suggestion if provided
        if suggestion:
            suggestion_text = f"💡 Suggestion: {suggestion}"
            if self.colors:
                suggestion_text = self.colors.apply(suggestion_text, 'info')
            lines.append(f"  {suggestion_text}")

        return "\n".join(lines)
