"""测试直接使用字体文件"""
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.font_manager import FontProperties

# 找到Droid Sans Fallback字体文件
font_path = '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf'
print(f"字体文件路径: {font_path}")

# 创建FontProperties对象
font_prop = FontProperties(fname=font_path)

# 创建测试图表
fig, ax = plt.subplots(figsize=(8, 6))

# 使用字体属性
ax.text(0.5, 0.7, '中文测试：匹配数', fontsize=20, ha='center', fontproperties=font_prop)
ax.text(0.5, 0.5, 'English Test: Matching', fontsize=20, ha='center', fontproperties=font_prop)
ax.text(0.5, 0.3, '数字测试：12345', fontsize=20, ha='center', fontproperties=font_prop)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_title('字体显示测试（直接使用字体文件）', fontsize=16, fontweight='bold', fontproperties=font_prop)

plt.savefig('results/font_test2.png', dpi=150, bbox_inches='tight')
print("测试图表已保存到: results/font_test2.png")
print("请检查图表中的中文和英文是否都能正常显示")
