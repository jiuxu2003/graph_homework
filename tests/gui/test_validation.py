"""
测试参数验证工具
"""

import pytest
from pathlib import Path
import tempfile
import json

from src.gui.utils.validation import (
    Validator,
    ValidationError,
    validate_experiment_config
)


class TestValidator:
    """测试Validator类"""

    def test_validate_positive_integer_valid(self):
        """测试验证正整数（有效值）"""
        assert Validator.validate_positive_integer(5, "test") == 5
        assert Validator.validate_positive_integer("10", "test") == 10

    def test_validate_positive_integer_invalid(self):
        """测试验证正整数（无效值）"""
        with pytest.raises(ValidationError, match="必须是正整数"):
            Validator.validate_positive_integer(0, "test")

        with pytest.raises(ValidationError, match="必须是正整数"):
            Validator.validate_positive_integer(-5, "test")

        with pytest.raises(ValidationError, match="必须是有效的整数"):
            Validator.validate_positive_integer("abc", "test")

    def test_validate_non_negative_integer_valid(self):
        """测试验证非负整数（有效值）"""
        assert Validator.validate_non_negative_integer(0, "test") == 0
        assert Validator.validate_non_negative_integer(5, "test") == 5

    def test_validate_non_negative_integer_invalid(self):
        """测试验证非负整数（无效值）"""
        with pytest.raises(ValidationError, match="不能是负数"):
            Validator.validate_non_negative_integer(-1, "test")

    def test_validate_range_valid(self):
        """测试验证数值范围（有效值）"""
        assert Validator.validate_range(5.5, "test", 0, 10) == 5.5
        assert Validator.validate_range("3.14", "test", 0, 10) == 3.14

    def test_validate_range_invalid(self):
        """测试验证数值范围（无效值）"""
        with pytest.raises(ValidationError, match="必须在"):
            Validator.validate_range(15, "test", 0, 10)

        with pytest.raises(ValidationError, match="必须在"):
            Validator.validate_range(-5, "test", 0, 10)

    def test_validate_file_path_valid(self):
        """测试验证文件路径（有效值）"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name

        try:
            result = Validator.validate_file_path(temp_path, "test", must_exist=True)
            assert isinstance(result, Path)
            assert result.exists()
        finally:
            Path(temp_path).unlink()

    def test_validate_file_path_not_exist(self):
        """测试验证文件路径（文件不存在）"""
        with pytest.raises(ValidationError, match="不存在"):
            Validator.validate_file_path("/nonexistent/file.txt", "test", must_exist=True)

    def test_validate_directory_path_valid(self):
        """测试验证目录路径（有效值）"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = Validator.validate_directory_path(temp_dir, "test")
            assert isinstance(result, Path)
            assert result.is_dir()

    def test_validate_directory_path_create(self):
        """测试验证目录路径（自动创建）"""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = Path(temp_dir) / "new_subdir"
            result = Validator.validate_directory_path(new_dir, "test", create_if_missing=True)
            assert result.exists()
            assert result.is_dir()

    def test_validate_json_file_valid(self):
        """测试验证JSON文件（有效值）"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"key": "value"}, f)
            temp_path = f.name

        try:
            result = Validator.validate_json_file(Path(temp_path), "test")
            assert result == {"key": "value"}
        finally:
            Path(temp_path).unlink()

    def test_validate_json_file_invalid(self):
        """测试验证JSON文件（无效格式）"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json")
            temp_path = f.name

        try:
            with pytest.raises(ValidationError, match="格式错误"):
                Validator.validate_json_file(Path(temp_path), "test")
        finally:
            Path(temp_path).unlink()

    def test_validate_config_structure_valid(self):
        """测试验证配置结构（有效配置）"""
        config = {
            "network_topology": {
                "num_users": 10,
                "num_channels": 5,
                "availability_matrix": [[1, 0], [0, 1]]
            },
            "constraints": {
                "max_channels_per_user": 2
            },
            "output": {
                "save_result": True
            }
        }

        errors = Validator.validate_config_structure(config, "test")
        assert errors == []

    def test_validate_config_structure_missing_fields(self):
        """测试验证配置结构（缺少字段）"""
        config = {
            "network_topology": {
                "num_users": 10
            }
        }

        errors = Validator.validate_config_structure(config, "test")
        assert len(errors) > 0
        assert any("缺少必需字段" in err for err in errors)


class TestValidateExperimentConfig:
    """测试validate_experiment_config函数"""

    def test_validate_experiment_config_valid(self):
        """测试验证实验配置（有效配置）"""
        valid_config = {
            "name": "test_experiment",
            "network_topology": {
                "num_users": 10,
                "num_channels": 5,
                "availability_matrix": [[1, 0], [0, 1]]
            },
            "constraints": {
                "max_channels_per_user": 2
            },
            "output": {
                "save_result": True
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(valid_config, f)
            temp_path = f.name

        try:
            config, errors = validate_experiment_config(Path(temp_path))
            assert config is not None
            assert errors == []
            assert config["name"] == "test_experiment"
        finally:
            Path(temp_path).unlink()

    def test_validate_experiment_config_file_not_exist(self):
        """测试验证实验配置（文件不存在）"""
        config, errors = validate_experiment_config(Path("/nonexistent/config.json"))
        assert config is None
        assert len(errors) > 0
        assert any("不存在" in err for err in errors)

    def test_validate_experiment_config_invalid_json(self):
        """测试验证实验配置（无效JSON）"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json")
            temp_path = f.name

        try:
            config, errors = validate_experiment_config(Path(temp_path))
            assert config is None
            assert len(errors) > 0
        finally:
            Path(temp_path).unlink()
