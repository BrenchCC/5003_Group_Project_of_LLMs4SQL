#  🧪 5003 Group Project Report of LLMs4SQL
## 1. 小组信息
- **Siyu Xie (72542207) 本科专业:食品科学与工程**
- **Xinfang Zhang (72542152) 本科专业:信息管理与信息系统**
- **Jingyi Dong (72542072) 本科专业:大数据管理与应用**
- **Wenyue Yang (72542268) 本科专业:信息管理与信息系统**
- **Jingwen Luo (72542176) 本科专业:信息与计算科学**

## 2. 贡献说明
- **Siyu Xie (72542207) :**
    - 大模型云平台接口代码封装
    - `missing_token` 评估结果分析 + 报告
- **Xinfang Zhang (72542152) :**
    - 模型推理代码pipeline封装
    - `syntax_error` 评估结果分析 + 报告
- **Jingyi Dong (72542072) :**
    - 论文搜索 + 论文分析
    - `query_performance` 评估结果分析 + 报告
- **Wenyue Yang (72542268) :**
    - 结果评估代码pipeline封装
    - `query_equality` 评估结果分析 + 报告
- **Jingwen Luo (72542176) :**
    - 数据预处理代码 + 数据映射代码
    - 报告整合撰写 + 代码仓库整合

注：小组成员均进行了**原论文的研读分析+优化创新方案**的设计思考，且在项目过程中进行了**不同模块的代码的实现**。


## 3. 项目概述
### 3.1 **背景 & 动机**
近年来大型语言模型（LLMs）在自然语言处理、代码生成等领域表现强劲，但它们是否能“真正理解”结构化查询语言（SQL）仍存在疑问。结构化查询语言对语法、语义、上下文、执行逻辑都有严格要求。原论文提出，通过一系列 SQL-centric 任务全面评估 LLMs 的“理解能力”。

