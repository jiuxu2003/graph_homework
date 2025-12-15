"""
主程序入口

认知无线电频谱分配系统
"""

import argparse
import json
import sys
from .io.config_loader import ConfigLoader
from .io.validator import Validator
from .io.result_exporter import ResultExporter
from .algorithm.matcher import Matcher
from .cli import OutputFormatter, OutputConfig


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='认知无线电频谱分配系统')
    parser.add_argument('--config', '-c', required=True, help='配置文件路径')
    parser.add_argument('--output', '-o', help='输出目录（覆盖配置文件）')
    parser.add_argument('--no-viz', action='store_true', help='不生成可视化图表')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出模式')
    parser.add_argument('--quiet', '-q', action='store_true', help='简洁输出模式')
    parser.add_argument('--no-color', action='store_true', help='禁用颜色输出')
    parser.add_argument('--batch', '-b', action='store_true', help='批量实验模式')

    args = parser.parse_args()

    # 创建输出配置
    output_config = OutputConfig.from_args(args)
    formatter = OutputFormatter(output_config)

    try:
        # 加载配置
        if output_config.verbosity_level == 'verbose':
            print(f"正在加载配置文件: {args.config}")

        config = ConfigLoader.load(args.config)

        # 验证配置
        is_valid, errors = Validator.validate_config(config)
        if not is_valid:
            print("配置文件验证失败:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)

        # 解析网络拓扑和约束条件
        topology = ConfigLoader.parse_network_topology(config)
        constraints = ConfigLoader.parse_constraints(config)

        if output_config.verbosity_level == 'verbose':
            print(f"网络拓扑: {topology.num_users}个用户, {topology.num_channels}个信道")
            print(f"约束条件: 可用性={constraints.enable_availability}, "
                  f"单收发机={constraints.enable_single_transceiver}, "
                  f"避免干扰={constraints.enable_interference_avoidance}")

        # 创建求解器并求解
        matcher = Matcher(topology, constraints)
        result = matcher.solve()

        # 输出结果（使用格式化器）
        print(formatter.format_result(result))

        # 保存结果
        output_settings = config.get('output', {})
        if output_settings.get('save_results', True):
            output_dir = args.output or output_settings.get('output_dir', 'results/')
            output_path = f"{output_dir}/result.json"
            ResultExporter.export_matching_result(result, output_path)
            print(f"\n结果已保存到: {output_path}")

        if output_config.verbosity_level != 'quiet':
            print("\n" + "="*50)
            print("执行完成！")
            print("="*50)

    except FileNotFoundError as e:
        error_msg = formatter.format_error(
            "File Not Found",
            f"配置文件不存在: {args.config}",
            "请检查文件路径是否正确，或使用 --help 查看使用说明"
        )
        print(error_msg)
        sys.exit(1)
    except json.JSONDecodeError as e:
        error_msg = formatter.format_error(
            "JSON Parse Error",
            f"配置文件格式错误: {str(e)}",
            "请检查JSON文件格式是否正确，确保所有括号、引号匹配"
        )
        print(error_msg)
        if output_config.verbosity_level == 'verbose':
            import traceback
            traceback.print_exc()
        sys.exit(1)
    except ValueError as e:
        error_msg = formatter.format_error(
            "Configuration Error",
            f"配置值错误: {str(e)}",
            "请检查配置文件中的数值是否在有效范围内"
        )
        print(error_msg)
        if output_config.verbosity_level == 'verbose':
            import traceback
            traceback.print_exc()
        sys.exit(1)
    except KeyError as e:
        error_msg = formatter.format_error(
            "Configuration Error",
            f"缺少必需的配置项: {str(e)}",
            "请参考示例配置文件，确保所有必需字段都已填写"
        )
        print(error_msg)
        if output_config.verbosity_level == 'verbose':
            import traceback
            traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        error_msg = formatter.format_error(
            "Unexpected Error",
            str(e),
            "如果问题持续存在，请使用 --verbose 选项查看详细错误信息"
        )
        print(error_msg)
        if output_config.verbosity_level == 'verbose':
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
