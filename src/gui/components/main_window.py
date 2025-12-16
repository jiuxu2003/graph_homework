"""
主应用窗口

提供GUI应用的主窗口和布局管理。
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Optional

from ..models.gui_state import GUIState, UserPreferences
from ..controllers.experiment_controller import ExperimentController
from ..controllers.history_controller import HistoryController
from ..utils.config_manager import UserConfigManager

from .config_panel import ConfigPanel
from .params_panel import ParamsPanel
from .results_panel import ResultsPanel
from .visualization_panel import VisualizationPanel


class MainWindow:
    """
    主应用窗口

    管理GUI应用的主窗口、菜单栏、标签页和整体布局。
    """

    def __init__(self, root: tk.Tk):
        """
        初始化主窗口

        Args:
            root: Tkinter根窗口
        """
        self.root = root
        self.root.title("认知无线电频谱分配系统")

        # 初始化状态和控制器
        self.state = GUIState()
        self.preferences = self._load_preferences()

        # 设置窗口大小和位置
        self._setup_window_geometry()

        # 初始化控制器
        self.experiment_controller = ExperimentController(
            result_callback=self._on_experiment_complete,
            error_callback=self._on_experiment_error
        )

        self.history_controller = HistoryController()

        # 创建UI组件
        self._create_menu_bar()
        self._create_main_layout()

        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _load_preferences(self) -> UserPreferences:
        """加载用户偏好设置"""
        try:
            UserConfigManager.ensure_config_dir()
            prefs_file = UserConfigManager.PREFERENCES_FILE

            if prefs_file.exists():
                import json
                with open(prefs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return UserPreferences.from_dict(data)
        except Exception:
            pass

        return UserPreferences()

    def _save_preferences(self):
        """保存用户偏好设置"""
        try:
            # 更新窗口位置和大小
            self.preferences.window_width = self.root.winfo_width()
            self.preferences.window_height = self.root.winfo_height()
            self.preferences.window_x = self.root.winfo_x()
            self.preferences.window_y = self.root.winfo_y()

            # 保存到文件
            prefs_file = UserConfigManager.PREFERENCES_FILE
            import json
            with open(prefs_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences.to_dict(), f, indent=2)
        except Exception as e:
            print(f"保存偏好设置失败: {e}")

    def _setup_window_geometry(self):
        """设置窗口几何属性"""
        width = self.preferences.window_width
        height = self.preferences.window_height

        if self.preferences.window_x is not None and self.preferences.window_y is not None:
            # 使用保存的位置
            x = self.preferences.window_x
            y = self.preferences.window_y
            self.root.geometry(f"{width}x{height}+{x}+{y}")
        else:
            # 居中显示
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            self.root.geometry(f"{width}x{height}+{x}+{y}")

        # 设置最小尺寸
        self.root.minsize(800, 600)

    def _create_menu_bar(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="加载配置...", command=self._on_load_config)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self._on_closing)

        # 实验菜单
        experiment_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="实验", menu=experiment_menu)
        experiment_menu.add_command(label="运行实验", command=self._on_run_experiment)
        experiment_menu.add_command(label="取消实验", command=self._on_cancel_experiment)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self._show_about)

    def _create_main_layout(self):
        """创建主布局"""
        # 创建标签页控件
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 创建各个面板
        self.config_panel = ConfigPanel(
            self.notebook,
            state=self.state,
            on_load_callback=self._on_config_loaded
        )

        self.params_panel = ParamsPanel(
            self.notebook,
            state=self.state
        )

        self.results_panel = ResultsPanel(
            self.notebook,
            state=self.state
        )

        self.viz_panel = VisualizationPanel(
            self.notebook,
            state=self.state,
            preferences=self.preferences
        )

        # 添加标签页
        self.notebook.add(self.config_panel.frame, text="配置")
        self.notebook.add(self.params_panel.frame, text="参数")
        self.notebook.add(self.results_panel.frame, text="结果")
        self.notebook.add(self.viz_panel.frame, text="可视化")

        # 创建底部状态栏
        self._create_status_bar()

        # 绑定标签页切换事件
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _create_status_bar(self):
        """创建状态栏"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = ttk.Label(
            self.status_frame,
            text="就绪",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=2)

    def _on_tab_changed(self, event):
        """标签页切换事件处理"""
        current_tab = self.notebook.index(self.notebook.select())
        tab_names = ["config", "params", "results", "viz"]

        if current_tab < len(tab_names):
            self.state.active_tab = tab_names[current_tab]

    def _on_load_config(self):
        """加载配置文件"""
        self.config_panel.load_config_file()

    def _on_config_loaded(self, config_file: str, config: dict):
        """配置加载完成回调"""
        self.state.current_config_file = config_file
        self.state.current_config = config

        # 更新参数面板
        self.params_panel.update_from_config(config)

        # 切换到参数标签页
        self.notebook.select(1)

        self._set_status(f"已加载配置: {Path(config_file).name}")

    def _on_run_experiment(self):
        """运行实验"""
        if self.state.current_config is None:
            messagebox.showwarning("警告", "请先加载配置文件")
            return

        if self.state.is_experiment_running:
            messagebox.showwarning("警告", "已有实验正在运行")
            return

        try:
            # 从参数面板获取当前配置
            config = self.params_panel.get_current_config()

            # 更新状态
            self.state.is_experiment_running = True
            self.state.current_result = None
            self._set_status("实验运行中...")

            # 异步运行实验
            self.current_task_id = self.experiment_controller.run_experiment_async(config)

            # 开始轮询实验状态
            self._poll_experiment_status()

        except Exception as e:
            self.state.is_experiment_running = False
            messagebox.showerror("错误", f"启动实验失败: {e}")
            self._set_status("就绪")

    def _on_cancel_experiment(self):
        """取消实验"""
        if not self.state.is_experiment_running:
            messagebox.showinfo("提示", "当前没有运行中的实验")
            return

        if hasattr(self, 'current_task_id'):
            if self.experiment_controller.cancel_experiment(self.current_task_id):
                messagebox.showinfo("提示", "实验已取消")
                self.state.is_experiment_running = False
                self._set_status("实验已取消")

    def _poll_experiment_status(self):
        """轮询实验状态"""
        if not hasattr(self, 'current_task_id'):
            return

        try:
            status = self.experiment_controller.get_experiment_status(self.current_task_id)

            if status["status"] == "running":
                # 继续轮询
                self.root.after(100, self._poll_experiment_status)
            elif status["status"] == "completed":
                # 获取结果并触发回调
                if "result" in status:
                    self._on_experiment_complete(status["result"])
            elif status["status"] == "failed":
                # 触发错误回调
                if "error" in status:
                    self._on_experiment_error(status["error"])

        except KeyError:
            # 任务不存在，可能已完成
            pass
        except Exception as e:
            self._on_experiment_error(e)

    def _on_experiment_complete(self, result: dict):
        """实验完成回调"""
        self.state.is_experiment_running = False
        self.state.current_result = result

        # 更新结果面板
        self.results_panel.update_results(result)

        # 更新可视化面板
        self.viz_panel.update_visualization(result)

        # 切换到结果标签页
        self.notebook.select(2)

        # 保存到历史记录
        if self.preferences.auto_save_history:
            self._save_to_history(result)

        self._set_status("实验完成")
        messagebox.showinfo("成功", "实验运行完成！")

    def _on_experiment_error(self, error: Exception):
        """实验错误回调"""
        self.state.is_experiment_running = False

        self._set_status("实验失败")
        messagebox.showerror("错误", f"实验运行失败:\n{error}")

    def _save_to_history(self, result: dict):
        """保存实验到历史记录"""
        try:
            from datetime import datetime

            self.history_controller.save_experiment(
                config_file=self.state.current_config_file or "unknown",
                config=self.state.current_config,
                result=result,
                success=True,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            print(f"保存历史记录失败: {e}")

    def _set_status(self, message: str):
        """设置状态栏消息"""
        self.status_label.config(text=message)

    def _show_about(self):
        """显示关于对话框"""
        messagebox.showinfo(
            "关于",
            "认知无线电频谱分配系统 v1.0\n\n"
            "基于匈牙利算法的二分图最大匹配\n"
            "支持约束条件的频谱资源优化分配\n\n"
            "© 2025"
        )

    def _on_closing(self):
        """窗口关闭事件"""
        # 保存偏好设置
        self._save_preferences()

        # 关闭历史控制器
        self.history_controller.close()

        # 销毁窗口
        self.root.destroy()

    def run(self):
        """启动主事件循环"""
        self.root.mainloop()