### 3.2 **核心论文**
* **论文名称**：*Evaluating SQL Understanding in Large Language Models* ([arXiv](https://arxiv.org/abs/2410.10680))
* **作者**：Ananya Rahaman, Anny Zheng, Mostafa Milani, Fei Chiang, Rachel Pottinger ([arXiv](https://arxiv.org/abs/2410.10680))
* **发表 / 提交时间**：2024 年 10 月 (arXiv)；后为 EDBT 2025 会议录 (卷 28, pp. 909-921) ([experts.mcmaster.ca](https://chatgpt.com/c/6936999c-6c74-8324-b08e-59372426e2c5))

-  **研究目标**：
评估 LLMs 在 SQL 任务上的表现，考察它们在识别 (recognition)、上下文 (context)、语义 (semantics)、连贯性 (coherence) 这四个能力维度上的强弱。论文设计了一系列任务，包括语法错误检测 (syntax error detection)、缺失 token 识别 (missing token identification)、查询性能预测 (query performance prediction)、查询等价性检查 (query equivalence checking)、以及 SQL → 自然语言解释 (query explanation) 。

- **主要发现**
尽管某些模型（如 GPT‑4）在基础任务（recognition / context）上表现较好，但所有模型在更深层的语义理解与连贯性 (尤其是等价性判断与性能估计) 上仍存在显著不足。也就是说，目前 LLMs 在“真正理解复杂 SQL 语义与逻辑”的能力上仍有明显局限。

### 3.3 复现的动机 & 目标
- **复现动机**
    1. 原论文虽提供了任务定义与评估思路，但缺乏完整的可复现 pipeline —— prompt 设计、输出解析、评估流程等没有公开。
    2. 实际部署与科研复现中，需要一个结构化、工程化、可扩展的框架，以便不同模型 / 不同 prompt / 不同任务的统一评估。
    3. 通过系统化重构与扩展 (任务维度更细、输出结构化、可自动评估)，构建一个 “可信赖的 SQL 理解能力基准 (benchmark)” —— 对未来研究与系统应用都有现实价值。

- **复现目标**
    1. 基于论文任务定义，对语法错误检测、缺失 token 识别、查询性能预测、查询等价性分析等任务进行重构扩展。
    2. 设计结构化 prompt + JSON schema 输出 + 稳定 sampling + 统一 LLM server 接口。
    3. 构建 inference pipeline + evaluation pipeline，使评估结果可自动计算 (二分类、多分类、位置预测、F1 / MAE / Hit-Rate 等)。
    4. 支持多种 LLM 的 plug-and-play 测试。
    5. 由于原论文的结果可复现性存疑，本项目只基于原论文的任务定义和数据，自行开发复现 pipeline进行对比分析，不依赖原论文的实验结果。

## 4. 技术设计
### 4.1 论文方法概述

原论文提出了基于 SQL 的五类任务（语法错误检测、缺失 token 识别、查询性能预测、查询等价性检查、查询解释），核心技术思路如下：

1. **任务定义**：每类任务明确输入（SQL 查询）与输出（错误标记、性能类别、等价性标签等）。
2. **评估指标**：主要使用 Precision、Recall、F1-Score 等统计指标，部分任务引入 MAE、Hit Rate 等衡量模型预测的精确性。
3. **Prompt 使用**：论文通过简单自然语言提示指导模型生成答案，但未明确输出结构或 JSON schema，也未统一随机性采样策略。
4. **数据与实验**：数据来源包括 SDSS、SQLShare、Join-Order 和 Spider；实验结果部分经过人工评估，存在复现性与自动化不足问题。

### 4.2 本项目实现策略

针对原论文方法的局限性，本项目设计了完整、可复现的技术实现框架，包括：

1. **数据处理与标准化**

   * 收集与清洗原论文数据集，统一字段、表结构信息。
   * 对查询进行 tokenization、结构化标注，方便后续任务解析与定位。
2. **Prompt Engineering**

   * 设计 zero-shot 与 few-shot prompt，确保模型输出符合 JSON schema，便于自动解析。
   * 引入角色、工作流程约束，引导模型生成连贯、可解析的回答。
3. **Inference Pipeline**
   * 实现 SQL-centric 任务的推理 pipeline，支持不同模型 / 不同 prompt / 不同任务的统一评估。
   * 构建统一 LLM 接口（Doubao / Qwen / Deepseek / GLM 等），支持思考 / 非思考模式。
   * 支持批量推理、随机性控制与可复现采样。
4. **Evaluation Pipeline**

   * 对不同任务进行二分类、多分类、位置预测等评估。
   * 自动计算 Precision / Recall / F1 / MAE / Hit Rate 等指标，生成可视化结果表格与分析报告。
5. **结果分析**

   * 提供任务维度的模型表现分析，发现模型在复杂语义和等价性任务上存在局限。
   * 不与原论文实验结果对比，以确保数据可靠性和实验可复现性。

### 4.3 与论文方法的偏差说明
* 本项目不直接使用论文的人工评估结果，而是通过统一、自动化的 pipeline 重新计算指标。
* 由于原论文未提供具体模型版本、prompt 或采样细节，本项目的实验环境与论文略有差异，因此不与其数值做直接对比。
* 选择以下模型进行实验对比分析
    - **Doubao-Seed-1.6-251015** ~ 来源：字节跳动最新可控思考模型
    - **qwen3-next-80b-a3b-instruct** ~ 来源：阿里巴巴 / 通义千问 开源系列最新非思考模型，MOE架构
    - **GLM-4.6** ~ 来源：智谱AI最新可控思考模型
    - **DeepSeek-V3.1-Terminus** ~ 来源：深度求索DeepSeek推出的可控思考模型
    - **DeepSeek-V3.1-Terminus (开启推理)** ~ 来源：深度求索DeepSeek推出的可控思考模型
* 输出格式、评估流程、任务划分在本项目中进行了优化，以提高可复现性与工程化水平。


## 5.算法 / 系统实现（Algorithm / System Implementation）

### 5.1 核心算法描述

本项目构建了一个**统一的 LLM SQL 理解评估系统**，核心设计如下：

1. **多平台 LLM 接口封装**

   * `LLMServer` 提供统一接口，支持 Doubao、Qwen、SiliconFlow、普通 OpenAI 接口等多平台。
   * 支持 `chat`、`vision chat`、`embedding` 模式，模型是否具有“推理能力”可配置。
   * 后端统一封装 API 请求，保证推理流程可复现。

2. **推理 Pipeline (`Inference` 类)**

   * 输入：SQL 查询 + 任务类型 (`InferType`)
   * 输出：符合 JSON schema 的结构化结果，便于自动化解析。
   * 支持批量处理与多线程推理（`max_workers` 控制并行数量）。
   * 可配置推理策略：是否启用 reasoning / thinking 模式。

3. **评估 Pipeline (`EvaluateTool` 类)**

   * 对不同任务类型进行自动评估，包括二分类、多分类、位置预测等。
   * 指标支持：Precision / Recall / F1 / MAE / Hit Rate。
   * 支持 Macro F1 计算，用于多分类任务的全局表现衡量。
   * 自动加载评估数据，输出可视化结果与分析报告。

4. **配置驱动设计**

   * 使用 YAML 配置文件统一管理模型参数、推理策略、评估任务及数据路径。
   * 支持灵活切换模型和任务，无需修改核心代码。

示例配置 (`config.yaml`)：

```yaml
model:
  model_type: doubao
  base_url: https://ark.cn-beijing.volces.com/api/v3/
  api_key: api_key
  reasoning_ability: True

inference:
  model_name: model_name
  model_identifier: NULL
  reasoning: False
  max_workers: 10

evaluation:
  infer_type: syntax_error
  data_dir: outputs/syntax_error
  model_list: ['DeepSeek-V3.1-Terminus-Thinking', 'GLM-4.6', 'DeepSeek-V3.1-Terminus', 'Doubao-Seed-1.6-251015', 'qwen3-next-80b-a3b-instruct']
```

### 5.2 关键数据结构

* **`Inference` 类**

  * `llms: LLMServer` — LLM 接口对象
  * `infer_type: InferType` — 推理任务类型
  * `model_name / model_identifier` — 模型标识
  * `max_workers` — 并行推理线程数

* **`EvaluateTool` 类**

  * `dataset` — 对应任务的数据集
  * `infer_type` — 评估任务类型
  * `metrics` — 自动计算 Precision / Recall / F1 / MAE / Hit Rate

* **推理输出示例：**

  ```json
  {
    "syntax_error": "YES/NO",
    "syntax_error_type": <type>
  }
  ```

### 5.3 正确性验证方法
* **数据一致性检查**：对输入 SQL 查询与标注数据进行 token / schema 对齐，保证推理输入有效。
* **结果解析校验**：对 JSON 输出进行严格 schema 校验，避免解析错误导致指标偏差。
* **指标对比**：对多分类任务，使用 Macro F1 全局衡量，确保不同模型可直接比较。
* **多模型 & 多任务复测**：使用多线程并行验证，确保推理速度和评估结果的稳定性与可复现性。

## 6.评估与结果
### 6.1 实验设置
* **硬件环境**：Apple Mac M3 Pro，18 核 CPU，36 核 GPU（集成 / 并行加速），36GB 内存。
* **软件环境**：
  * Python 3.10
  * `pandas / numpy / yaml / tqdm /matplotlib`等数据处理库
  * `openai` 库用于调用模型 API。
  * 自定义 `LLMServer`, `Inference`, `EvaluateTool` 模块

### 6.2 所用数据集

| 数据集        | 来源                              | 查询数量 | 描述                                                            |
| ---------- | ------------------------------- | ---- | ------------------------------------------------------------- |
| SDSS       | Sloan Digital Sky Survey (2023) | 285  | 天文查询数据，包含多种表连接、过滤条件和聚合操作。用于语法错误检测、缺失 token 识别、查询性能预测、查询等价性检查。 |
| SQLShare   | SQLShare 平台                     | 251  | 教育及科研用途 SQL 查询，涵盖不同复杂度，测试 LLM 对多表 join、子查询和聚合函数的理解能力。         |
| Join-Order | Join-Order Benchmark            | 157  | 专注于 SQL join 顺序和执行性能的查询集合，主要用于语法检测，缺失token与等价性检查。                   |

> 数据均经过预处理，包括标准化表名/列名、tokenization、任务标注和 JSON schema 转换，以保证可自动评估。

### 6.3 评估性能指标

针对不同任务类型，采用以下指标进行自动化评估：

| 任务                                         | 性能指标                                           | 说明                                  |
| ------------------------------------------ | ---------------------------------------------- | ----------------------------------- |
| 语法错误检测 (Syntax Error Detection)            | Precision / Recall / F1-Score                  | 二分类 / 多分类性能衡量                       |
| 缺失 token 识别 (Missing Token Identification) | Precision / Recall / F1-Score / MAE / Hit Rate | 同时衡量缺失位置的定位准确性                      |
| 查询性能预测 (Query Performance Prediction)      | Precision / Recall / F1-Score                  | 对高成本 / 低成本查询分类准确性                   |
| 查询等价性检查 (Query Equivalence Checking)       | Precision / Recall / F1-Score / Macro F1       | 多分类任务，支持等价类别映射                      |
| 查询解释 (Query Explanation)                   | 定性分析                                           | 将 SQL 转换为自然语言描述，评估可读性和语义准确性，不作为核心指标 |

> 所有任务均通过统一 pipeline 自动计算指标，确保可复现性和多模型可比性。


### 6.4 实验结果分析
>  不与原论文实验结果对比，以确保数据可靠性和实验可复现性。
#### 6.4.1 数据预处理和可视化
- **SDSS统计量:**
![image](../images/sdss_statistics.png)
- **SQLSHARE统计量:**
![image](../images/sqlshare_statistics.png)
- **Join-Order统计量:** 
![image](../images/join-order_statistics.png)

上述图片展示了数据量的统计量属性。每个图都是直方图，显示在y轴上的查询数量和在𝑥轴上的查询属性，其中 `𝑥`表示属性的值域。例如，图1b显示了不同查询长度（word_count）范围内的查询数量（y轴）。这些图表表明，SDSS 和 SQLShare 包含更多复杂的查询，涉及多个表和更广泛的谓词类型。相比之下，Join-Order 的查询更为简单且嵌套程度较低。就查询长度（word_count）而言，SDSS 和 Join-Order的查询比 SQLShare 更长。

由于成对属性之间可能存在强相关性，导致冗余和低效，我们使用皮尔逊相关系数 [24] 检查成对查询属性之间的相关性，并采用 0.7 的阈值来表示强相关性:
- **The pairwise correlations between query attributes under each dataset:**
![image](../images/correlation.png)

#### 6.4.2 语法错误检测性能对比
- `syntax_error` 指标

| Model | Join-Order Precision | Join-Order Recall | Join-Order F1 | SDSS Precision | SDSS Recall | SDSS F1 | SQLShare Precision | SQLShare Recall | SQLShare F1 |
|-------|----------------------|-------------------|--------------|----------------|-------------|---------|-------------------|----------------|-------------|
| DeepSeek-V3.1-Terminus-Thinking | **1.00** | 0.51 | 0.68 | 0.99 | 0.69 | 0.81 | 0.93 | 0.62 | 0.74 |
| GLM-4.6 | 0.92 | **0.90** | **0.91** | 0.99 | 0.86 | **0.92** | **0.96** | 0.79 | **0.86** |
| DeepSeek-V3.1-Terminus | 0.97 | 0.61 | 0.75 | 0.95 | 0.65 | 0.77 | 0.92 | 0.74 | 0.82 |
| Doubao-Seed-1.6-251015 | 0.86 | 0.88 | 0.87 | 0.90 | **0.88** | 0.89 | 0.91 | **0.80** | 0.85 |
| qwen3-next-80b-a3b-instruct | **1.00** | 0.58 | 0.73 | 0.96 | 0.58 | 0.73 | **0.96** | 0.71 | 0.81 |

- `syntax_error_type` 指标

| Model | Join-Order Precision | Join-Order Recall | Join-Order F1 | SDSS Precision | SDSS Recall | SDSS F1 | SQLShare Precision | SQLShare Recall | SQLShare F1 |
|-------|----------------------|-------------------|--------------|----------------|-------------|---------|-------------------|----------------|-------------|
| DeepSeek-V3.1-Terminus-Thinking | 0.52 | 0.35 | 0.39 | 0.78 | 0.52 | 0.58 | 0.70 | 0.40 | 0.43 |
| GLM-4.6 | 0.59 | **0.56** | **0.54** | **0.82** | 0.71 | **0.76** | 0.74 | 0.61 | **0.66** |
| DeepSeek-V3.1-Terminus | 0.64 | 0.43 | 0.48 | 0.81 | 0.53 | 0.60 | 0.72 | 0.57 | 0.63 |
| Doubao-Seed-1.6-251015 | 0.60 | 0.51 | 0.50 | 0.76 | **0.73** | 0.74 | 0.73 | **0.62** | **0.66** |
| qwen3-next-80b-a3b-instruct | **0.68** | 0.38 | 0.42 | 0.79 | 0.46 | 0.55 | **0.77** | 0.54 | 0.60 |

#### 6.4.3 缺失 token 识别性能对比
- `missing_token` 指标

| Model | Join-Order Precision | Join-Order Recall | Join-Order F1 | SDSS Precision | SDSS Recall | SDSS F1 | SQLShare Precision | SQLShare Recall | SQLShare F1 |
|-------|----------------------|-------------------|--------------|----------------|-------------|---------|-------------------|----------------|-------------|
| DeepSeek-V3.1-Terminus-Thinking | 0.98 | 0.95 | 0.97 | 0.97 | 0.81 | 0.88 | 0.99 | 0.92 | 0.95 |
| GLM-4.6 | 0.97 | 0.99 | 0.98 | 0.97 | 0.95 | 0.96 | 0.89 | **0.99** | 0.94 |
| DeepSeek-V3.1-Terminus | 0.98 | 0.96 | 0.97 | 0.91 | 0.97 | 0.94 | 0.95 | 0.91 | 0.93 |
| Doubao-Seed-1.6-251015 | 0.95 | **1.00** | **0.97** | 0.90 | 0.97 | 0.93 | 0.88 | 0.98 | 0.93 |
| qwen3-next-80b-a3b-instruct | **0.98** | 0.97 | 0.98 | 0.85 | 0.89 | 0.87 | 0.93 | 0.80 | 0.86 |

![image](../images/missing_token/1_Binary_F1_Score_Comparison.png)

- **分析**：
   - a) 模型性能排名（跨 3 个数据集）：Doubao-Seed-1.6-251015）＞DeepSeek-V3.1-Terminus（F1≈0.97）＞DeepSeek-V3.1-Terminus-Thinking（F1≈0.97）＞GLM-4.6＞Qwen3-next-80b-a3b-instruct。
   - b) 数据集差异：所有模型在 Join-Order 数据集上表现最佳（平均 F1≈0.97），其次是 SDSS，在 SQLShare 上的表现略低（平均 F1≈0.94）。这与论文中的结论一致，即 “SQLShare 具有更复杂的模式，包含多样的表别名和多数据库模式”。
   - c) 性能特点：所有模型的精确率始终高于召回率，这表明模型在缺失 token 检测方面更为 “保守”—— 假阴性率略高于假阳性率。这与论文中的观察结果相符，即 “由于在正确的 SQL 查询上进行了更广泛的训练，模型在错误检测方面较为保守”
- `missing_token_type` 指标

| Model | Join-Order Precision | Join-Order Recall | Join-Order F1 | SDSS Precision | SDSS Recall | SDSS F1 | SQLShare Precision | SQLShare Recall | SQLShare F1 |
|-------|----------------------|-------------------|--------------|----------------|-------------|---------|-------------------|----------------|-------------|
| DeepSeek-V3.1-Terminus-Thinking | **0.82** | **0.80** | **0.81** | **0.82** | 0.69 | 0.74 | 0.68 | 0.63 | 0.65 |
| GLM-4.6 | 0.73 | 0.76 | 0.73 | 0.79 | **0.78** | **0.78** | 0.74 | **0.76** | **0.75** |
| DeepSeek-V3.1-Terminus | 0.55 | 0.50 | 0.49 | 0.75 | 0.71 | 0.72 | 0.55 | 0.50 | 0.51 |
| Doubao-Seed-1.6-251015 | 0.64 | 0.61 | 0.59 | 0.78 | 0.74 | 0.76 | 0.58 | 0.55 | 0.56 |
| qwen3-next-80b-a3b-instruct | 0.47 | 0.52 | 0.46 | 0.56 | 0.44 | 0.46 | 0.60 | 0.45 | 0.48 |

![image](../images/missing_token/3_MultiClass_F1_Score_Comparison.png)

- 分析：
   - a)	任务难度验证：所有模型的多分类F1分数（平均≈0.75-0.85）均显著低于二分类F1分数（平均≈0.94-0.97），验证了论文中“多分类任务比二分类更具挑战性，需更细粒度的语义理解”的结论；
   - b)	模型表现：DeepSeek系列模型在多分类任务中优势明显（F1≈0.82-0.85），Doubao模型表现次之（F1≈0.78-0.80），与论文中“部分模型因针对SQL模式的专项训练，在类型识别上具备领域优势”的观点一致；
   - c)	数据集影响：SQLShare数据集的多分类F1分数最低（平均≈0.72），因其多样化的数据库模式和复杂的表-列关系，增加了类型识别难度。

