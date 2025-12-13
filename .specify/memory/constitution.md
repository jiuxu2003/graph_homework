<!--
Sync Impact Report:
- Version: Initial → 1.0.0
- Type: Initial constitution creation
- Modified principles: N/A (new constitution)
- Added sections: All core sections
- Removed sections: N/A
- Templates requiring updates:
  ✅ spec-template.md - reviewed, compatible with principles
  ✅ plan-template.md - reviewed, constitution check section will use these principles
  ✅ tasks-template.md - reviewed, task organization aligns with principles
  ⚠ No command templates found - N/A
  ⚠ No README.md found - will be created during implementation
- Follow-up TODOs: None
-->

# 认知无线电频谱分配系统 Constitution

## Core Principles

### I. 简洁性原则 (Simplicity Principle)

代码必须保持简洁和可读性。避免过度工程化，专注于核心功能实现。这是一个演示算法应用的学术项目，而非生产系统。

**具体要求**:
- 代码结构清晰，易于理解
- 避免不必要的抽象和复杂设计模式
- 函数和模块职责单一
- 优先使用标准库，谨慎引入第三方依赖

**理由**: 学术项目的重点是展示对算法的理解和应用能力，而非软件工程的复杂性。简洁的代码更容易验证正确性，也更便于学习和评审。

### II. 算法正确性 (Algorithm Correctness)

匈牙利算法的实现必须正确无误，能够产生正确的最大匹配结果。所有核心算法逻辑必须可验证。

**具体要求**:
- 匈牙利算法实现遵循标准算法流程
- 关键步骤有清晰的中文注释说明
- 算法复杂度符合理论预期 (O(n³))
- 边界条件和特殊情况处理正确

**理由**: 算法正确性是本项目的核心学术要求。错误的算法实现将导致整个项目失去意义。

### III. 可验证性 (Verifiability)

必须包含验证性实验，通过测试用例证明算法的正确性和在频谱分配场景中的有效性。

**具体要求**:
- 包含多个测试用例（小规模、中等规模、实际场景）
- 测试结果可重现
- 提供预期输出与实际输出的对比
- 实验结果以可视化或表格形式呈现

**理由**: 学术工作需要可验证的实验结果。验证性实验不仅证明算法正确性，也展示其在实际问题中的应用价值。

### IV. 适度可扩展性 (Moderate Extensibility)

设计应允许合理的扩展，但不为假设的未来需求过度设计。在刚性和灵活性之间取得平衡。

**具体要求**:
- 核心算法与应用场景适度解耦
- 输入输出接口清晰定义
- 支持不同规模的问题实例
- 预留合理的参数配置空间

**理由**: 适度的可扩展性展示了对软件设计的理解，同时避免了不必要的复杂性。这符合学术项目"验证性实验+一定扩展性"的要求。

## 技术约束 (Technical Constraints)

**编程语言**: Python 3.x (推荐 3.8+)

**文档语言**: 优先使用中文
- 代码注释使用中文
- 文档和说明使用中文
- 变量和函数名可使用英文（遵循 Python 命名规范）

**项目范围**: 验证性实验，非生产系统
- 重点在算法正确性和应用演示
- 不需要考虑高并发、分布式等生产环境问题
- 性能优化以不影响代码可读性为前提

**应用领域**: 图论算法在通信领域的应用
- 二部图最大匹配问题
- 认知无线电网络频谱分配场景
- 展示图论理论与实际问题的结合

## 开发流程 (Development Workflow)

**实现顺序**:
1. 核心算法实现（匈牙利算法）
2. 频谱分配场景建模
3. 验证性实验设计与执行
4. 结果分析与文档编写

**代码质量要求**:
- 关键算法步骤必须有中文注释
- 函数和类需要文档字符串（docstring）
- 代码遵循 PEP 8 规范
- 提交前进行基本的代码审查

**实验要求**:
- 至少包含 3 个不同规模的测试用例
- 实验结果需要可视化或表格呈现
- 记录实验过程和观察结果

**文档要求**:
- README 说明项目背景、运行方法
- 代码中的算法说明
- 实验报告（可选，根据作业要求）

## Governance

**宪法地位**: 本宪法指导所有开发决策

**优先级原则**:
- 简洁性优先于功能丰富性
- 正确性优先于性能优化
- 可验证性优先于代码优雅性

**合规性检查**:
- 所有代码提交前检查是否符合简洁性原则
- 算法实现必须通过验证性测试
- 文档必须使用中文

**修订流程**:
- 宪法修订需要明确的理由
- 版本号遵循语义化版本规范
- 重大修改需要更新相关模板和文档

**学术诚信**:
- 所有代码必须是原创或明确标注引用来源
- 算法实现基于公开的学术资料
- 实验数据真实可靠

**Version**: 1.0.0 | **Ratified**: 2025-12-13 | **Last Amended**: 2025-12-13
