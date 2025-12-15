#!/usr/bin/env python3
"""
批量实验演示脚本

演示如何使用批量实验运行器和报告生成器
"""

import os
from src.experiments import BatchRunner, ReportGenerator

def main():
    print("=" * 80)
    print("认知无线电频谱分配系统 - 批量实验演示")
    print("=" * 80)
    
    # 创建输出目录
    output_dir = "results/demo_batch/"
    os.makedirs(output_dir, exist_ok=True)
    
    # 配置文件列表
    config_files = [
        'configs/examples/simple_3x3.json',
        'configs/examples/medium_10x8.json'
    ]
    
    # 运行批量实验
    print("\n步骤 1: 运行批量实验")
    print("-" * 80)
    runner = BatchRunner(config_files, output_dir=output_dir)
    batch_results = runner.run()
    
    # 保存批量结果
    print("\n步骤 2: 保存批量实验结果")
    print("-" * 80)
    runner.save_results(batch_results, filename="batch_results.json")
    
    # 生成完整报告
    print("\n步骤 3: 生成实验报告")
    print("-" * 80)
    report_gen = ReportGenerator(batch_results, output_dir=output_dir)
    report_gen.generate_full_report('experiment_report')
    
    # 生成Markdown报告
    print("\n步骤 4: 生成Markdown报告")
    print("-" * 80)
    markdown_path = os.path.join(output_dir, 'experiment_report.md')
    report_gen.generate_markdown_report(markdown_path)
    
    print("\n" + "=" * 80)
    print("演示完成！")
    print(f"所有结果已保存至: {output_dir}")
    print("=" * 80)

if __name__ == '__main__':
    main()
