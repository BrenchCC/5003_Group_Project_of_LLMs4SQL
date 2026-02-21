# 5003 Group Project of LLMs4SQL
Evaluate LLMs for SQL understanding and execution across five task-specific metrics, with reproducible inference and evaluation pipelines.

## Quick Start
```bash
git clone https://github.com/BrenchCC/5003_Group_Project_of_LLMs4SQL
cd 5003_Group_Project_of_LLMs4SQL

conda create -n llms4sql python==3.10
conda activate llms4sql
pip install -r requirements.txt
```

## Repository Structure
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

## Datasets
- Raw data and stats: `datasets/raw_data`
- Dataset statistics: `datasets/raw_data/datasets_stats.ipynb`
- Data mapping: `datasets/data_tranform.ipynb`

## Documents
- Course tutorial (Chinese): `docs/course_tutorial.md`
- Project report: `docs/report.md`
- Project report (PDF): `docs/report.pdf`
- Assay summary and thinking: `docs/summary_of_assay.md`

## Models Evaluated
- Doubao-Seed-1.6-251015 (no reasoning)
- qwen3-next-80b-a3b-instruct (no reasoning)
- GLM-4.6 (no reasoning)
- DeepSeek-V3.1-Terminus / deepseek-v3.1 (no reasoning)
- DeepSeek-V3.1-Terminus / deepseek-v3.1 (reasoning)

## Inference Pipeline
1. Prepare model configs in `infer_model_configs/`
2. Prepare prompts in `prompts/`
3. Run inference:
```bash
python inference_pipeline.py --config infer_model_configs/demo.yaml --infer_option <all|demo|syntax_error|query_equality|query_performance|missing_token>
```

## Evaluation Pipeline
1. Prepare evaluation configs in `eval_configs/`
2. Run evaluation:
```bash
python evaluation_pipeline.py --config eval_configs/demo.yaml
```

## Reproducibility Checklist
1. Confirm dataset files exist in `datasets/processed_data/`
2. Confirm prompts exist in `prompts/`
3. Prepare model configs in `infer_model_configs/`
4. Run inference
5. Run evaluation
6. Collect results from `outputs/`

## Output Artifacts
All outputs are saved under `outputs/`, grouped by task and model name.

## Configuration Details
### Model Configs (`infer_model_configs/`)
Use YAML to define inference targets. Required fields typically include:
- `model_name`: readable model id for output folders
- `provider`: inference backend or API identifier
- `base_url`: API endpoint
- `api_key_env`: environment variable name for the API key
- `temperature`, `max_tokens`: generation settings

Example (minimal):
```yaml
model_name: demo-model
provider: openai_compatible
base_url: https://api.example.com/v1
api_key_env: DEMO_API_KEY
temperature: 0.0
max_tokens: 2048
```

### Evaluation Configs (`eval_configs/`)
Use YAML to define evaluation targets and dataset paths. Required fields typically include:
- `task`: one of `syntax_error`, `query_equality`, `query_performance`, `missing_token`
- `input_path`: dataset path
- `output_dir`: output folder

Example (minimal):
```yaml
task: syntax_error
input_path: datasets/processed_data/syntax_error_join.csv
output_dir: outputs/syntax_error
```

