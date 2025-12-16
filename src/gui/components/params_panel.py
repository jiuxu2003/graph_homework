"""
参数编辑面板

提供配置参数的查看和编辑功能。
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any

from ..models.gui_state import GUIState


class ParamsPanel:
    """
    参数编辑面板

    显示和编辑实验配置参数。
    """

    def __init__(self, parent: ttk.Notebook, state: GUIState):
        """
        初始化参数面板

        Args:
            parent: 父容器（Notebook）
            state: 全局GUI状态
        """
        self.state = state

        # 创建主框架
        self.frame = ttk.Frame(parent, padding="10")

        # 存储参数输入框
        self.param_widgets: Dict[str, tk.Widget] = {}

        self._create_widgets()

    def _create_widgets(self):
        """创建界面组件"""
        # 标题
        title_label = ttk.Label(
            self.frame,
            text="实验参数配置",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 10))

        # 提示信息
        info_label = ttk.Label(
            self.frame,
            text="请检查并修改以下参数（可选）",
            foreground="gray"
        )
        info_label.pack(pady=(0, 10))

        # 创建滚动区域
        canvas = tk.Canvas(self.frame)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 占位符（在加载配置后动态创建）
        self.placeholder_label = ttk.Label(
            self.scrollable_frame,
            text="请先在「配置」标签页加载配置文件",
            foreground="gray",
            font=("Arial", 12)
        )
        self.placeholder_label.pack(pady=50)

        # 底部操作按钮
        action_frame = ttk.Frame(self.frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))

        self.reset_button = ttk.Button(
            action_frame,
            text="重置参数",
            command=self._reset_params,
            state=tk.DISABLED
        )
        self.reset_button.pack(side=tk.LEFT)

        self.run_button = ttk.Button(
            action_frame,
            text="运行实验 ▶",
            command=self._on_run,
            state=tk.DISABLED
        )
        self.run_button.pack(side=tk.RIGHT)

    def update_from_config(self, config: dict):
        """
        根据配置更新参数显示

        Args:
            config: 配置字典
        """
        # 清除占位符
        if self.placeholder_label.winfo_exists():
            self.placeholder_label.destroy()

        # 清除旧的参数输入框
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.param_widgets.clear()

        # 创建参数输入区域
        row = 0

        # 网络拓扑参数
        if "network" in config:
            self._create_section_header(self.scrollable_frame, "网络拓扑", row)
            row += 1

            network = config["network"]

            # 兼容两种命名
            num_users = network.get("num_secondary_users") or network.get("num_users", 0)

            row = self._create_param_field(
                self.scrollable_frame,
                "用户数量",
                "num_users",
                num_users,
                "int",
                row
            )

            row = self._create_param_field(
                self.scrollable_frame,
                "信道数量",
                "num_channels",
                network.get("num_channels", 0),
                "int",
                row
            )

            row += 1

        # 约束条件参数
        if "constraints" in config:
            self._create_section_header(self.scrollable_frame, "约束条件", row)
            row += 1

            constraints = config["constraints"]

            if "enable_availability" in constraints:
                row = self._create_param_field(
                    self.scrollable_frame,
                    "可用性约束",
                    "enable_availability",
                    constraints["enable_availability"],
                    "bool",
                    row
                )

            if "enable_single_transceiver" in constraints:
                row = self._create_param_field(
                    self.scrollable_frame,
                    "单收发器约束",
                    "enable_single_transceiver",
                    constraints["enable_single_transceiver"],
                    "bool",
                    row
                )

            if "enable_interference_avoidance" in constraints:
                row = self._create_param_field(
                    self.scrollable_frame,
                    "干扰避免约束",
                    "enable_interference_avoidance",
                    constraints["enable_interference_avoidance"],
                    "bool",
                    row
                )

            if "max_channels_per_user" in constraints:
                row = self._create_param_field(
                    self.scrollable_frame,
                    "每用户最大信道数",
                    "max_channels_per_user",
                    constraints["max_channels_per_user"],
                    "int",
                    row
                )

            if "min_spectrum_utilization" in constraints:
                row = self._create_param_field(
                    self.scrollable_frame,
                    "最小频谱利用率",
                    "min_spectrum_utilization",
                    constraints["min_spectrum_utilization"],
                    "float",
                    row
                )

            row += 1

        # 算法参数
        if "algorithm" in config:
            self._create_section_header(self.scrollable_frame, "算法参数", row)
            row += 1

            algo = config["algorithm"]

            if "timeout" in algo:
                row = self._create_param_field(
                    self.scrollable_frame,
                    "超时时间（秒）",
                    "timeout",
                    algo["timeout"],
                    "int",
                    row
                )

        # 启用按钮
        self.reset_button.config(state=tk.NORMAL)
        self.run_button.config(state=tk.NORMAL)

    def _create_section_header(self, parent, title: str, row: int):
        """创建分节标题"""
        header = ttk.Label(
            parent,
            text=title,
            font=("Arial", 11, "bold")
        )
        header.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))

    def _create_param_field(
        self,
        parent,
        label: str,
        key: str,
        value: Any,
        param_type: str,
        row: int
    ) -> int:
        """
        创建参数输入字段

        Args:
            parent: 父容器
            label: 参数标签
            key: 参数键名
            value: 参数值
            param_type: 参数类型 (int/float/str/bool)
            row: 行号

        Returns:
            下一行号
        """
        # 标签
        label_widget = ttk.Label(parent, text=f"{label}:")
        label_widget.grid(row=row, column=0, sticky=tk.W, padx=(10, 5), pady=5)

        # 根据类型创建不同的输入控件
        if param_type == "bool":
            # 布尔类型使用复选框
            var = tk.BooleanVar(value=bool(value))
            checkbox = ttk.Checkbutton(parent, variable=var)
            checkbox.grid(row=row, column=1, sticky=tk.W, pady=5)

            self.param_widgets[key] = {
                "var": var,
                "type": param_type,
                "original": value
            }
        else:
            # 其他类型使用输入框
            entry_var = tk.StringVar(value=str(value))
            entry = ttk.Entry(parent, textvariable=entry_var, width=20)
            entry.grid(row=row, column=1, sticky=tk.W, pady=5)

            self.param_widgets[key] = {
                "var": entry_var,
                "type": param_type,
                "original": value
            }

        return row + 1

    def _reset_params(self):
        """重置参数到原始值"""
        for key, widget_info in self.param_widgets.items():
            widget_info["var"].set(str(widget_info["original"]))

        messagebox.showinfo("提示", "参数已重置到原始值")

    def _on_run(self):
        """运行按钮点击"""
        # 由主窗口处理
        pass

    def get_current_config(self) -> dict:
        """
        获取当前配置（包括用户修改）

        Returns:
            dict: 更新后的配置字典
        """
        if not self.state.current_config:
            raise ValueError("未加载配置")

        # 复制原始配置
        config = self.state.current_config.copy()

        # 更新参数
        for key, widget_info in self.param_widgets.items():
            try:
                param_type = widget_info["type"]

                # 类型转换
                if param_type == "bool":
                    value = widget_info["var"].get()
                elif param_type == "int":
                    value_str = widget_info["var"].get()
                    value = int(value_str)
                elif param_type == "float":
                    value_str = widget_info["var"].get()
                    value = float(value_str)
                else:
                    value = widget_info["var"].get()

                # 更新到配置中（需要找到正确的位置）
                self._update_config_value(config, key, value)

            except ValueError as e:
                raise ValueError(f"参数 {key} 的值无效: {widget_info['var'].get()}")

        return config

    def _update_config_value(self, config: dict, key: str, value: Any):
        """
        更新配置中的值

        Args:
            config: 配置字典
            key: 参数键
            value: 新值
        """
        # 在各个部分中查找并更新
        if "network" in config:
            network = config["network"]

            # 处理用户数量的两种命名
            if key == "num_users":
                if "num_secondary_users" in network:
                    network["num_secondary_users"] = value
                elif "num_users" in network:
                    network["num_users"] = value
                else:
                    network["num_secondary_users"] = value
            elif key in network:
                network[key] = value

        if "constraints" in config and key in config["constraints"]:
            config["constraints"][key] = value

        if "algorithm" in config and key in config["algorithm"]:
            config["algorithm"][key] = value