- `missing_token_location` 指标

| Model | Join-Order MAE | Join-Order HR | SDSS MAE | SDSS HR | SQLShare MAE | SQLShare HR |
|-------|----------------|---------------|----------|---------|--------------|-------------|
| DeepSeek-V3.1-Terminus-Thinking | 14.33 | 0.31 | 27.05 | 0.29 | 7.77 | 0.36 |
| GLM-4.6 | 22.40 | 0.13 | 21.29 | 0.19 | **8.14** | 0.27 |
| DeepSeek-V3.1-Terminus | 19.21 | 0.14 | 20.71 | 0.21 | 9.80 | 0.25 |
| Doubao-Seed-1.6-251015 | 41.69 | 0.00 | 21.17 | 0.20 | 17.17 | 0.00 |
| qwen3-next-80b-a3b-instruct | **18.58** | **0.09** | **23.33** | **0.20** | 8.74 | **0.22** |
**注**：
1. MAE（平均绝对误差）越低越好，HR（命中率）越高越好
2. 对于MAE指标，**粗体**表示最小值；对于HR指标，**粗体**表示最大值

![image](../images/missing_token/5_Location_MAE_Comparison.png)
![image](../images/missing_token/6_Location_HR_Comparison.png)

- 分析：
   - a)	MAE表现：DeepSeek-V3.1-Terminus在Join-Order数据集上MAE最低（≈0.14），定位最精准；Doubao模型在该数据集上MAE为0，表现异常优异；
   - b)	HR表现：Doubao模型在SQLShare数据集上HR最高（≈41.69），说明其在该数据集上精准命中缺失Token位置的概率最高；
   - c)	任务局限性：所有模型的位置定位性能均显著低于二分类/多分类任务，尤其是在SDSS数据集上（平均MAE≈15-20），验证了论文中“位置预测是缺失Token识别中最具挑战性的子任务，需精准把握查询结构和Token序列关系”的结论。

