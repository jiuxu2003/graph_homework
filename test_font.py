"""测试中文字体显示"""
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 清除字体缓存
fm._load_fontmanager(try_read_cache=False)

# 配置字体
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Droid Sans Fallback', 'SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 打印当前使用的字体
print("当前字体配置:", plt.rcParams['font.sans-serif'])

# 创建测试图表
fig, ax = plt.subplots(figsize=(8, 6))
ax.text(0.5, 0.7, '中文测试：匹配数', fontsize=20, ha='center')
ax.text(0.5, 0.5, 'English Test: Matching', fontsize=20, ha='center')
ax.text(0.5, 0.3, '数字测试：12345', fontsize=20, ha='center')
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_title('字体显示测试', fontsize=16, fontweight='bold')

plt.savefig('results/font_test.png', dpi=150, bbox_inches='tight')
print("测试图表已保存到: results/font_test.png")

# 检查实际使用的字体
from matplotlib import font_manager
prop = font_manager.FontProperties(family='sans-serif')
font_file = font_manager.findfont(prop)
print(f"实际使用的字体文件: {font_file}")
