"""
结果导出器

将匹配结果导出为JSON文件
"""

import json
import os
from typing import Dict, Any
from ..models import MatchingResult, ExperimentResult, BatchExperimentResults


class ResultExporter:
    """结果导出器"""

    @staticmethod
    def export_matching_result(result: MatchingResult, output_path: str):
        """
        导出匹配结果到JSON文件

        参数:
            result: 匹配结果
            output_path: 输出文件路径
        """
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 转换为字典并导出
        data = result.to_dict()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def export_experiment_result(result: ExperimentResult, output_path: str):
        """
        导出实验结果到JSON文件

        参数:
            result: 实验结果
            output_path: 输出文件路径
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        data = result.to_dict()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def export_batch_results(results: BatchExperimentResults, output_path: str):
        """
        导出批量实验结果到JSON文件

        参数:
            results: 批量实验结果
            output_path: 输出文件路径
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        data = results.to_dict()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