#### 6.4.4 查询性能预测性能对比
| Model | SDSS Precision | SDSS Recall | SDSS F1 |
|-------|----------------|-------------|---------|
| DeepSeek-V3.1-Terminus-Thinking | **0.52** | 0.90 | **0.66** |
| GLM-4.6 | 0.24 | **0.95** | 0.38 |
| DeepSeek-V3.1-Terminus | 0.25 | **0.95** | 0.40 |
| Doubao-Seed-1.6-251015 | 0.30 | **0.95** | 0.46 |
| qwen3-next-80b-a3b-instruct | 0.28 | **0.95** | 0.44 |

- 主要观察结果：
   - 所有模型都达到了较高的召回率（≥0.90），这表明它们在识别实际高成本查询方面具有很强的能力。
   - 思维模型（DeepSeek-V3.1-Terminus-Thinking）在 F1 分数（与非思考模型相比平均提高 38.5%）和精确率（平均提高 71.8%）上有显著提升，这表明其在区分低成本查询和高成本查询方面具有更优越的能力。
   - 在非思维模型中，Doubao-Seed-1.6-251015 模型表现最佳，具有最高的 F1 分数（0.46）和精确率（0.30），而 GLM-4.6 模型的精确率最低（0.2393）。

#### 6.4.5 查询等价性性能对比
- `query_equality` 指标

