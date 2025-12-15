# 认知无线电频谱分配系统

基于匈牙利算法的认知无线电网络频谱资源动态分配系统

## 项目简介

本项目实现了匈牙利算法（Hungarian Algorithm）用于求解认知无线电网络中的频谱资源动态分配问题。系统将二部图最大匹配理论应用于通信领域，支持多种约束条件，并提供图形化的结果展示。

## 核心功能

- ✅ 匈牙利算法求解二部图最大匹配
- ✅ 支持可用性约束、单收发机限制、避免同频干扰
- ✅ JSON配置文件输入
- ✅ 图形界面展示结果（matplotlib）
- ✅ 批量实验模式
- ✅ 性能对比分析
- ✅ 美化的CLI输出（彩色输出、格式化表格、进度跟踪）

## 环境要求

- Python 3.8+ （推荐3.10+）
- Anaconda/Miniconda

## 安装步骤

### 1. 创建并激活conda环境

```bash
conda create -n graph_homework python=3.10 -y
conda activate graph_homework
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 验证安装

```bash
python -c "import numpy; import matplotlib; print('安装成功！')"
```

## 快速开始

### 运行简单示例

```bash
python src/main.py --config configs/examples/simple_3x3.json
```

### 批量实验

```bash
python src/main.py --config configs/examples/batch_experiment.json --batch
```

## 命令行选项

系统支持多种命令行参数来控制输出格式和详细程度：

### 基本选项

- `--config, -c`: 配置文件路径（必需）
- `--output, -o`: 输出目录（可选，覆盖配置文件中的设置）
- `--batch, -b`: 批量实验模式

### 输出控制

- `--verbose, -v`: 详细输出模式，显示额外的调试信息和统计数据
- `--quiet, -q`: 简洁输出模式，仅显示关键指标
- `--no-color`: 禁用彩色输出（在输出重定向时自动禁用）
- `--no-viz`: 不生成可视化图表

### 使用示例

**详细模式**（显示完整的调试信息）：
```bash
python src/main.py --config configs/examples/simple_3x3.json --verbose
```

**简洁模式**（仅显示关键指标）：
```bash
python src/main.py --config configs/examples/simple_3x3.json --quiet
```

**禁用颜色**（适用于日志文件或不支持颜色的终端）：
```bash
python src/main.py --config configs/examples/simple_3x3.json --no-color
```

**输出重定向**（颜色和进度自动禁用）：
```bash
python src/main.py --config configs/examples/simple_3x3.json > output.log
```

## 输出格式

系统提供三种输出详细程度：

### 简洁模式（--quiet）
单行输出，包含关键指标：
```
Matches: 3, Utilization: 100.0%, Time: 0.123ms
```

### 标准模式（默认）
格式化的表格输出，包含：
- 最大匹配数
- 频谱利用率
- 算法运行时间
- 约束条件满足情况
- 匹配方案表格

### 详细模式（--verbose）
包含标准模式的所有信息，额外显示：
- 匹配和未匹配的用户ID列表
- 匹配和未匹配的信道ID列表
- 网络拓扑详细信息
- 约束条件详细配置

## 项目结构

```
src/
├── algorithm/          # 匈牙利算法核心实现
├── models/            # 数据模型
├── io/                # 配置加载和结果导出
├── cli/               # CLI美化模块（颜色、格式化、进度跟踪）
├── visualization/     # 图形界面
├── experiments/       # 批量实验
└── main.py           # 主程序入口

tests/                 # 测试文件
configs/examples/      # 配置示例
results/              # 结果输出
```

## 文档

- [快速开始指南](specs/001-spectrum-allocation/quickstart.md)
- [实现计划](specs/001-spectrum-allocation/plan.md)
- [数据模型](specs/001-spectrum-allocation/data-model.md)

## 许可证

本项目用于学术研究和教学目的。
