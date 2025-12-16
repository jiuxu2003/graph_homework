"""
配置加载面板

提供配置文件的加载和基本信息显示。
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional, Callable

from ..models.gui_state import GUIState
from ..utils.validation import validate_experiment_config


class ConfigPanel:
    """
    配置文件加载面板

    允许用户选择和加载配置文件，显示配置基本信息。
    """

    def __init__(
        self,
        parent: ttk.Notebook,
        state: GUIState,
        on_load_callback: Optional[Callable[[str, dict], None]] = None
    ):
        """
        初始化配置面板

        Args:
            parent: 父容器（Notebook）
            state: 全局GUI状态
            on_load_callback: 配置加载完成回调
        """
        self.state = state
        self.on_load_callback = on_load_callback

        # 创建主框架
        self.frame = ttk.Frame(parent, padding="10")

        self._create_widgets()

    def _create_widgets(self):
        """创建界面组件"""
        # 标题
        title_label = ttk.Label(
            self.frame,
            text="配置文件加载",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 10))

        # 文件选择区域
        file_frame = ttk.LabelFrame(self.frame, text="选择配置文件", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))

        # 文件路径显示
        path_frame = ttk.Frame(file_frame)
        path_frame.pack(fill=tk.X)

        ttk.Label(path_frame, text="文件路径:").pack(side=tk.LEFT)

        self.file_path_var = tk.StringVar(value="未选择")
        self.file_path_label = ttk.Label(
            path_frame,
            textvariable=self.file_path_var,
            foreground="gray"
        )
        self.file_path_label.pack(side=tk.LEFT, padx=10)

        # 按钮区域
        button_frame = ttk.Frame(file_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        self.load_button = ttk.Button(
            button_frame,
            text="浏览...",
            command=self.load_config_file
        )
        self.load_button.pack(side=tk.LEFT, padx=(0, 5))

        self.example_button = ttk.Button(
            button_frame,
            text="加载示例配置",
            command=self._load_example_config
        )
        self.example_button.pack(side=tk.LEFT)

        # 快速生成配置区域
        quick_frame = ttk.LabelFrame(self.frame, text="快速生成配置", padding="10")
        quick_frame.pack(fill=tk.X, pady=(0, 10))

        # 说明文本
        desc_label = ttk.Label(
            quick_frame,
            text="无需配置文件，直接输入参数快速生成默认配置",
            foreground="gray",
            font=("Arial", 9)
        )
        desc_label.pack(pady=(0, 10))

        # 参数输入区域
        params_frame = ttk.Frame(quick_frame)
        params_frame.pack(fill=tk.X)

        # 用户数量
        ttk.Label(params_frame, text="用户数量:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.quick_users_var = tk.StringVar(value="3")
        ttk.Entry(params_frame, textvariable=self.quick_users_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=5)

        # 信道数量
        ttk.Label(params_frame, text="信道数量:").grid(row=0, column=2, sticky=tk.W, padx=(20, 5), pady=5)
        self.quick_channels_var = tk.StringVar(value="3")
        ttk.Entry(params_frame, textvariable=self.quick_channels_var, width=10).grid(row=0, column=3, sticky=tk.W, pady=5)

        # 生成按钮
        self.generate_button = ttk.Button(
            params_frame,
            text="生成并加载配置",
            command=self._generate_quick_config
        )
        self.generate_button.grid(row=0, column=4, padx=(20, 0), pady=5)

        # 配置信息显示区域
        info_frame = ttk.LabelFrame(self.frame, text="配置信息", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True)

        # 创建文本框显示配置信息
        text_frame = ttk.Frame(info_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.info_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            height=15,
            state=tk.DISABLED,
            yscrollcommand=scrollbar.set
        )
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.info_text.yview)

        # 底部操作按钮
        action_frame = ttk.Frame(self.frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))

        self.continue_button = ttk.Button(
            action_frame,
            text="继续配置参数 →",
            command=self._on_continue,
            state=tk.DISABLED
        )
        self.continue_button.pack(side=tk.RIGHT)

    def load_config_file(self):
        """打开文件对话框选择配置文件"""
        # 确定初始目录
        initial_dir = Path.cwd() / "configs" / "examples"
        if not initial_dir.exists():
            initial_dir = Path.cwd()

        # 打开文件对话框
        file_path = filedialog.askopenfilename(
            title="选择配置文件",
            initialdir=str(initial_dir),
            filetypes=[
                ("JSON文件", "*.json"),
                ("所有文件", "*.*")
            ]
        )

        if file_path:
            self._load_config(file_path)

    def _load_example_config(self):
        """加载示例配置文件"""
        example_path = Path.cwd() / "configs" / "examples" / "simple_3x3.json"

        if not example_path.exists():
            messagebox.showerror("错误", f"示例配置文件不存在:\n{example_path}")
            return

        self._load_config(str(example_path))

    def _load_config(self, file_path: str):
        """
        加载配置文件

        Args:
            file_path: 配置文件路径
        """
        try:
            # 验证配置文件
            config, errors = validate_experiment_config(Path(file_path))

            if errors:
                error_msg = "配置文件验证失败:\n\n" + "\n".join(errors)
                messagebox.showerror("验证失败", error_msg)
                return

            # 更新界面
            self.file_path_var.set(file_path)
            self.file_path_label.config(foreground="black")

            # 显示配置信息
            self._display_config_info(config)

            # 启用继续按钮
            self.continue_button.config(state=tk.NORMAL)

            # 保存到状态
            self.state.current_config_file = file_path
            self.state.current_config = config

            # 调用回调
            if self.on_load_callback:
                self.on_load_callback(file_path, config)

            messagebox.showinfo("成功", f"配置文件加载成功!\n{Path(file_path).name}")

        except Exception as e:
            messagebox.showerror("错误", f"加载配置文件失败:\n{e}")

    def _display_config_info(self, config: dict):
        """
        显示配置信息

        Args:
            config: 配置字典
        """
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete("1.0", tk.END)

        # 格式化显示配置信息
        info_lines = []

        # 基本信息
        info_lines.append("=" * 50)
        info_lines.append("实验配置信息")
        info_lines.append("=" * 50)
        info_lines.append("")

        # 从metadata或顶层获取名称
        if "metadata" in config and "name" in config["metadata"]:
            info_lines.append(f"实验名称: {config['metadata']['name']}")
        elif "name" in config:
            info_lines.append(f"实验名称: {config['name']}")
        info_lines.append("")

        # 网络拓扑
        if "network" in config:
            network = config["network"]
            info_lines.append("【网络拓扑】")

            # 兼容两种命名
            num_users = network.get('num_secondary_users') or network.get('num_users', 'N/A')
            info_lines.append(f"  用户数量: {num_users}")
            info_lines.append(f"  信道数量: {network.get('num_channels', 'N/A')}")

            if "availability_matrix" in network:
                matrix = network["availability_matrix"]
                info_lines.append(f"  可用性矩阵: {len(matrix)}x{len(matrix[0]) if matrix else 0}")

            info_lines.append("")

        # 主用户信息
        if "primary_users" in config:
            primary = config["primary_users"]
            info_lines.append("【主用户】")

            occupied = primary.get("occupied_channels", [])
            if occupied:
                info_lines.append(f"  占用信道: {', '.join(map(str, occupied))}")
            else:
                info_lines.append("  占用信道: 无")

            info_lines.append("")

        # 干扰图信息
        if "interference" in config:
            interference = config["interference"]
            info_lines.append("【干扰图】")

            if "adjacency_matrix" in interference:
                matrix = interference["adjacency_matrix"]
                info_lines.append(f"  邻接矩阵: {len(matrix)}x{len(matrix[0]) if matrix else 0}")

            info_lines.append("")

        # 约束条件
        if "constraints" in config:
            constraints = config["constraints"]
            info_lines.append("【约束条件】")

            if "enable_availability" in constraints:
                info_lines.append(f"  可用性约束: {'启用' if constraints['enable_availability'] else '禁用'}")

            if "enable_single_transceiver" in constraints:
                info_lines.append(f"  单收发器约束: {'启用' if constraints['enable_single_transceiver'] else '禁用'}")

            if "enable_interference_avoidance" in constraints:
                info_lines.append(f"  干扰避免约束: {'启用' if constraints['enable_interference_avoidance'] else '禁用'}")

            if "max_channels_per_user" in constraints:
                info_lines.append(f"  每用户最大信道数: {constraints['max_channels_per_user']}")

            if "min_spectrum_utilization" in constraints:
                info_lines.append(f"  最小频谱利用率: {constraints['min_spectrum_utilization']}")

            if "priority_users" in constraints:
                priority = constraints["priority_users"]
                info_lines.append(f"  优先用户: {', '.join(map(str, priority)) if priority else '无'}")

            info_lines.append("")

        # 算法参数
        if "algorithm" in config:
            algo = config["algorithm"]
            info_lines.append("【算法参数】")
            info_lines.append(f"  算法类型: {algo.get('type', 'hungarian')}")

            if "timeout" in algo:
                info_lines.append(f"  超时时间: {algo['timeout']} 秒")

            info_lines.append("")

        # 输出设置
        if "output" in config:
            output = config["output"]
            info_lines.append("【输出设置】")
            info_lines.append(f"  保存结果: {'是' if output.get('save_results', False) else '否'}")
            info_lines.append(f"  生成可视化: {'是' if output.get('generate_visualization', False) else '否'}")

            if "output_dir" in output:
                info_lines.append(f"  输出目录: {output['output_dir']}")

        self.info_text.insert("1.0", "\n".join(info_lines))
        self.info_text.config(state=tk.DISABLED)

    def _on_continue(self):
        """继续按钮点击"""
        # 这个功能由主窗口处理（切换标签页）
        pass

    def _generate_quick_config(self):
        """快速生成配置"""
        try:
            # 读取并验证输入
            num_users = int(self.quick_users_var.get())
            num_channels = int(self.quick_channels_var.get())

            if num_users <= 0 or num_channels <= 0:
                messagebox.showerror("输入错误", "用户数量和信道数量必须大于0")
                return

            if num_users > 100 or num_channels > 100:
                if not messagebox.askyesno(
                    "确认",
                    f"您输入的规模较大（{num_users}×{num_channels}），可能需要较长时间运行。\n是否继续？"
                ):
                    return

            # 生成配置
            config = self._create_default_config(num_users, num_channels)

            # 更新界面
            self.file_path_var.set(f"[快速生成] {num_users}用户 × {num_channels}信道")
            self.file_path_label.config(foreground="blue")

            # 显示配置信息
            self._display_config_info(config)

            # 启用继续按钮
            self.continue_button.config(state=tk.NORMAL)

            # 保存到状态
            self.state.current_config_file = None  # 快速生成的配置没有文件路径
            self.state.current_config = config

            # 调用回调
            if self.on_load_callback:
                self.on_load_callback(None, config)

            messagebox.showinfo("成功", f"配置已生成！\n{num_users} 用户 × {num_channels} 信道")

        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的数字")
        except Exception as e:
            messagebox.showerror("错误", f"生成配置失败:\n{e}")

    def _create_default_config(self, num_users: int, num_channels: int) -> dict:
        """
        创建默认配置

        Args:
            num_users: 用户数量
            num_channels: 信道数量

        Returns:
            dict: 配置字典
        """
        # 生成全1的可用性矩阵（所有信道对所有用户可用）
        availability_matrix = [[1 for _ in range(num_channels)] for _ in range(num_users)]

        # 生成全0的邻接矩阵（用户间无干扰）
        adjacency_matrix = [[0 for _ in range(num_users)] for _ in range(num_users)]

        # 创建配置字典
        config = {
            "metadata": {
                "name": f"快速生成配置 ({num_users}x{num_channels})",
                "description": "通过GUI快速生成的默认配置"
            },
            "network": {
                "num_secondary_users": num_users,
                "num_channels": num_channels,
                "availability_matrix": availability_matrix
            },
            "primary_users": {
                "occupied_channels": []
            },
            "interference": {
                "adjacency_matrix": adjacency_matrix
            },
            "constraints": {
                "enable_availability": True,
                "enable_single_transceiver": True,
                "enable_interference_avoidance": True,
                "max_channels_per_user": 1,
                "min_spectrum_utilization": 0.0,
                "priority_users": []
            },
            "algorithm": {
                "type": "hungarian",
                "timeout": 60
            },
            "output": {
                "save_results": True,
                "generate_visualization": True,
                "output_dir": "results"
            }
        }

        return config

