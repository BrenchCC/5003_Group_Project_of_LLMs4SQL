# 5003 Group Project of LLMs4SQL
评测大语言模型对 SQL 的理解与执行能力，覆盖 5 类任务指标，并提供可复现实验流程与结果产物。

## 快速开始
```bash
git clone https://github.com/BrenchCC/5003_Group_Project_of_LLMs4SQL
cd 5003_Group_Project_of_LLMs4SQL

conda create -n llms4sql python==3.10
conda activate llms4sql
pip install -r requirements.txt
```

## 目录结构
```text
.
├── datasets
│   ├── data_tranform.ipynb
│   ├── processed_data
│   └── raw_data
├── docs
├── eval_configs
├── evaluation_pipeline.py
├── infer_model_configs
├── inference
├── inference_pipeline.py
├── outputs
├── prompts
├── Reference
├── requirements.txt
└── utils
```

## 数据集
- 原始数据与统计脚本：`datasets/raw_data`
- 数据统计脚本：`datasets/raw_data/datasets_stats.ipynb`
- 数据映射脚本：`datasets/data_tranform.ipynb`

## 文档
- 课程教程（中文）：`docs/course_tutorial.md`
- 课程报告：`docs/report.md`
- 课程报告（PDF）：`docs/report.pdf`
- 实验总结与思考：`docs/summary_of_assay.md`

## 模型概览
- Doubao-Seed-1.6-251015（无推理）
- qwen3-next-80b-a3b-instruct（无推理）
- GLM-4.6（无推理）
- DeepSeek-V3.1-Terminus / deepseek-v3.1（无推理）
- DeepSeek-V3.1-Terminus / deepseek-v3.1（推理）

## 推理流程
1. 在 `infer_model_configs/` 准备模型配置
2. 在 `prompts/` 准备提示词
3. 运行推理：
```bash
python inference_pipeline.py --config infer_model_configs/demo.yaml --infer_option <all|demo|syntax_error|query_equality|query_performance|missing_token>
```

## 评测流程
1. 在 `eval_configs/` 准备评测配置
2. 运行评测：
```bash
python evaluation_pipeline.py --config eval_configs/demo.yaml
```

## 复现实验清单
1. 确认 `datasets/processed_data/` 数据齐全
2. 确认 `prompts/` 已准备
3. 配置 `infer_model_configs/`
4. 运行推理
5. 运行评测
6. 在 `outputs/` 收集结果

## 结果输出
所有结果产物位于 `outputs/`，按任务类型与模型名称组织。

## 配置说明
### 推理配置（`infer_model_configs/`）
使用 YAML 定义推理目标，常见字段：
- `model_name`：模型名称，用于结果目录命名
- `provider`：推理后端或 API 类型
- `base_url`：API 地址
- `api_key_env`：API Key 的环境变量名
- `temperature`, `max_tokens`：生成参数

示例（最小配置）：
```yaml
model_name: demo-model
provider: openai_compatible
base_url: https://api.example.com/v1
api_key_env: DEMO_API_KEY
temperature: 0.0
max_tokens: 2048
```

### 评测配置（`eval_configs/`）
使用 YAML 定义评测目标与数据路径，常见字段：
- `task`：`syntax_error` / `query_equality` / `query_performance` / `missing_token`
- `input_path`：数据路径
- `output_dir`：输出目录

示例（最小配置）：
```yaml
task: syntax_error
input_path: datasets/processed_data/syntax_error_join.csv
output_dir: outputs/syntax_error
```