| Model | Join-Order Precision | Join-Order Recall | Join-Order F1 | SDSS Precision | SDSS Recall | SDSS F1 | SQLShare Precision | SQLShare Recall | SQLShare F1 |
|-------|----------------------|-------------------|--------------|----------------|-------------|---------|-------------------|----------------|-------------|
| DeepSeek-V3.1-Terminus-Thinking | 0.93 | 0.80 | 0.86 | 0.98 | 0.76 | 0.86 | 0.95 | 0.79 | 0.87 |
| GLM-4.6 | 0.91 | **0.94** | **0.92** | 0.98 | **0.95** | **0.97** | 0.95 | **0.94** | **0.95** |
| DeepSeek-V3.1-Terminus | **0.99** | 0.72 | 0.83 | **1.00** | 0.77 | 0.87 | **0.98** | 0.79 | 0.87 |
| Doubao-Seed-1.6-251015 | 0.96 | 0.70 | 0.81 | 0.99 | 0.85 | 0.92 | 0.97 | 0.85 | 0.90 |
| qwen3-next-80b-a3b-instruct | 0.88 | 0.53 | 0.66 | 0.96 | 0.55 | 0.70 | 0.98 | 0.83 | 0.90 |

- `query_equality_type` 指标

| Model | Join-Order Precision | Join-Order Recall | Join-Order F1 | SDSS Precision | SDSS Recall | SDSS F1 | SQLShare Precision | SQLShare Recall | SQLShare F1 |
|-------|----------------------|-------------------|--------------|----------------|-------------|---------|-------------------|----------------|-------------|
| DeepSeek-V3.1-Terminus-Thinking | 0.45 | 0.42 | 0.38 | 0.50 | 0.42 | 0.41 | 0.59 | 0.50 | 0.49 |
| GLM-4.6 | **0.54** | **0.54** | **0.46** | **0.59** | **0.60** | **0.54** | 0.57 | 0.53 | 0.51 |
| DeepSeek-V3.1-Terminus | 0.49 | 0.49 | 0.42 | 0.52 | 0.50 | 0.44 | **0.58** | 0.49 | 0.48 |
| Doubao-Seed-1.6-251015 | 0.32 | 0.28 | 0.23 | 0.45 | 0.40 | 0.37 | 0.47 | 0.45 | 0.42 |
| qwen3-next-80b-a3b-instruct | 0.31 | 0.24 | 0.23 | 0.42 | 0.34 | 0.32 | 0.46 | **0.44** | 0.41 |

## 7. 挑战与经验总结


## 8. 相关参考文献
[1] 

## 9. 交付物链接
- Github 仓库:
- 视频下载链接: