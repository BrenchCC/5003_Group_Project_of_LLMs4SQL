# 🧪 Assay Summary by Brench：语言模型 SQL 理解能力评估

> **Repo:** [https://github.com/AnanyaRahaman/LLMs_SQL_Understanding](https://github.com/AnanyaRahaman/LLMs_SQL_Understanding)
> **相关文档：**[原论文](2410.10680v1.pdf)｜[中文翻译](2410.10680_zh_CN.pdf)

本项目复现并扩展了 *“Evaluating SQL Understanding in Large Language Models”* 一文中提出的 SQL 理解能力测试（SQL Understanding Assay），同时针对提示词设计、模型接口、评估维度、推理流程等方面做了更工程化且可复现的实现。

---

## 一、研究背景

大语言模型（LLMs）在 NLP、代码生成、甚至多模态任务中展现出惊人能力，但它们是否真正“理解”结构化查询语言（SQL）仍缺乏系统论证。结构化语言不同于自然语言，更强调**语法约束、语义一致性、执行逻辑和上下文关系**——这些能力决定模型在数据管理系统中的可用性与可信度。

本研究参照原论文，将“理解能力”拆解为四类核心技能：

* **识别（Recognition）：** 理解基本 SQL 结构和 token。
* **语义（Semantics）：** 理解查询背后的实际意义。
* **上下文（Context）：** 把握列/表之间关系、依赖和约束。
* **连贯性（Coherence）：** 推断查询是否完整、逻辑是否自洽。

这些能力支撑模型在数据分析、数据库自动化、SQL 修复等任务中的落地表现。

---

## 二、任务定义与评估目标

本研究采用五项互补任务，覆盖从语法层面到语义层面的 SQL 理解能力：

| 任务              | 目标                 | 技能维度    | 数据来源                     | 关键指标                             |
| --------------- | ------------------ | ------- | ------------------------ | -------------------------------- |
| **语法错误检测**      | 判断 SQL 是否存在语法或语义违规 | 识别、连贯性  | SDSS、SQLShare、Join-Order | Precision / Recall / F1（二分类+多分类） |
| **缺失 token 识别** | 识别 SQL 缺失元素及其位置    | 识别、上下文  | SDSS、SQLShare、Join-Order | F1、MAE、Hit Rate、多分类、位置预测         |
| **查询性能预测**      | 基于 SQL 文本预测运行成本    | 上下文、连贯性 | SDSS（含 runtime）          | 二分类指标                            |
| **查询等价性分析**     | 判断不同写法的 SQL 是否语义等价 | 语义、连贯性  | SDSS、SQLShare、Join-Order | 二分类+多分类（需 label mapping）         |
| **查询解释**        | SQL → NL 转换        | 语义、上下文  | Spider                   | 不做量化评估（语言生成任务）                   |

> 注：原论文对查询解释任务只做定性分析，本项目不作为主评估维度。

---

## 三、Assay 反思与实验复现问题

在复现原论文过程中，发现一些影响可信度的关键问题，需要重新设计 pipeline：

### 1. Prompt 设计偏弱

论文原始 prompt 过于简单，无法约束输出格式。模型输出结构不稳定，难以自动解析，推高标注成本。

### 2. 缺少模型输出样例

论文和仓库均未提供真实输出，无法验证 prompt 与结果的对应关系，也不利于复现。

### 3. 评估数据混乱

* 查询等价类别存在重复，未与论文“10+8 类”保持一致
* 多分类任务未明确使用 Micro 还是 Macro F1
* 推理/评估 pipeline 未提供

### 4. 模型随机性未被控制

未限定 sampling 参数（如 temperature, top_p），难以保证可复现性。

### 5. 未固定模型版本

论文未提供具体的模型版本号，导致复现实验之间不可比。

---

## 四、优化策略（Optimization Strategy）

下面总结针对原始设计的增强策略，确保可复现性、稳定输出和更全面的评估。

### 4.1 改进评估维度（Redefine Evaluation Dimension）

每项任务统一支持以下模式：

* **Binary（原论文标准）**
* **Multi-class（扩展能力）**
* **位置预测（Missing Token 专用）**

示例如下：

* *Syntax Error →* 是否语法错误 + 错误类型分类
* *Missing Token →* 缺失类别 + 缺失位置
* *Query Performance →* 高/低成本判断
* *Query Equivalence →* 二分类 + 语义类别映射（label mapping）

这些扩展指标对于模型能力诊断更细致、更科学。

### 4.2 Prompt Engineering

从“随便问一句”升级为“结构化、可解析、语义引导”的专业提示策略：

* zero-shot 基线
* few-shot JSON schema 强约束
* structured role/workflow prompt
* 针对 non-thinking 模型，加入 *next-token reasoning skeleton* 引导（作为未来优化点）

### 4.3 多模型推理接口（LLM Server）

统一封装 Doubao / Qwen / DeepSeek / GLM
支持是否启用 reasoning（思维链）
隐藏平台差异
供 inference pipeline 调用

### 4.4 推理 Pipeline（Inference Pipeline）

统一规定：

* 固定 sampling 参数
* 模型输出结构化解析
* 自动构造评估输入
* 可批量处理多模型、多 dataset

### 4.5 评估 Pipeline（Evaluation Pipeline）

包含：

* 多任务评估
* 多分类/二分类区分
* 可自定义聚合方式（micro/macro/weighted）
* 性能/错误分析

### 4.6 简单结果分析

结合论文方式，可扩展分析维度：
* word_count / predicate_count / table_count / column_count
* 模型大小、训练数据来源
* 推理模式（thinking vs non-thinking）

五、未来的展望
- 性能优化：Finetune + prompt engineering
- 速度优化：采取非思考模型，加入 next-token reasoning skeleton 引导，提高推理速度。
- 外部知识库引入：
    - 数据库 schema 信息
    - 表/列 注释
    - 常用查询模板
    帮助模型理解数据库结构，提高查询准确性。
- 应用层展望：sql agent 辅助 数据库管理系统 ～ context engineering
    - 自动纠错
    - 自动优化查询
    - 自动生成高质量查询
    - 自动解释查询
    - 调用tools 自动执行数据库操作
