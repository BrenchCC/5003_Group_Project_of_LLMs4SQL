# Assay Summary by Brench：语言模型SQL理解能力评估
> https://github.com/AnanyaRahaman/LLMs_SQL_Understanding
> ralated_docs: [assay_origin](2410.10680v1.pdf) | [assay_cn](2410.10680_zh_CN.pdf)
## 一、背景
大语言模型（LLMs）在自然语言处理和图像生成等领域表现显著，但对其在SQL等结构化领域的真实"理解"程度仍存争议。本研究将"理解"定义为模型在**识别、语义、上下文、连贯性**四项核心技能上的表现，这对于LLMs在数据管理场景中的可靠应用至关重要。

## 二、任务分析
研究设计了5项递进式SQL任务，全面评估从基础语法到深层语义的理解能力：

| 任务类别 | 核心目标 | 关键技能 | 数据集来源 | 主要评估指标 |
|---------|---------|---------|-----------|------------|
| **语法错误检测** | 识别SQL语法和语义违规 | 识别、连贯性 | SDSS、SQLShare、Join-Order | Precision、Recall、F1-Score |
| **缺失token识别** | 检测SQL查询中缺失元素 | 识别、上下文 | SDSS、SQLShare、Join-Order | Precision、Recall、F1-Score、MAE、HR |
| **查询性能预测** | 通过SQL文本估算运行性能 | 上下文、连贯性 | SDSS（含运行时数据） | Precision、Recall、F1-Score |
| **查询等价性检查** | 判断语法不同但语义相同的查询 | 语义、连贯性 | SDSS、SQLShare、Join-Order | Precision、Recall、F1-Score |
| **查询解释** | 将SQL转化为自然语言描述 | 语义、上下文 | Spider | 定性分析（建议不作为核心评估） |

> 在原论文中，基于测试后的结果，分析模型表现差异的归因：从word_count, table_count, predicate_count, column_count, 模型训练数据等角度进行分析。

## 三、Optimization Strategy and Assay thinking
### 3.1 Optimization Strategy
- Doubao/Qwen/Deepseek/kimi: thinking/not thinking
- evaluation dimension：
    - 语法错误检测 二分类+多分类
    - 缺失token识别 二分类+多分类+location定位（词的位置）
    - 查询性能预测 二分类 (是否高成本； 原文只输入了query)
    - 查询等价性检查 二分类+多分类 （多分类的话需要做一个label mapping，将等价类别的查询映射到一个等价类别的label）
    - 查询解释 不做 无法评估
- Prompt Engineering
    - zero shot
    - few shot for formatted output json schema
    - formatted output with reasons based on next token prediction
    - role, workflow, json format

### 3.2 Assay thinking
- 论文中的prompt过于简单，没有考虑到模型的理解能力和输出问题；
    - 输出结构本身不稳定, 无法直接解析得到需要的答案
    - 代码仓库只有初始文件和最终答案的文件，模型的答案经过人工评估，是否会存在人工污染的情况？
- 没有讨论大模型输出的随机性采样对任务评估的影响
    - 不同的采样策略会导致不同的输出结果，从而影响任务的评估
- 不建议拿论文结果和自己的实验结果做对比，推理/评估过程均没对齐，建议直接对比自己的实验结果即可
- Results Analysis etc.