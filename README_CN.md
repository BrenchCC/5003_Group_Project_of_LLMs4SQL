# LLMs4SQL 小组项目

[English README](README.md) · [文档索引](docs/README.md)

本项目参考论文 [*Evaluating SQL Understanding in Large Language Models*](docs/2410.10680v1.pdf)，评估大语言模型的 SQL 理解能力。论文涉及五项任务；仓库为其中四项提供推理与量化评估流程：语法错误检测、缺失 token 识别、查询性能预测和查询等价性判断。查询解释在报告中讨论，但仓库没有对应的量化流程。

## 项目目录

| 路径 | 内容 |
| --- | --- |
| [`datasets/`](datasets/) | 原始与处理后的数据、预处理及统计 Notebook |
| [`prompts/`](prompts/) | 推理使用的各任务提示词 |
| [`infer_model_configs/`](infer_model_configs/) | 模型 API 与推理 YAML 配置 |
| [`eval_configs/`](eval_configs/) | 评估 YAML 配置 |
| [`inference_pipeline.py`](inference_pipeline.py) | 执行单项或全部四项任务的推理 |
| [`evaluation_pipeline.py`](evaluation_pipeline.py) | 根据已保存的结果计算与汇总指标 |
| [`outputs/`](outputs/) | 各模型预测结果与指标 |
| [`docs/`](docs/README.md) | 报告、论文 PDF、项目笔记和视频讲稿 |

## 运行流程

1. 使用 Python 3.10，在仓库根目录安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

2. 从 [`infer_model_configs/`](infer_model_configs/) 选择 YAML 配置，填入自己的 `model.api_key`，核对 `model.base_url` 与 `inference.model_name`，并设置非空的 `inference.model_identifier` 作为输出目录名。仓库中的 `demo.yaml` 含占位值，不能直接调用模型。不要提交密钥。

3. 在仓库根目录运行推理。省略 `--infer_option` 会执行四项已实现任务，也可指定单项任务：

   ```bash
   python inference_pipeline.py --config infer_model_configs/GLM-4.6.yaml --infer_option syntax_error
   ```

   可选值：`all`、`demo`、`syntax_error`、`missing_token`、`query_performance`、`query_equality`。`demo` 使用代码内置的一条缺失 token 示例；四项任务使用 [`datasets/processed_data/`](datasets/processed_data/) 中的 CSV。

4. 相应模型的推理结果齐备后，运行评估：

   ```bash
   python evaluation_pipeline.py --config eval_configs/syntax_error.yaml
   ```

   其他任务配置见 [`eval_configs/`](eval_configs/)。将 `evaluation.model_list` 改为实际存在的模型输出目录。评估读取 `evaluation.data_dir/<model>/`，并在该任务的 [`outputs/`](outputs/) 目录下写入模型指标及汇总 CSV、JSON 文件。

推理 YAML 分为 `model`（`model_type`、`base_url`、`api_key`、`reasoning_ability`）与 `inference`（`model_name`、`model_identifier`、`reasoning`、`max_workers`，以及可选的 `stream`）。评估 YAML 的 `evaluation` 节包含 `infer_type`、`data_dir`、`model_list`。完整写法参见仓库中的 YAML。当前代码直接读取 YAML 中的 `model.api_key`，不会解析环境变量名。

## 结果与文档

已有结果位于 [`outputs/`](outputs/)。方法和分析可阅读[中文报告](docs/report.md)或[英文报告](docs/DB_Unit_Five-report.md)。论文、PDF、项目笔记和视频讲稿见[文档索引](docs/README.md)。
