# LLMs4SQL Group Project

[中文说明](README_CN.md) · [Documentation](docs/README.md)

This project evaluates how large language models understand SQL, following [*Evaluating SQL Understanding in Large Language Models*](docs/2410.10680v1.pdf). The paper covers five tasks. This repository has inference and quantitative evaluation pipelines for four: syntax error detection, missing token identification, query performance prediction, and query equivalence checking. Query explanation is discussed in the report but has no quantitative pipeline here.

## Project layout

| Path | Contents |
| --- | --- |
| [`datasets/`](datasets/) | Raw and processed data, preprocessing and statistics notebooks |
| [`prompts/`](prompts/) | Task prompts used by inference |
| [`infer_model_configs/`](infer_model_configs/) | Model API and inference YAML configurations |
| [`eval_configs/`](eval_configs/) | Evaluation YAML configurations |
| [`inference_pipeline.py`](inference_pipeline.py) | Model inference for one or all four implemented tasks |
| [`evaluation_pipeline.py`](evaluation_pipeline.py) | Metrics from saved inference results |
| [`outputs/`](outputs/) | Saved predictions and metrics |
| [`docs/`](docs/README.md) | Reports, paper PDFs, notes, and video scripts |

## Run the pipelines

1. Use Python 3.10 and install dependencies from the repository root:

   ```bash
   pip install -r requirements.txt
   ```

2. Choose a YAML file in [`infer_model_configs/`](infer_model_configs/). Set `model.api_key` to your own API key, check `model.base_url` and `inference.model_name`, and set a nonempty `inference.model_identifier` for the output directory. The tracked `demo.yaml` contains placeholders and cannot call a model as supplied. Keep credentials out of commits.

3. Run inference from the repository root. Omit `--infer_option` to run all four implemented tasks, or select one:

   ```bash
   python inference_pipeline.py --config infer_model_configs/GLM-4.6.yaml --infer_option syntax_error
   ```

   Accepted options are `all`, `demo`, `syntax_error`, `missing_token`, `query_performance`, and `query_equality`. `demo` uses one built-in missing-token example. The four task options process CSV files in [`datasets/processed_data/`](datasets/processed_data/).

4. After inference results exist for the models listed in an evaluation config, run evaluation:

   ```bash
   python evaluation_pipeline.py --config eval_configs/syntax_error.yaml
   ```

   Other task configs are in [`eval_configs/`](eval_configs/). Set `evaluation.model_list` to the model output directories you actually have. Evaluation reads `evaluation.data_dir/<model>/` and writes per-model metrics plus aggregate CSV and JSON files under that task's [`outputs/`](outputs/) directory.

The inference YAML has `model` (`model_type`, `base_url`, `api_key`, `reasoning_ability`) and `inference` (`model_name`, `model_identifier`, `reasoning`, `max_workers`, and optional `stream`) sections. Evaluation YAML uses an `evaluation` section with `infer_type`, `data_dir`, and `model_list`. See the tracked YAML files for examples. The current code reads `model.api_key` directly from YAML; it does not resolve an environment-variable name.

## Results and reading

Existing results are in [`outputs/`](outputs/). Start with the [Chinese report](docs/report.md) or [English report](docs/DB_Unit_Five-report.md) for methodology and analysis. The [documentation index](docs/README.md) lists the paper, PDFs, notes, and presentation scripts.
