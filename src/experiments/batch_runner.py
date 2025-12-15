"""
批量实验运行器

支持运行多组实验配置并收集结果
"""

import os
import json
from typing import List, Dict, Optional
from pathlib import Path

from ..models import (
    NetworkTopology, Constraints, ExperimentConfig,
    ExperimentResult, BatchExperimentResults
)
from ..algorithm import Matcher
from ..io import ConfigLoader
from ..cli import ProgressTracker, OutputFormatter, OutputConfig


class BatchRunner:
    """批量实验运行器"""

    def __init__(self, config_files: List[str], output_dir: str = "results/batch/"):
        """
        初始化批量运行器

        参数:
            config_files: 配置文件路径列表
            output_dir: 输出目录
        """
        self.config_files = config_files
        self.output_dir = output_dir
        self.results: List[ExperimentResult] = []

        # 创建输出目录
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    def run(self, output_config: Optional[OutputConfig] = None) -> BatchExperimentResults:
        """
        运行所有实验

        参数:
            output_config: 输出配置（可选，默认使用标准配置）

        返回:
            BatchExperimentResults对象
        """
        # 创建输出配置和格式化器
        if output_config is None:
            output_config = OutputConfig()
        formatter = OutputFormatter(output_config)

        # 创建进度跟踪器
        tracker = ProgressTracker(len(self.config_files), output_config)

        print(f"开始批量实验，共 {len(self.config_files)} 个配置文件")
        print("=" * 60)

        for i, config_file in enumerate(self.config_files, 1):
            # 更新进度
            tracker.update(i, f"运行实验: {os.path.basename(config_file)}")

            try:
                result = self._run_single_experiment(config_file)
                self.results.append(result)

                if output_config.verbosity_level != 'quiet':
                    print(f"✓ 实验成功: {result.config.name}")
                    print(f"  - 匹配数: {result.matching_result.num_matches}")
                    print(f"  - 频谱利用率: {result.matching_result.spectrum_utilization:.2%}")
                    print(f"  - 执行时间: {result.matching_result.execution_time*1000:.2f} ms")
            except Exception as e:
                print(f"✗ 实验失败: {str(e)}")
                # 创建失败的实验结果
                error_result = ExperimentResult(
                    config=ExperimentConfig(name=os.path.basename(config_file)),
                    matching_result=None,
                    timestamp="",
                    success=False,
                    error_message=str(e)
                )
                self.results.append(error_result)

        # 标记进度完成
        tracker.complete()

        # 创建批量结果对象
        batch_results = BatchExperimentResults.create(self.results)

        # 显示汇总统计
        print(formatter.format_summary(self.results))

        return batch_results

    def _run_single_experiment(self, config_file: str) -> ExperimentResult:
        """
        运行单个实验

        参数:
            config_file: 配置文件路径

        返回:
            ExperimentResult对象
        """
        # 加载配置
        config_data = ConfigLoader.load(config_file)

        # 构建网络拓扑
        topology = ConfigLoader.parse_network_topology(config_data)

        # 构建约束条件
        constraints = ConfigLoader.parse_constraints(config_data)

        # 创建实验配置
        experiment_config = ExperimentConfig(
            name=config_data.get('metadata', {}).get('name', os.path.basename(config_file)),
            description=config_data.get('metadata', {}).get('description', ''),
            output_dir=self.output_dir,
            save_results=config_data.get('output', {}).get('save_results', True),
            generate_visualization=config_data.get('output', {}).get('generate_visualization', False)
        )

        # 运行匹配算法
        matcher = Matcher(topology, constraints)
        matching_result = matcher.solve()

        # 创建实验结果
        experiment_result = ExperimentResult.create(experiment_config, matching_result)

        return experiment_result

    def save_results(self, batch_results: BatchExperimentResults, filename: str = "batch_results.json") -> None:
        """
        保存批量实验结果到JSON文件

        参数:
            batch_results: 批量实验结果
            filename: 文件名
        """
        output_path = os.path.join(self.output_dir, filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(batch_results.to_dict(), f, indent=2, ensure_ascii=False)

        print(f"\n批量实验结果已保存至: {output_path}")


class ParametricBatchRunner(BatchRunner):
    """参数化批量实验运行器"""

    def __init__(self, base_config: Dict, param_variations: List[Dict], output_dir: str = "results/parametric/"):
        """
        初始化参数化批量运行器

        参数:
            base_config: 基础配置字典
            param_variations: 参数变化列表，每个元素是一个包含变化参数的字典
            output_dir: 输出目录
        """
        self.base_config = base_config
        self.param_variations = param_variations
        self.output_dir = output_dir
        self.results: List[ExperimentResult] = []

        # 创建输出目录
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    def run(self) -> BatchExperimentResults:
        """
        运行所有参数化实验

        返回:
            BatchExperimentResults对象
        """
        print(f"开始参数化批量实验，共 {len(self.param_variations)} 组参数")
        print("=" * 60)

        for i, variation in enumerate(self.param_variations, 1):
            print(f"\n[{i}/{len(self.param_variations)}] 运行参数组 {i}")
            print(f"参数变化: {variation}")

            try:
                # 合并配置
                config = self._merge_config(self.base_config, variation)

                # 运行实验
                result = self._run_from_config(config, f"Param_{i}")
                self.results.append(result)

                print(f"✓ 实验成功")
                print(f"  - 匹配数: {result.matching_result.num_matches}")
                print(f"  - 频谱利用率: {result.matching_result.spectrum_utilization:.2%}")
                print(f"  - 执行时间: {result.matching_result.execution_time*1000:.2f} ms")

            except Exception as e:
                print(f"✗ 实验失败: {str(e)}")
                error_result = ExperimentResult(
                    config=ExperimentConfig(name=f"Param_{i}"),
                    matching_result=None,
                    timestamp="",
                    success=False,
                    error_message=str(e)
                )
                self.results.append(error_result)

        print("\n" + "=" * 60)
        print("参数化批量实验完成")

        # 创建批量结果对象
        batch_results = BatchExperimentResults.create(self.results)
        return batch_results

    def _merge_config(self, base: Dict, variation: Dict) -> Dict:
        """
        合并基础配置和变化参数

        参数:
            base: 基础配置
            variation: 变化参数

        返回:
            合并后的配置
        """
        import copy
        config = copy.deepcopy(base)

        # 递归更新配置
        def update_dict(d, u):
            for k, v in u.items():
                if isinstance(v, dict):
                    d[k] = update_dict(d.get(k, {}), v)
                else:
                    d[k] = v
            return d

        return update_dict(config, variation)

    def _run_from_config(self, config: Dict, name: str) -> ExperimentResult:
        """
        从配置字典运行实验

        参数:
            config: 配置字典
            name: 实验名称

        返回:
            ExperimentResult对象
        """
        # 构建网络拓扑
        from ..models import SecondaryUser, Channel, PrimaryUser
        import numpy as np

        network_config = config['network']
        num_users = network_config['num_secondary_users']
        num_channels = network_config['num_channels']
        availability_matrix = np.array(network_config['availability_matrix'])

        # 创建次级用户
        secondary_users = []
        for i in range(num_users):
            available_channels = [j for j in range(num_channels) if availability_matrix[i, j] == 1]
            user = SecondaryUser(user_id=i, available_channels=available_channels)
            secondary_users.append(user)

        # 创建信道
        occupied_channels = config.get('primary_users', {}).get('occupied_channels', [])
        channels = []
        for i in range(num_channels):
            channel = Channel(channel_id=i, is_available=(i not in occupied_channels))
            channels.append(channel)

        # 创建主用户
        primary_users = []
        if occupied_channels:
            primary_users.append(PrimaryUser(user_id=0, occupied_channels=occupied_channels))

        # 创建干扰矩阵
        interference_matrix = None
        if 'interference' in config and 'adjacency_matrix' in config['interference']:
            interference_matrix = np.array(config['interference']['adjacency_matrix'])

        # 创建网络拓扑
        topology = NetworkTopology(
            secondary_users=secondary_users,
            channels=channels,
            availability_matrix=availability_matrix,
            primary_users=primary_users,
            interference_matrix=interference_matrix
        )

        # 构建约束条件
        constraints_config = config.get('constraints', {})
        constraints = Constraints(
            enable_availability=constraints_config.get('enable_availability', True),
            enable_single_transceiver=constraints_config.get('enable_single_transceiver', True),
            enable_interference_avoidance=constraints_config.get('enable_interference_avoidance', True)
        )

        # 创建实验配置
        experiment_config = ExperimentConfig(
            name=name,
            description=config.get('metadata', {}).get('description', ''),
            output_dir=self.output_dir,
            save_results=False,
            generate_visualization=False
        )

        # 运行匹配算法
        matcher = Matcher(topology, constraints)
        matching_result = matcher.solve()

        # 创建实验结果
        experiment_result = ExperimentResult.create(experiment_config, matching_result)

        return experiment_result
