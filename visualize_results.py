"""
实验结果可视化脚本

生成规模对比实验的可视化图表
"""

import json
import matplotlib.pyplot as plt
import numpy as np
import os

# 配置中文字体
plt.rcParams['font.sans-serif'] = ['Source Han Sans SC', 'DejaVu Sans', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# 注册思源黑体
from matplotlib.font_manager import fontManager
font_path = 'fonts/SourceHanSansSC-Regular.otf'
if os.path.exists(font_path):
    fontManager.addfont(font_path)


def load_results():
    """加载实验结果"""
    with open('results/scale_comparison/summary.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['experiments']


def extract_scale_info(scale_str):
    """从规模字符串中提取用户数和信道数"""
    parts = scale_str.split('×')
    return int(parts[0]), int(parts[1])


def plot_execution_time_vs_scale(experiments):
    """绘制执行时间随规模变化的图表"""
    fig, ax = plt.subplots(figsize=(12, 7))

    # 提取数据
    names = [exp['name'] for exp in experiments]
    scales = [exp['scale'] for exp in experiments]
    times = [exp['result']['execution_time'] * 1000 for exp in experiments]  # 转换为毫秒

    # 计算总节点数（用户数 + 信道数）作为规模指标
    total_nodes = []
    for scale in scales:
        users, channels = extract_scale_info(scale)
        total_nodes.append(users + channels)

    # 创建颜色映射
    colors = plt.cm.viridis(np.linspace(0, 1, len(experiments)))

    # 绘制散点图和折线图
    ax.scatter(total_nodes, times, s=200, c=colors, alpha=0.7, edgecolors='black', linewidth=2, zorder=3)
    ax.plot(total_nodes, times, 'o-', color='steelblue', linewidth=2, markersize=10, alpha=0.5, zorder=2)

    # 添加数据标签
    for i, (x, y, name) in enumerate(zip(total_nodes, times, names)):
        ax.annotate(f'{y:.3f}ms',
                   xy=(x, y),
                   xytext=(0, 10),
                   textcoords='offset points',
                   ha='center',
                   fontsize=9,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor=colors[i], alpha=0.3))

    ax.set_xlabel('网络规模（用户数 + 信道数）', fontsize=13, fontweight='bold')
    ax.set_ylabel('执行时间 (ms)', fontsize=13, fontweight='bold')
    ax.set_title('匈牙利算法执行时间随网络规模变化', fontsize=15, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')

    # 添加趋势线
    z = np.polyfit(total_nodes, times, 2)
    p = np.poly1d(z)
    x_trend = np.linspace(min(total_nodes), max(total_nodes), 100)
    ax.plot(x_trend, p(x_trend), '--', color='red', linewidth=2, alpha=0.5, label='二次拟合趋势线')

    ax.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig('results/scale_comparison/chart_execution_time.png', dpi=300, bbox_inches='tight')
    print("✓ 已生成: chart_execution_time.png")
    plt.close()


def plot_spectrum_utilization(experiments):
    """绘制频谱利用率对比图"""
    fig, ax = plt.subplots(figsize=(14, 7))

    # 提取数据
    names = [exp['name'] for exp in experiments]
    utilizations = [exp['result']['spectrum_utilization'] * 100 for exp in experiments]
    matches = [exp['result']['num_matches'] for exp in experiments]

    x = np.arange(len(names))
    width = 0.6

    # 创建颜色映射（根据利用率）
    colors = ['#2ecc71' if u == 100 else '#e74c3c' for u in utilizations]

    # 绘制柱状图
    bars = ax.bar(x, utilizations, width, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

    # 添加数据标签
    for i, (bar, util, match) in enumerate(zip(bars, utilizations, matches)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
               f'{util:.1f}%\n({match}匹配)',
               ha='center', va='bottom', fontsize=10, fontweight='bold')

    # 添加100%参考线
    ax.axhline(y=100, color='green', linestyle='--', linewidth=2, alpha=0.5, label='100%利用率')

    ax.set_xlabel('实验场景', fontsize=13, fontweight='bold')
    ax.set_ylabel('频谱利用率 (%)', fontsize=13, fontweight='bold')
    ax.set_title('不同场景下的频谱利用率对比', fontsize=15, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha='right', fontsize=10)
    ax.set_ylim(0, 115)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.legend(fontsize=11)

    plt.tight_layout()
    plt.savefig('results/scale_comparison/chart_utilization.png', dpi=300, bbox_inches='tight')
    print("✓ 已生成: chart_utilization.png")
    plt.close()


def plot_matches_comparison(experiments):
    """绘制匹配数对比图"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # 提取数据
    names = [exp['name'] for exp in experiments]
    scales = [exp['scale'] for exp in experiments]
    matches = [exp['result']['num_matches'] for exp in experiments]

    # 计算用户数和信道数
    users_list = []
    channels_list = []
    for scale in scales:
        users, channels = extract_scale_info(scale)
        users_list.append(users)
        channels_list.append(channels)

    # 左图：匹配数柱状图
    x = np.arange(len(names))
    colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(experiments)))

    bars = ax1.bar(x, matches, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

    for bar, match in zip(bars, matches):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{int(match)}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax1.set_xlabel('实验场景', fontsize=12, fontweight='bold')
    ax1.set_ylabel('匹配数', fontsize=12, fontweight='bold')
    ax1.set_title('各场景匹配数对比', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, rotation=45, ha='right', fontsize=9)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')

    # 右图：用户数、信道数、匹配数对比
    x2 = np.arange(len(names))
    width = 0.25

    bars1 = ax2.bar(x2 - width, users_list, width, label='用户数', color='#3498db', alpha=0.8)
    bars2 = ax2.bar(x2, channels_list, width, label='信道数', color='#2ecc71', alpha=0.8)
    bars3 = ax2.bar(x2 + width, matches, width, label='匹配数', color='#e74c3c', alpha=0.8)

    ax2.set_xlabel('实验场景', fontsize=12, fontweight='bold')
    ax2.set_ylabel('数量', fontsize=12, fontweight='bold')
    ax2.set_title('用户数、信道数与匹配数关系', fontsize=14, fontweight='bold')
    ax2.set_xticks(x2)
    ax2.set_xticklabels(names, rotation=45, ha='right', fontsize=9)
    ax2.legend(fontsize=11)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig('results/scale_comparison/chart_matches.png', dpi=300, bbox_inches='tight')
    print("✓ 已生成: chart_matches.png")
    plt.close()


def plot_performance_summary(experiments):
    """绘制性能综合对比图"""
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

    names = [exp['name'] for exp in experiments]
    scales = [exp['scale'] for exp in experiments]
    times = [exp['result']['execution_time'] * 1000 for exp in experiments]
    utilizations = [exp['result']['spectrum_utilization'] * 100 for exp in experiments]
    matches = [exp['result']['num_matches'] for exp in experiments]

    # 计算总节点数
    total_nodes = []
    for scale in scales:
        users, channels = extract_scale_info(scale)
        total_nodes.append(users + channels)

    # 1. 执行时间 vs 规模（散点图）
    ax1 = fig.add_subplot(gs[0, 0])
    scatter = ax1.scatter(total_nodes, times, s=300, c=times, cmap='YlOrRd',
                         alpha=0.7, edgecolors='black', linewidth=2)
    ax1.plot(total_nodes, times, 'o-', color='gray', linewidth=1, alpha=0.3)
    ax1.set_xlabel('网络规模（节点总数）', fontsize=11, fontweight='bold')
    ax1.set_ylabel('执行时间 (ms)', fontsize=11, fontweight='bold')
    ax1.set_title('执行时间 vs 网络规模', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax1, label='执行时间 (ms)')

    # 2. 频谱利用率（饼图）
    ax2 = fig.add_subplot(gs[0, 1])
    util_100 = sum(1 for u in utilizations if u == 100)
    util_other = len(utilizations) - util_100
    sizes = [util_100, util_other] if util_other > 0 else [util_100]
    labels = ['100%利用率', '< 100%利用率'] if util_other > 0 else ['100%利用率']
    colors_pie = ['#2ecc71', '#e74c3c'] if util_other > 0 else ['#2ecc71']
    explode = (0.1, 0) if util_other > 0 else (0.1,)

    ax2.pie(sizes, explode=explode, labels=labels, colors=colors_pie,
           autopct='%1.1f%%', shadow=True, startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
    ax2.set_title(f'频谱利用率分布\n(共{len(experiments)}个实验)', fontsize=12, fontweight='bold')

    # 3. 匹配数趋势（折线图）
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(range(len(names)), matches, 'o-', color='#3498db', linewidth=3,
            markersize=10, markerfacecolor='white', markeredgewidth=2, markeredgecolor='#3498db')
    ax3.fill_between(range(len(names)), matches, alpha=0.3, color='#3498db')
    ax3.set_xlabel('实验序号', fontsize=11, fontweight='bold')
    ax3.set_ylabel('匹配数', fontsize=11, fontweight='bold')
    ax3.set_title('匹配数变化趋势', fontsize=12, fontweight='bold')
    ax3.set_xticks(range(len(names)))
    ax3.set_xticklabels([f'实验{i+1}' for i in range(len(names))], fontsize=9)
    ax3.grid(True, alpha=0.3)

    # 4. 性能指标雷达图
    ax4 = fig.add_subplot(gs[1, 1], projection='polar')

    # 归一化指标（0-1范围）
    norm_time = 1 - (np.array(times) / max(times))  # 时间越短越好
    norm_util = np.array(utilizations) / 100
    norm_matches = np.array(matches) / max(matches)

    # 计算平均值
    avg_metrics = [
        np.mean(norm_time),
        np.mean(norm_util),
        np.mean(norm_matches)
    ]

    categories = ['执行速度', '频谱利用率', '匹配效率']
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    avg_metrics += avg_metrics[:1]
    angles += angles[:1]

    ax4.plot(angles, avg_metrics, 'o-', linewidth=3, color='#9b59b6', markersize=10)
    ax4.fill(angles, avg_metrics, alpha=0.25, color='#9b59b6')
    ax4.set_xticks(angles[:-1])
    ax4.set_xticklabels(categories, fontsize=11, fontweight='bold')
    ax4.set_ylim(0, 1)
    ax4.set_title('平均性能指标', fontsize=12, fontweight='bold', pad=20)
    ax4.grid(True)

    plt.suptitle('匈牙利算法性能综合分析', fontsize=16, fontweight='bold', y=0.98)
    plt.savefig('results/scale_comparison/chart_performance_summary.png', dpi=300, bbox_inches='tight')
    print("✓ 已生成: chart_performance_summary.png")
    plt.close()


def main():
    """主函数"""
    print("=" * 80)
    print("生成实验结果可视化图表")
    print("=" * 80)
    print()

    # 加载实验结果
    experiments = load_results()
    print(f"已加载 {len(experiments)} 个实验结果")
    print()

    # 生成各类图表
    print("正在生成图表...")
    print()

    plot_execution_time_vs_scale(experiments)
    plot_spectrum_utilization(experiments)
    plot_matches_comparison(experiments)
    plot_performance_summary(experiments)

    print()
    print("=" * 80)
    print("所有图表生成完成！")
    print("=" * 80)
    print()
    print("生成的图表文件：")
    print("  1. chart_execution_time.png - 执行时间随规模变化")
    print("  2. chart_utilization.png - 频谱利用率对比")
    print("  3. chart_matches.png - 匹配数对比")
    print("  4. chart_performance_summary.png - 性能综合分析")
    print()
    print("所有图表已保存到: results/scale_comparison/")
    print()


if __name__ == '__main__':
    main()
