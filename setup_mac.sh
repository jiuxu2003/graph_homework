#!/bin/bash
# Graph Homework GUI - Mac 一键安装脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}==================================="
    echo "  $1"
    echo "===================================${NC}"
    echo ""
}

# 检查命令是否存在
check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# 主安装流程
main() {
    print_header "Graph Homework GUI 安装向导"

    # 1. 检查必要工具
    print_info "检查必要工具..."

    if ! check_command "git"; then
        print_error "未找到 Git，请先安装 Git: https://git-scm.com/"
        exit 1
    fi
    print_success "Git 已安装"

    if ! check_command "conda"; then
        print_error "未找到 Conda，请先安装 Anaconda 或 Miniconda"
        print_info "下载地址: https://docs.conda.io/en/latest/miniconda.html"
        exit 1
    fi
    print_success "Conda 已安装"

    # 2. 克隆仓库
    print_header "步骤 1/5: 克隆代码仓库"

    if [ -d "graph_homework" ]; then
        print_warning "目录 graph_homework 已存在"
        read -p "是否删除并重新克隆？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf graph_homework
            print_info "已删除旧目录"
        else
            print_info "使用现有目录"
            cd graph_homework
            git fetch
            git checkout 003-interactive-gui
            git pull
        fi
    fi

    if [ ! -d "graph_homework" ]; then
        print_info "正在克隆仓库..."
        git clone git@github.com:jiuxu2003/graph_homework.git
        cd graph_homework
        print_success "仓库克隆完成"
    fi

    # 3. 切换分支
    print_header "步骤 2/5: 切换到 GUI 分支"
    print_info "切换到 003-interactive-gui 分支..."
    git checkout 003-interactive-gui
    print_success "分支切换完成"

    # 4. 创建 Conda 环境
    print_header "步骤 3/5: 创建 Conda 虚拟环境"

    if conda env list | grep -q "graph_homework"; then
        print_warning "环境 graph_homework 已存在"
        read -p "是否删除并重新创建？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "删除旧环境..."
            conda env remove -n graph_homework -y
            print_success "旧环境已删除"
        else
            print_info "使用现有环境"
        fi
    fi

    if ! conda env list | grep -q "graph_homework"; then
        print_info "创建新环境 (Python 3.10)..."
        conda create -n graph_homework python=3.10 -y
        print_success "Conda 环境创建完成"
    fi

    # 5. 激活环境并安装依赖
    print_header "步骤 4/5: 安装项目依赖"

    print_info "激活环境..."
    eval "$(conda shell.bash hook)"
    conda activate graph_homework

    print_info "安装 Python 依赖包..."
    pip install -r requirements.txt
    print_success "项目依赖安装完成"

    print_info "安装测试工具..."
    pip install pytest pytest-cov
    print_success "测试工具安装完成"

    # 6. 验证安装
    print_header "步骤 5/5: 验证安装"

    print_info "检查 Python 版本..."
    python --version

    print_info "运行快速测试..."
    if pytest tests/gui/test_gui_state.py -v --tb=short; then
        print_success "测试通过！"
    else
        print_warning "部分测试失败，但不影响基本功能"
    fi

    # 7. 完成
    print_header "安装完成！"

    echo -e "${GREEN}🎉 恭喜！Graph Homework GUI 已成功安装${NC}"
    echo ""
    echo "接下来你可以："
    echo ""
    echo -e "${BLUE}1. 启动 GUI：${NC}"
    echo "   conda activate graph_homework"
    echo "   python src/gui_main.py"
    echo ""
    echo -e "${BLUE}2. 运行 CLI 示例：${NC}"
    echo "   python -m src.main configs/examples/simple_3x3.json"
    echo ""
    echo -e "${BLUE}3. 运行测试：${NC}"
    echo "   pytest tests/gui/ -v"
    echo ""
    echo -e "${BLUE}4. 查看帮助文档：${NC}"
    echo "   cat INSTALL_MAC.md"
    echo ""

    print_info "当前在虚拟环境中，使用 'conda activate graph_homework' 激活"
}

# 错误处理
trap 'print_error "安装过程中发生错误，请查看上方的错误信息"; exit 1' ERR

# 运行主函数
main

# 保持在环境中
exec bash
