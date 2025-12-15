# Mac 端安装和运行指南

## 前置要求
- macOS 系统
- 已安装 Conda（Anaconda 或 Miniconda）
- Git 已配置

## 快速安装脚本

将以下脚本保存为 `setup_mac.sh` 并执行：

```bash
#!/bin/bash
set -e

echo "==================================="
echo "  Graph Homework GUI 安装脚本"
echo "==================================="

# 1. 克隆仓库
echo "📦 克隆代码仓库..."
git clone git@github.com:jiuxu2003/graph_homework.git
cd graph_homework

# 2. 切换到GUI分支
echo "🔀 切换到 003-interactive-gui 分支..."
git checkout 003-interactive-gui

# 3. 创建 Conda 环境
echo "🐍 创建 Conda 环境 graph_homework..."
conda create -n graph_homework python=3.10 -y

# 4. 激活环境
echo "✅ 激活环境..."
eval "$(conda shell.bash hook)"
conda activate graph_homework

# 5. 安装依赖
echo "📚 安装Python依赖..."
pip install -r requirements.txt

# 6. 安装测试依赖
echo "🧪 安装测试依赖..."
pip install pytest pytest-cov

echo ""
echo "==================================="
echo "  ✅ 安装完成！"
echo "==================================="
echo ""
echo "运行GUI："
echo "  conda activate graph_homework"
echo "  python src/gui_main.py"
echo ""
echo "运行CLI："
echo "  python -m src.main configs/examples/simple_3x3.json"
echo ""
echo "运行测试："
echo "  pytest tests/gui/"
echo ""
```

## 手动安装步骤

### 1. 克隆仓库
```bash
git clone git@github.com:jiuxu2003/graph_homework.git
cd graph_homework
```

### 2. 切换到GUI分支
```bash
git checkout 003-interactive-gui
```

### 3. 创建 Conda 虚拟环境
```bash
conda create -n graph_homework python=3.10 -y
```

### 4. 激活环境
```bash
conda activate graph_homework
```

### 5. 安装依赖
```bash
# 安装项目依赖
pip install -r requirements.txt

# 安装测试依赖
pip install pytest pytest-cov
```

## 运行应用

### 启动 GUI（图形界面）
```bash
conda activate graph_homework
python src/gui_main.py
```

### 运行 CLI（命令行）
```bash
# 运行单个实验
python -m src.main configs/examples/simple_3x3.json

# 运行批量实验
python demo_batch_experiment.py

# 运行规模对比实验
./run_scale_comparison.sh
```

### 运行测试
```bash
# 运行所有GUI测试
pytest tests/gui/ -v

# 运行特定测试文件
pytest tests/gui/test_gui_state.py -v

# 查看测试覆盖率
pytest tests/gui/ --cov=src/gui --cov-report=html
```

## 项目依赖（requirements.txt）
```
numpy>=1.24.0
scipy>=1.10.0
matplotlib>=3.7.0
```

## 目录结构
```
graph_homework/
├── src/
│   ├── gui/                    # GUI模块
│   │   ├── components/         # UI组件（待实现）
│   │   ├── controllers/        # 控制器层
│   │   ├── models/             # 数据模型
│   │   └── utils/              # 工具函数
│   ├── algorithm/              # 匹配算法
│   ├── cli/                    # 命令行界面
│   ├── io/                     # 输入输出
│   ├── models/                 # 核心数据模型
│   └── visualization/          # 可视化
├── configs/                    # 配置文件
│   ├── examples/               # 示例配置
│   └── experiments/            # 实验配置
├── tests/                      # 测试文件
│   ├── gui/                    # GUI测试
│   ├── unit/                   # 单元测试
│   └── integration/            # 集成测试
└── results/                    # 实验结果

```

## 验证安装

### 1. 检查环境
```bash
conda activate graph_homework
python --version  # 应该显示 Python 3.10.x
```

### 2. 运行测试验证
```bash
pytest tests/gui/test_gui_state.py -v
```

### 3. 快速测试CLI
```bash
python -m src.main configs/examples/simple_3x3.json
```

## 常见问题

### Q: 如果遇到 `ModuleNotFoundError`
```bash
# 确保在正确的环境中
conda activate graph_homework

# 重新安装依赖
pip install -r requirements.txt
```

### Q: 如果 Conda 命令不可用
```bash
# 添加 conda 到 PATH（如果使用 Miniconda）
export PATH="$HOME/miniconda3/bin:$PATH"

# 或者使用 Anaconda
export PATH="$HOME/anaconda3/bin:$PATH"

# 初始化 conda
conda init bash
```

### Q: GUI 无法启动
```bash
# 检查 Python 环境
python -c "import tkinter; print('Tkinter OK')"

# Mac 上 Tkinter 应该是内置的，如果报错可能需要重新安装 Python
```

## 下一步

GUI 当前处于 Phase 2 完成状态：
- ✅ 基础设施完成（工具、模型、控制器）
- ✅ 单元测试完成
- ⏳ GUI 界面组件（Phase 3）待实现

启动 GUI 后，你将看到一个初始化窗口。后续将实现完整的用户界面。

## 开发模式

如果你想参与开发：

```bash
# 安装开发依赖
pip install pytest pytest-cov black ruff

# 运行代码格式化
black src/ tests/

# 运行代码检查
ruff check src/ tests/

# 运行完整测试套件
pytest tests/ -v --cov=src
```

## 支持

如有问题，请查看项目文档或提交 Issue。
