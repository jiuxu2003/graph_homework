"""
生成大规模测试配置文件

用于创建50×30和100×50规模的测试用例
"""

import json
import numpy as np
import os


def generate_availability_matrix(num_users, num_channels, density=0.3):
    """
    生成可用性矩阵

    参数:
        num_users: 用户数
        num_channels: 信道数
        density: 密度（0-1之间，表示可用性的比例）

    返回:
        可用性矩阵（列表形式）
    """
    np.random.seed(42)  # 固定随机种子以保证可重复性
    matrix = np.random.rand(num_users, num_channels) < density

    # 确保每个用户至少有一个可用信道
    for i in range(num_users):
        if not matrix[i].any():
            matrix[i, np.random.randint(num_channels)] = True

    # 确保每个信道至少有一个用户可以访问
    for j in range(num_channels):
        if not matrix[:, j].any():
            matrix[np.random.randint(num_users), j] = True

    return matrix.astype(int).tolist()


def generate_chain_interference(num_users):
    """
    生成链式干扰矩阵（每个用户与相邻的2-3个用户干扰）

    参数:
        num_users: 用户数

    返回:
        干扰矩阵（列表形式）
    """
    matrix = np.zeros((num_users, num_users), dtype=int)

    for i in range(num_users):
        # 与前后各1-2个用户相邻
        for offset in [1, 2]:
            if i + offset < num_users:
                matrix[i, i + offset] = 1
                matrix[i + offset, i] = 1

    return matrix.tolist()


def generate_config(name, description, num_users, num_channels,
                    density, primary_occupied_ratio, output_dir):
    """
    生成配置文件

    参数:
        name: 配置名称
        description: 描述
        num_users: 用户数
        num_channels: 信道数
        density: 可用性密度
        primary_occupied_ratio: 主用户占用比例
        output_dir: 输出目录
    """
    # 生成可用性矩阵
    availability_matrix = generate_availability_matrix(num_users, num_channels, density)

    # 生成干扰矩阵
    interference_matrix = generate_chain_interference(num_users)

    # 生成主用户占用列表
    num_occupied = int(num_channels * primary_occupied_ratio)
    np.random.seed(42)
    occupied_channels = sorted(np.random.choice(num_channels, num_occupied, replace=False).tolist())

    # 构建配置
    config = {
        "metadata": {
            "name": name,
            "description": description
        },
        "network": {
            "num_secondary_users": num_users,
            "num_channels": num_channels,
            "availability_matrix": availability_matrix
        },
        "primary_users": {
            "occupied_channels": occupied_channels
        },
        "interference": {
            "adjacency_matrix": interference_matrix
        },
        "constraints": {
            "enable_availability": True,
            "enable_single_transceiver": True,
            "enable_interference_avoidance": False
        },
        "output": {
            "save_results": True,
            "output_dir": output_dir,
            "generate_visualization": False
        }
    }

    return config


def main():
    """主函数"""
    # 确保输出目录存在
    os.makedirs("configs/experiments", exist_ok=True)

    # 配置列表
    configs = [
        {
            "filename": "configs/experiments/large_50x30_ideal.json",
            "name": "大规模-理想场景(50×30)",
            "description": "50用户30信道，中等密度可用性，少量主用户占用",
            "num_users": 50,
            "num_channels": 30,
            "density": 0.4,
            "primary_occupied_ratio": 0.1,
            "output_dir": "results/scale_comparison/"
        },
        {
            "filename": "configs/experiments/large_50x30_heavy.json",
            "name": "大规模-重负载场景(50×30)",
            "description": "50用户30信道，稀疏可用性，高主用户占用率",
            "num_users": 50,
            "num_channels": 30,
            "density": 0.25,
            "primary_occupied_ratio": 0.3,
            "output_dir": "results/scale_comparison/"
        },
        {
            "filename": "configs/experiments/xlarge_100x50_ideal.json",
            "name": "超大规模-理想场景(100×50)",
            "description": "100用户50信道，中等密度可用性，测试算法可扩展性",
            "num_users": 100,
            "num_channels": 50,
            "density": 0.35,
            "primary_occupied_ratio": 0.15,
            "output_dir": "results/scale_comparison/"
        }
    ]

    # 生成配置文件
    for cfg in configs:
        config = generate_config(
            name=cfg["name"],
            description=cfg["description"],
            num_users=cfg["num_users"],
            num_channels=cfg["num_channels"],
            density=cfg["density"],
            primary_occupied_ratio=cfg["primary_occupied_ratio"],
            output_dir=cfg["output_dir"]
        )

        # 保存到文件
        with open(cfg["filename"], 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"✓ 已生成: {cfg['filename']}")
        print(f"  - 用户数: {cfg['num_users']}, 信道数: {cfg['num_channels']}")
        print(f"  - 可用性密度: {cfg['density']:.0%}, 主用户占用: {cfg['primary_occupied_ratio']:.0%}")
        print()

    print("所有大规模配置文件生成完成！")


if __name__ == '__main__':
    main()
