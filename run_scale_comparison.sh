#!/bin/bash

# 规模对比实验运行脚本

echo "================================================================================"
echo "匈牙利算法规模对比实验"
echo "================================================================================"
echo ""

# 创建输出目录
mkdir -p results/scale_comparison

# 定义实验配置列表
declare -a configs=(
    "configs/experiments/small_5x5_ideal.json"
    "configs/experiments/small_5x8_sparse.json"
    "configs/experiments/medium_10x10_ideal.json"
    "configs/experiments/medium_15x10_compete.json"
    "configs/experiments/medium_20x15_sparse.json"
    "configs/experiments/large_50x30_ideal.json"
    "configs/experiments/large_50x30_heavy.json"
    "configs/experiments/xlarge_100x50_ideal.json"
)

declare -a names=(
    "小规模-理想(5×5)"
    "小规模-稀疏(5×8)"
    "中规模-理想(10×10)"
    "中规模-竞争(15×10)"
    "中规模-稀疏(20×15)"
    "大规模-理想(50×30)"
    "大规模-重负载(50×30)"
    "超大规模-理想(100×50)"
)

# 运行每个实验
total=${#configs[@]}
success=0
failed=0

echo "开始运行 $total 个实验..."
echo ""

for i in "${!configs[@]}"; do
    config="${configs[$i]}"
    name="${names[$i]}"

    echo "[$((i+1))/$total] 运行实验: $name"
    echo "配置文件: $config"

    # 运行实验
    if conda run -n graph_homework python -m src.main --config "$config" --output results/scale_comparison/ > /dev/null 2>&1; then
        echo "✓ 实验成功"
        ((success++))
    else
        echo "✗ 实验失败"
        ((failed++))
    fi
    echo ""
done

echo "================================================================================"
echo "实验完成！"
echo "================================================================================"
echo ""
echo "实验摘要："
echo "  总实验数: $total"
echo "  成功实验: $success"
echo "  失败实验: $failed"
echo "  成功率: $(awk "BEGIN {printf \"%.1f%%\", ($success/$total)*100}")"
echo ""
echo "所有结果已保存到: results/scale_comparison/"
echo ""
echo "查看详细结果："
echo "  ls -lh results/scale_comparison/"
echo ""
