"""
字体配置模块

统一配置matplotlib的中文字体支持
"""

import os
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 思源黑体字体文件路径
FONT_PATH = os.path.join(PROJECT_ROOT, 'fonts', 'SourceHanSansSC-Regular.otf')


def configure_chinese_font():
    """
    配置matplotlib支持中文显示

    使用思源黑体（Source Han Sans SC）作为中文字体
    """
    if os.path.exists(FONT_PATH):
        # 使用思源黑体
        plt.rcParams['font.sans-serif'] = ['Source Han Sans SC', 'DejaVu Sans', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False

        # 注册字体
        from matplotlib.font_manager import fontManager
        fontManager.addfont(FONT_PATH)

        return True
    else:
        # 回退到系统字体
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False
        return False


def get_chinese_font():
    """
    获取中文字体属性对象

    返回:
        FontProperties对象，如果字体文件存在；否则返回None
    """
    if os.path.exists(FONT_PATH):
        return FontProperties(fname=FONT_PATH)
    return None
