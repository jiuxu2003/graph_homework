"""
实验报告生成器

生成批量实验的详细报告，包括文本报告和可视化图表
"""

import os
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

from ..models import BatchExperimentResults, ExperimentResult
from ..visualization import MetricsPlotter


class ReportGenerator:
    """实验报告生成器"""

    def __init__(self, batch_results: BatchExperimentResults, output_dir: str = "results/reports/"):
        """
        初始化报告生成器

        参数:
            batch_results: 批量实验结果
            output_dir: 输出目录
        """
        self.batch_results = batch_results
        self.output_dir = output_dir

        # 创建输出目录
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    def generate_full_report(self, report_name: str = "experiment_report") -> None:
        """
        生成完整报告（包括文本和可视化）

        参数:
            report_name: 报告名称
        """
        print("\n" + "=" * 60)
        print("开始生成实验报告")
        print("=" * 60)

        # 生成文本报告
        text_report_path = os.path.join(self.output_dir, f"{report_name}.txt")
        self.generate_text_report(text_report_path)

        # 生成JSON报告
        json_report_path = os.path.join(self.output_dir, f"{report_name}.json")
        self.generate_json_report(json_report_path)

        # 生成可视化报告
        self.generate_visualization_report(report_name)

        print("\n" + "=" * 60)
        print("报告生成完成")
        print(f"输出目录: {self.output_dir}")
        print("=" * 60)

    def generate_text_report(self, output_path: str) -> None:
        """
        生成文本格式报告

        参数:
            output_path: 输出文件路径
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            # 标题
            f.write("=" * 80 + "\n")
            f.write("认知无线电频谱分配系统 - 批量实验报告\n")
            f.write("=" * 80 + "\n\n")

            # 基本信息
            f.write(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"实验时间戳: {self.batch_results.timestamp}\n\n")

            # 汇总统计
            f.write("-" * 80 + "\n")
            f.write("汇总统计\n")
            f.write("-" * 80 + "\n")
            summary = self.batch_results.summary
            f.write(f"总实验数: {summary['total_experiments']}\n")
            f.write(f"成功实验数: {summary['successful_experiments']}\n")
            f.write(f"失败实验数: {summary['failed_experiments']}\n")
            f.write(f"成功率: {summary['successful_experiments']/summary['total_experiments']*100:.1f}%\n\n")

            if summary['successful_experiments'] > 0:
                f.write(f"平均匹配数: {summary['average_matches']:.2f}\n")
                f.write(f"平均频谱利用率: {summary['average_spectrum_utilization']*100:.2f}%\n")
                f.write(f"平均执行时间: {summary['average_execution_time']*1000:.2f} ms\n\n")

            # 详细结果
            f.write("-" * 80 + "\n")
            f.write("详细实验结果\n")
            f.write("-" * 80 + "\n\n")

            for i, exp in enumerate(self.batch_results.experiments, 1):
                f.write(f"实验 {i}: {exp.config.name}\n")
                f.write(f"  时间戳: {exp.timestamp}\n")

                if exp.success:
                    result = exp.matching_result
                    f.write(f"  状态: ✓ 成功\n")
                    f.write(f"  匹配数: {result.num_matches}\n")
                    f.write(f"  已匹配用户: {sorted(result.matched_users)}\n")
                    f.write(f"  已匹配信道: {sorted(result.matched_channels)}\n")
                    f.write(f"  未匹配用户: {sorted(result.unmatched_users)}\n")
                    f.write(f"  频谱利用率: {result.spectrum_utilization*100:.2f}%\n")
                    f.write(f"  执行时间: {result.execution_time*1000:.2f} ms\n")
                    f.write(f"  约束满足: {'是' if result.constraints_satisfied else '否'}\n")

                    # 详细匹配关系
                    f.write(f"  匹配关系:\n")
                    for matching in result.matchings:
                        f.write(f"    用户 {matching.user_id} -> 信道 {matching.channel_id}\n")
                else:
                    f.write(f"  状态: ✗ 失败\n")
                    f.write(f"  错误信息: {exp.error_message}\n")

                f.write("\n")

            # 性能分析
            if summary['successful_experiments'] > 1:
                f.write("-" * 80 + "\n")
                f.write("性能分析\n")
                f.write("-" * 80 + "\n\n")

                successful_exps = [e for e in self.batch_results.experiments if e.success]

                # 最佳匹配数
                best_matches = max(successful_exps, key=lambda e: e.matching_result.num_matches)
                f.write(f"最佳匹配数: {best_matches.matching_result.num_matches} ({best_matches.config.name})\n")

                # 最高利用率
                best_util = max(successful_exps, key=lambda e: e.matching_result.spectrum_utilization)
                f.write(f"最高频谱利用率: {best_util.matching_result.spectrum_utilization*100:.2f}% ({best_util.config.name})\n")

                # 最快执行时间
                fastest = min(successful_exps, key=lambda e: e.matching_result.execution_time)
                f.write(f"最快执行时间: {fastest.matching_result.execution_time*1000:.2f} ms ({fastest.config.name})\n\n")

            f.write("=" * 80 + "\n")
            f.write("报告结束\n")
            f.write("=" * 80 + "\n")

        print(f"✓ 文本报告已生成: {output_path}")

    def generate_json_report(self, output_path: str) -> None:
        """
        生成JSON格式报告

        参数:
            output_path: 输出文件路径
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.batch_results.to_dict(), f, indent=2, ensure_ascii=False)

        print(f"✓ JSON报告已生成: {output_path}")

    def generate_visualization_report(self, report_name: str) -> None:
        """
        生成可视化报告

        参数:
            report_name: 报告名称
        """
        plotter = MetricsPlotter(self.batch_results)

        # 生成对比图
        comparison_path = os.path.join(self.output_dir, f"{report_name}_comparison.png")
        plotter.plot_comparison(save_path=comparison_path, show=False)
        print(f"✓ 对比图已生成: {comparison_path}")

        # 生成汇总图
        summary_path = os.path.join(self.output_dir, f"{report_name}_summary.png")
        plotter.plot_summary(save_path=summary_path, show=False)
        print(f"✓ 汇总图已生成: {summary_path}")

        # 生成趋势图
        for metric in ['num_matches', 'spectrum_utilization', 'execution_time']:
            trend_path = os.path.join(self.output_dir, f"{report_name}_trend_{metric}.png")
            plotter.plot_trend(metric=metric, save_path=trend_path, show=False)
            print(f"✓ 趋势图已生成: {trend_path}")

    def generate_markdown_report(self, output_path: str) -> None:
        """
        生成Markdown格式报告

        参数:
            output_path: 输出文件路径
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            # 标题
            f.write("# 认知无线电频谱分配系统 - 批量实验报告\n\n")

            # 基本信息
            f.write("## 基本信息\n\n")
            f.write(f"- **报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"- **实验时间戳**: {self.batch_results.timestamp}\n\n")

            # 汇总统计
            f.write("## 汇总统计\n\n")
            summary = self.batch_results.summary
            f.write(f"- **总实验数**: {summary['total_experiments']}\n")
            f.write(f"- **成功实验数**: {summary['successful_experiments']}\n")
            f.write(f"- **失败实验数**: {summary['failed_experiments']}\n")
            f.write(f"- **成功率**: {summary['successful_experiments']/summary['total_experiments']*100:.1f}%\n\n")

            if summary['successful_experiments'] > 0:
                f.write("### 平均性能指标\n\n")
                f.write(f"- **平均匹配数**: {summary['average_matches']:.2f}\n")
                f.write(f"- **平均频谱利用率**: {summary['average_spectrum_utilization']*100:.2f}%\n")
                f.write(f"- **平均执行时间**: {summary['average_execution_time']*1000:.2f} ms\n\n")

            # 详细结果表格
            f.write("## 详细实验结果\n\n")
            f.write("| 实验 | 名称 | 状态 | 匹配数 | 利用率 | 执行时间(ms) |\n")
            f.write("|------|------|------|--------|--------|-------------|\n")

            for i, exp in enumerate(self.batch_results.experiments, 1):
                if exp.success:
                    result = exp.matching_result
                    f.write(f"| {i} | {exp.config.name} | ✓ | {result.num_matches} | "
                           f"{result.spectrum_utilization*100:.2f}% | {result.execution_time*1000:.2f} |\n")
                else:
                    f.write(f"| {i} | {exp.config.name} | ✗ | - | - | - |\n")

            f.write("\n")

            # 性能分析
            if summary['successful_experiments'] > 1:
                f.write("## 性能分析\n\n")
                successful_exps = [e for e in self.batch_results.experiments if e.success]

                best_matches = max(successful_exps, key=lambda e: e.matching_result.num_matches)
                best_util = max(successful_exps, key=lambda e: e.matching_result.spectrum_utilization)
                fastest = min(successful_exps, key=lambda e: e.matching_result.execution_time)

                f.write(f"- **最佳匹配数**: {best_matches.matching_result.num_matches} ({best_matches.config.name})\n")
                f.write(f"- **最高频谱利用率**: {best_util.matching_result.spectrum_utilization*100:.2f}% ({best_util.config.name})\n")
                f.write(f"- **最快执行时间**: {fastest.matching_result.execution_time*1000:.2f} ms ({fastest.config.name})\n\n")

        print(f"✓ Markdown报告已生成: {output_path}")


class ComparisonReportGenerator(ReportGenerator):
    """对比报告生成器（用于参数对比实验）"""

    def generate_comparison_table(self, output_path: str, param_name: str) -> None:
        """
        生成参数对比表格

        参数:
            output_path: 输出文件路径
            param_name: 参数名称
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"参数对比分析: {param_name}\n")
            f.write("=" * 80 + "\n\n")

            # 表头
            f.write(f"{'实验':<10} {'匹配数':<10} {'利用率(%)':<12} {'执行时间(ms)':<15} {'约束满足':<10}\n")
            f.write("-" * 80 + "\n")

            # 数据行
            for exp in self.batch_results.experiments:
                if exp.success:
                    result = exp.matching_result
                    f.write(f"{exp.config.name:<10} {result.num_matches:<10} "
                           f"{result.spectrum_utilization*100:<12.2f} "
                           f"{result.execution_time*1000:<15.2f} "
                           f"{'是' if result.constraints_satisfied else '否':<10}\n")

        print(f"✓ 对比表格已生成: {output_path}")
