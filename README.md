# 认知无线电频谱分配系统

基于匈牙利算法的认知无线电网络频谱资源动态分配系统

## 项目简介

本项目实现了匈牙利算法（Hungarian Algorithm）用于求解认知无线电网络中的频谱资源动态分配问题。系统将二部图最大匹配理论应用于通信领域，支持多种约束条件，并提供CLI工具和图形化GUI界面。

## 核心功能

### Phase 1-2: 核心算法与CLI
- ✅ 匈牙利算法求解二部图最大匹配
- ✅ 支持可用性约束、单收发机限制、避免同频干扰
- ✅ JSON配置文件输入（支持简化矩阵格式）
- ✅ 批量实验模式
- ✅ 性能对比分析
- ✅ 美化的CLI输出（彩色输出、格式化表格、进度跟踪）
- ✅ 双频谱利用率指标（可用 vs 总体）

### Phase 3: 交互式GUI（新增）
- ✅ 完整的Tkinter GUI界面
  - 配置面板（加载/快速生成配置）
  - 参数面板（查看/修改参数）
  - 结果面板（关键指标展示）
  - 可视化面板（匹配矩阵、利用率图、统计汇总）
- ✅ CLI-GUI分离架构（subprocess调用）
- ✅ 实时可视化图表
- ✅ 结果导出功能

## 环境要求

- Python 3.10+
- Anaconda/Miniconda（推荐）

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

### CLI模式

**运行简单示例：**
```bash
python -m src.main --config configs/examples/basic_3x3.json
```

**运行大规模测试：**
```bash
python -m src.main --config configs/examples/realistic_50x30_heavy.json
```

**批量实验：**
```bash
python -m src.main --config configs/examples/batch_experiment.json --batch
```

### GUI模式（新增）

**启动图形界面：**
```bash
python src/gui_main.py
```

GUI功能：
- 加载JSON配置或快速生成配置
- 实时查看实验参数
- 运行实验并查看结果
- 可视化展示（匹配矩阵、利用率对比、统计汇总）
- 导出结果和图表

## 命令行选项

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
python -m src.main --config configs/examples/basic_3x3.json --verbose
```

**简洁模式**（仅显示关键指标）：
```bash
python -m src.main --config configs/examples/basic_3x3.json --quiet
```

**禁用颜色**（适用于日志文件或不支持颜色的终端）：
```bash
python -m src.main --config configs/examples/basic_3x3.json --no-color
```

**输出重定向**（颜色和进度自动禁用）：
```bash
python -m src.main --config configs/examples/basic_3x3.json > output.log
```

## 实验结果示例

### 现实场景测试（50用户 × 30信道）

**配置：**
- 50个次级用户
- 30个信道（14个被主用户占用）
- 可用信道：16个
- 稀疏可用性矩阵（30%连接概率）

**结果：**
```
✓ Maximum Matches: 16
✓ Available Spectrum Utilization: 100.00% (16/16)
✓ Total Spectrum Utilization: 53.33% (16/30)
⏱ Algorithm Runtime: ~3ms
✓ Primary User Occupied Channels: 14
```

**关键发现：**
- 可用频谱利用率：100%（完全利用可用资源）
- 总体频谱利用率：53.3%（考虑主用户占用）
- 未匹配用户：34个（68%）- 反映资源稀缺性

## 项目结构

```
graph_homework/
├── src/
│   ├── algorithm/          # 匈牙利算法核心实现
│   ├── models/            # 数据模型
│   ├── io/                # 配置加载和结果导出
│   ├── cli/               # CLI美化模块
│   ├── gui/               # GUI模块（新增）
│   │   ├── components/   # UI组件
│   │   ├── controllers/  # 业务控制器
│   │   ├── models/       # GUI状态模型
│   │   └── utils/        # 工具函数
│   ├── visualization/     # 图形界面
│   ├── experiments/       # 批量实验
│   ├── main.py           # CLI入口
│   └── gui_main.py       # GUI入口（新增）
│
├── configs/examples/      # 配置示例
│   ├── basic_3x3.json
│   ├── medium_10x8.json
│   └── realistic_50x30_heavy.json
│
├── tests/                 # 测试文件
├── results/              # 结果输出
└── HANDOVER_TO_GEMINI.md # 技术交接文档
```

## 配置文件格式

### 标准JSON格式

```json
{
  "network": {
    "num_secondary_users": 50,
    "num_channels": 30,
    "availability_matrix": [[1,0,1,...], ...]
  },
  "primary_users": {
    "occupied_channels": [1, 3, 5, ...]
  },
  "interference": {
    "adjacency_matrix": [[0,1,0,...], ...]
  }
}
```

### 简化字符串格式（支持）

```json
{
  "network": {
    "num_secondary_users": 50,
    "num_channels": 30,
    "availability_matrix": "random_sparse_0.3"
  },
  "primary_users": {
    "occupied_channels": [1, 3, 5, ...]
  },
  "interference": {
    "adjacency_matrix": "chain"
  }
}
```

支持的简化格式：
- **可用性矩阵**: `all_ones`, `random_sparse_X`, `random_dense_X`
- **干扰矩阵**: `chain`, `ring`, `complete`

## 技术特性

### 双频谱利用率指标

系统提供两个利用率指标：

1. **可用频谱利用率** = 匹配数 / 可用信道数
   - 衡量对可用资源的利用效率
   - 反映算法性能

2. **总体频谱利用率** = 匹配数 / 总信道数
   - 衡量整体频谱使用情况
   - 考虑主用户占用影响

### CLI-GUI分离架构

- GUI通过subprocess调用CLI
- 避免模块导入冲突
- 确保结果一致性
- 支持后台任务执行

## 文档

- [技术交接文档](HANDOVER_TO_GEMINI.md) - 面向Gemini AI的技术交接文档
- [快速开始指南](specs/001-spectrum-allocation/quickstart.md)
- [实现计划](specs/001-spectrum-allocation/plan.md)
- [数据模型](specs/001-spectrum-allocation/data-model.md)
- [GUI设计](specs/003-interactive-gui/)

## 项目阶段

- ✅ **Phase 1**: 核心算法实现（匈牙利算法）
- ✅ **Phase 2**: CLI增强（美化输出、批量实验）
- ✅ **Phase 3**: 交互式GUI（Tkinter界面、可视化）

## 许可证

本项目用于学术研究和教学目的。
