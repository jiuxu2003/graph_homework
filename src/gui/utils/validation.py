"""
参数验证工具

提供配置验证和参数范围检查功能。
"""

from typing import List, Any, Optional
from pathlib import Path
import json


class ValidationError(Exception):
    """验证错误异常"""
    pass


class Validator:
    """参数验证器"""

    @staticmethod
    def validate_positive_integer(value: Any, name: str) -> int:
        """
        验证正整数

        Args:
            value: 要验证的值
            name: 参数名称（用于错误消息）

        Returns:
            int: 验证后的整数值

        Raises:
            ValidationError: 如果验证失败
        """
        try:
            int_value = int(value)
            if int_value <= 0:
                raise ValidationError(f"{name}必须是正整数（当前值: {value}）")
            return int_value
        except (TypeError, ValueError):
            raise ValidationError(f"{name}必须是有效的整数（当前值: {value}）")

    @staticmethod
    def validate_non_negative_integer(value: Any, name: str) -> int:
        """
        验证非负整数

        Args:
            value: 要验证的值
            name: 参数名称（用于错误消息）

        Returns:
            int: 验证后的整数值

        Raises:
            ValidationError: 如果验证失败
        """
        try:
            int_value = int(value)
            if int_value < 0:
                raise ValidationError(f"{name}不能是负数（当前值: {value}）")
            return int_value
        except (TypeError, ValueError):
            raise ValidationError(f"{name}必须是有效的整数（当前值: {value}）")

    @staticmethod
    def validate_range(value: Any, name: str, min_val: float, max_val: float) -> float:
        """
        验证数值范围

        Args:
            value: 要验证的值
            name: 参数名称
            min_val: 最小值
            max_val: 最大值

        Returns:
            float: 验证后的数值

        Raises:
            ValidationError: 如果验证失败
        """
        try:
            float_value = float(value)
            if not (min_val <= float_value <= max_val):
                raise ValidationError(
                    f"{name}必须在{min_val}到{max_val}之间（当前值: {value}）"
                )
            return float_value
        except (TypeError, ValueError):
            raise ValidationError(f"{name}必须是有效的数值（当前值: {value}）")

    @staticmethod
    def validate_file_path(path: Any, name: str, must_exist: bool = True) -> Path:
        """
        验证文件路径

        Args:
            path: 要验证的路径
            name: 参数名称
            must_exist: 文件是否必须存在

        Returns:
            Path: 验证后的路径对象

        Raises:
            ValidationError: 如果验证失败
        """
        try:
            path_obj = Path(path)

            if must_exist and not path_obj.exists():
                raise ValidationError(f"{name}不存在: {path}")

            if must_exist and not path_obj.is_file():
                raise ValidationError(f"{name}不是有效的文件: {path}")

            return path_obj
        except (TypeError, ValueError) as e:
            raise ValidationError(f"{name}路径无效: {e}")

    @staticmethod
    def validate_directory_path(path: Any, name: str, create_if_missing: bool = False) -> Path:
        """
        验证目录路径

        Args:
            path: 要验证的路径
            name: 参数名称
            create_if_missing: 如果目录不存在是否创建

        Returns:
            Path: 验证后的路径对象

        Raises:
            ValidationError: 如果验证失败
        """
        try:
            path_obj = Path(path)

            if not path_obj.exists():
                if create_if_missing:
                    path_obj.mkdir(parents=True, exist_ok=True)
                else:
                    raise ValidationError(f"{name}不存在: {path}")

            if path_obj.exists() and not path_obj.is_dir():
                raise ValidationError(f"{name}不是有效的目录: {path}")

            return path_obj
        except (TypeError, ValueError) as e:
            raise ValidationError(f"{name}路径无效: {e}")

    @staticmethod
    def validate_json_file(file_path: Path, name: str) -> dict:
        """
        验证并加载JSON文件

        Args:
            file_path: JSON文件路径
            name: 参数名称

        Returns:
            dict: 解析后的JSON数据

        Raises:
            ValidationError: 如果验证失败
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValidationError(f"{name}格式错误: {e}")
        except Exception as e:
            raise ValidationError(f"无法读取{name}: {e}")

    @staticmethod
    def validate_config_structure(config: dict, name: str) -> List[str]:
        """
        验证配置文件结构（兼容CLI格式）

        Args:
            config: 配置字典
            name: 配置名称

        Returns:
            List[str]: 错误消息列表（空列表表示验证通过）
        """
        errors = []

        # 检查必需的顶层字段（使用CLI格式）
        if 'network' not in config:
            errors.append("缺少必需字段: network")

        # 验证network结构
        if 'network' in config:
            network = config['network']
            if not isinstance(network, dict):
                errors.append("network必须是字典类型")
            else:
                # 检查必需字段（兼容两种命名）
                has_users = 'num_secondary_users' in network or 'num_users' in network
                if not has_users:
                    errors.append("network缺少num_secondary_users或num_users字段")

                if 'num_channels' not in network:
                    errors.append("network缺少num_channels字段")

                if 'availability_matrix' not in network:
                    errors.append("network缺少availability_matrix字段")

        # 验证constraints结构（可选）
        if 'constraints' in config:
            constraints = config['constraints']
            if not isinstance(constraints, dict):
                errors.append("constraints必须是字典类型")

        # 验证output结构（可选）
        if 'output' in config:
            output = config['output']
            if not isinstance(output, dict):
                errors.append("output必须是字典类型")

        return errors


def validate_experiment_config(config_file: Path) -> tuple[Optional[dict], List[str]]:
    """
    验证实验配置文件

    Args:
        config_file: 配置文件路径

    Returns:
        tuple: (配置字典, 错误列表)
               如果验证成功，返回(config, [])
               如果验证失败，返回(None, errors)
    """
    errors = []

    # 验证文件存在
    try:
        Validator.validate_file_path(config_file, "配置文件", must_exist=True)
    except ValidationError as e:
        return None, [str(e)]

    # 验证JSON格式
    try:
        config = Validator.validate_json_file(config_file, "配置文件")
    except ValidationError as e:
        return None, [str(e)]

    # 验证配置结构
    structure_errors = Validator.validate_config_structure(config, "配置文件")
    if structure_errors:
        return None, structure_errors

    return config, []
