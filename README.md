# 5003 Group Project of LLMs4SQL
> A group project repository focused on evaluating large language models’ understanding of SQL.
> It assesses models across five task-specific metrics, providing a comprehensive measurement of their SQL query comprehension and execution capabilities.

**How to get repo files:**
- 1. using git clone command as follow command **(ensure you have installed git)**:
    ``` bash
    git clone https://github.com/BrenchCC/5003_Group_Project_of_LLMs4SQL
    ```
- 2. download zip file

## 1. Python Environment Installation Guidance
### 1.1 Create a Python Environment by conda command
```bash
conda create -n llms4sql python==3.10 

conda activate llms4sql
```

### 1.2 Install the Required Packages
```bash
pip install -r requirements.txt
```

### 1.3 Code Instruction
```ascii
.
├── datasets
│   ├── data_tranform.ipynb
│   ├── processed_data
│   │   ├── equi_join_mapping.csv
│   │   ├── equi_join.csv
│   │   ├── equi_sdss_mapping.csv
│   │   ├── equi_sdss.csv
│   │   ├── equi_sqlshare_mapping.csv
│   │   ├── equi_sqlshare.csv
│   │   ├── missing_token_join.csv
│   │   ├── missing_token_sdss.csv
│   │   ├── missing_token_sqlshare.csv
│   │   ├── sdss_runtime.csv
│   │   ├── spider_dataset_with_error.csv
│   │   ├── syntax_error_join.csv
│   │   ├── syntax_error_sdss.csv
│   │   └── syntax_error_sqlshare.csv
│   └── raw_data
│       ├── datasets_stats.ipynb
│       ├── images
│       ├── README.md
│       ├── Stats
│       └── Tasks
├── docs
│   ├── 2410.10680_zh_CN.pdf
│   ├── 2410.10680v1.pdf
├── eval_configs
│   ├── demo.yaml
│   ├── missing_token.yaml
│   ├── query_equality.yaml
│   ├── query_performance.yaml
│   └── syntax_error.yaml
├── evaluation_pipeline.py
├── infer_model_configs
│   ├── DeepSeek-V3.1-Terminus-Thinking.yaml
│   ├── DeepSeek-V3.1-Terminus.yaml
│   ├── demo.yaml
│   ├── Doubao-Seed-1.6-251015.yaml
│   ├── GLM-4.6.yaml
│   └── qwen3-next-80b-a3b-instruct.yaml
├── inference
│   ├── __init__.py
│   ├── evaluate.py
│   ├── infer_type.py
│   └── infer.py
├── inference_pipeline.py
├── LICENSE
├── outputs
│   ├── missing_token
│   │   ├── DeepSeek-V3.1-Terminus
│   │   ├── DeepSeek-V3.1-Terminus-Thinking
│   │   ├── Doubao-Seed-1.6-251015
│   │   ├── GLM-4.6
│   │   ├── missing_token_5_models_evaluation.csv
│   │   ├── missing_token_location_5_models_evaluation.csv
│   │   ├── missing_token_type_5_models_evaluation.csv
│   │   └── qwen3-next-80b-a3b-instruct
│   ├── query_equality
│   │   ├── DeepSeek-V3.1-Terminus
│   │   ├── DeepSeek-V3.1-Terminus-Thinking
│   │   ├── Doubao-Seed-1.6-251015
│   │   ├── GLM-4.6
│   │   ├── query_equality_5_models_evaluation.csv
│   │   ├── query_equality_type_5_models_evaluation.csv
│   │   └── qwen3-next-80b-a3b-instruct
│   ├── query_performance
│   │   ├── DeepSeek-V3.1-Terminus
│   │   ├── DeepSeek-V3.1-Terminus-Thinking
│   │   ├── Doubao-Seed-1.6-251015
│   │   ├── GLM-4.6
│   │   ├── query_performance_5_models_evaluation.csv
│   │   └── qwen3-next-80b-a3b-instruct
│   └── syntax_error
│       ├── DeepSeek-V3.1-Terminus
│       ├── DeepSeek-V3.1-Terminus-Thinking
│       ├── Doubao-Seed-1.6-251015
│       ├── GLM-4.6
│       ├── qwen3-next-80b-a3b-instruct
│       ├── syntax_error_5_models_evaluation.csv
│       └── syntax_error_type_5_models_evaluation.csv
├── prompts
│   ├── missing_token.md
│   ├── query_equality.md
│   ├── query_performance.md
│   └── syntax_error.md
├── README.md
├── Reference
│   ├── README_CN.md
│   ├── README.md
│   └── results.ipynb
├── requirements.txt
└── utils
    ├── __init__.py
    ├── api_recording.json
    └── llm_server.py
```
## 2. Dataset Instruction 
- Details in [datasets](datasets/raw_data)
- [Data Preprocessing Code](datasets/raw_data/datasets_stats.ipynb)
- [Data Mapping Code](datasets/data_tranform.ipynb) 

## 3. Model Using Overview
- Doubao-Seed-1.6-251015 ~ no reasoning
- qwen3-next-80b-a3b-instruct ~ no reasoning
- GLM-4.6 ~ no reasoning
- DeepSeek-V3.1-Terminus(deepseek-v3.1)~ no reasoning
- DeepSeek-V3.1-Terminus(deepseek-v3.1)~ reasoning

## 4. Inference Pipeline
- 4.1 Inference Configs
  - [infer_model_configs](infer_model_configs/demo.yaml): **Prepare your own model configs and put here**
  - [Prompts](prompts/): **Prompt Engineering for different tasks**
- 4.2 Inference Pipeline
  - [inference_pipeline.py](inference_pipeline.py)
  - using:
  ```bash
    python inference_pipeline.py --configs infer_model_configs/demo.yaml --infer_option <[all, syntax_error, query_equality, query_performance, missing_token]>
  ```

## 5. Evaluation Pipeline
- 5.1 Evaluation Configs
  - [eval_configs](eval_configs/demo.yaml): **Prepare your own evaluation configs**
- 5.2 Evaluation Pipeline
  - [evaluation_pipeline.py](evaluation_pipeline.py)
  - using:
  ```bash
    python evaluation_pipeline.py --configs eval_configs/demo.yaml
  ```



