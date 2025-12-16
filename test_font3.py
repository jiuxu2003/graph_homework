"""测试思源黑体字体"""
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties, fontManager

# 字体文件路径
font_path = 'fonts/SourceHanSansSC-Regular.otf'

# 注册字体
fontManager.addfont(font_path)

# 配置matplotlib使用思源黑体
plt.rcParams['font.sans-serif'] = ['Source Han Sans SC', 'DejaVu Sans', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

print(f"字体文件: {font_path}")
print(f"字体配置: {plt.rcParams['font.sans-serif']}")

# 创建测试图表
fig, ax = plt.subplots(figsize=(10, 6))

ax.text(0.5, 0.8, '中文测试：匹配数、频谱利用率', fontsize=18, ha='center')
ax.text(0.5, 0.6, 'English Test: Matching, Spectrum Utilization', fontsize=18, ha='center')
ax.text(0.5, 0.4, '数字测试：0123456789', fontsize=18, ha='center')
ax.text(0.5, 0.2, '混合测试：用户0->信道1 (100%)', fontsize=18, ha='center')

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_title('思源黑体字体显示测试', fontsize=20, fontweight='bold')
ax.set_xlabel('横轴标签 (X-axis)', fontsize=14)
ax.set_ylabel('纵轴标签 (Y-axis)', fontsize=14)

plt.tight_layout()
plt.savefig('results/font_test3.png', dpi=150, bbox_inches='tight')
print("测试图表已保存到: results/font_test3.png")
print("如果没有警告信息，说明字体配置成功！")
