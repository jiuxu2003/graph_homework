"""
规模对比实验运行脚本

执行不同规模的测试用例，生成性能对比报告
"""

import sys
import os
sys.path.insert(0, 'src')

from experiments.batch_runner import BatchRunner
from experiments.report_generator import ReportGenerator
from models import ExperimentConfig


def main():
    """主函数"""
    print("=" * 80)
    print("匈牙利算法规模对比实验")
    print("=" * 80)
    print()

    # 定义实验配置列表
    experiment_configs = [
        {
            "name": "小规模-理想(5×5)",
            "config_path": "configs/experiments/small_5x5_ideal.json"
        },
        {
            "name": "小规模-稀疏(5×8)",
            "config_path": "configs/experiments/small_5x8_sparse.json"
        },
        {
            "name": "中规模-理想(10×10)",
            "config_path": "configs/experiments/medium_10x10_ideal.json"
        },
        {
            "name": "中规模-竞争(15×10)",
            "config_path": "configs/experiments/medium_15x10_compete.json"
        },
        {
            "name": "中规模-稀疏(20×15)",
            "config_path": "configs/experiments/medium_20x15_sparse.json"
        },
        {
            "name": "大规模-理想(50×30)",
            "config_path": "configs/experiments/large_50x30_ideal.json"
        },
        {
            "name": "大规模-重负载(50×30)",
            "config_path": "configs/experiments/large_50x30_heavy.json"
        },
        {
            "name": "超大规模-理想(100×50)",
            "config_path": "configs/experiments/xlarge_100x50_ideal.json"
        }
    ]

    # 步骤1：运行批量实验
    print("步骤 1: 运行批量实验")
    print("-" * 80)

    configs = []
    for exp in experiment_configs:
        config = ExperimentConfig(
            name=exp["name"],
            config_path=exp["config_path"]
        )
        configs.append(config)

    runner = BatchRunner(configs)
    batch_results = runner.run()

    print()
    print("步骤 2: 生成实验报告")
    print("-" * 80)

    # 确保输出目录存在
    output_dir = "results/scale_comparison"
    os.makedirs(output_dir, exist_ok=True)

    # 生成报告
    generator = ReportGenerator(batch_results)

    # 生成所有格式的报告
    report_files = generator.generate_all_reports(
        output_dir=output_dir,
        base_filename="scale_comparison_report"
    )

    print()
    print("=" * 80)
    print("实验完成！")
    print("=" * 80)
    print()
    print("生成的报告文件：")
    for file_type, file_path in report_files.items():
        print(f"  - {file_type}: {file_path}")
    print()

    # 打印摘要统计
    summary = batch_results.summary
    print("实验摘要：")
    print(f"  总实验数: {summary['total_experiments']}")
    print(f"  成功实验: {summary['successful_experiments']}")
    print(f"  失败实验: {summary['failed_experiments']}")
    print(f"  成功率: {summary['success_rate']:.1%}")
    print()
    print(f"  平均匹配数: {summary['average_matches']:.2f}")
    print(f"  平均频谱利用率: {summary['average_spectrum_utilization']:.1%}")
    print(f"  平均执行时间: {summary['average_execution_time']*1000:.3f} ms")
    print()

    # 打印各规模的详细结果
    print("各规模详细结果：")
    print("-" * 80)
    print(f"{'实验名称':<25} {'用户×信道':<12} {'匹配数':<8} {'利用率':<10} {'时间(ms)':<10}")
    print("-" * 80)

    for exp in batch_results.experiments:
        if exp.success:
            result = exp.matching_result
            # 从配置路径提取规模信息
            config_name = exp.config.name
            scale = config_name.split('(')[1].rstrip(')')

            print(f"{config_name:<25} {scale:<12} {result.num_matches:<8} "
                  f"{result.spectrum_utilization*100:>6.1f}%   {result.execution_time*1000:>8.3f}")

    print("-" * 80)
    print()
    print("✓ 所有结果已保存到: results/scale_comparison/")
    print()


if __name__ == '__main__':
    main()
