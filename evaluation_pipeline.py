import os
import sys
import json
import yaml
import logging
import argparse
from typing import Dict, List, Any

sys.path.append(os.getcwd())

from inference.evaluate import EvaluateTool
from inference.infer_type import InferType

import pandas as pd

# Logging setup
logger = logging.getLogger("Evaluation_Pipeline")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

# Argument parser
def args_parser():
    """Parse command line arguments for evaluation pipeline."""
    parser = argparse.ArgumentParser(description="Evaluation Pipeline for LLMs4SQL")
    parser.add_argument(
        "--config",
        type=str,
        default="eval_configs/demo.yaml",
        help="Path to evaluation config file",
    )
    return parser.parse_args()

# Load config
def load_evaluation_config(config_path: str) -> List[dict]:
    """
    Load evaluation configs from YAML file.

    Parameters:
        config_path (str): Path to YAML config.

    Returns:
        list: A list of evaluation configurations.
    """
    config_path = os.path.abspath(config_path)

    if not os.path.exists(config_path):
        logger.error(f"Config file not found: {config_path}")
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        configs = yaml.safe_load(f)

    logger.info(f"Evaluation config loaded from: {config_path}")
    logger.info(f"Config content: {configs}")

    return configs.get("evaluation", [])

# InferType mapping
def infer_type_mapping(infer_type: str) -> InferType:
    """Map infer_type string to InferType enum."""
    mapping = {
        "syntax_error": InferType.SYNTAX_ERROR,
        "missing_token": InferType.MISSING_TOKEN,
        "query_performance": InferType.QUERY_PERFORMANCE,
        "query_equality": InferType.QUERY_EQUALITY,
    }
    return mapping[infer_type]

# Write CSV
def results2csv(df: pd.DataFrame, output_path: str):
    """Save DataFrame to CSV, creating directories if needed."""
    os.makedirs(os.path.dirname(output_path), exist_ok = True)
    df.to_csv(output_path)
    logger.info(f"Saved metrics table to: {output_path}")

def results2json(results: dict, output_path: str):
    """Save metrics dict to JSON, creating directories if needed."""
    os.makedirs(os.path.dirname(output_path), exist_ok = True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent = 2)
    logger.info(f"Saved metrics JSON to: {output_path}")

# Load or compute metrics
def get_metrics(infer_type: InferType, model_eval_data_dir: str) -> Dict[str, Any]:
    """
    Load metrics JSON or compute metrics using EvaluateTool.

    Parameters:
        infer_type (InferType): Type of inference.
        model_eval_data_dir (str): Path to model evaluation data.

    Returns:
        dict: Metrics results.
    """
    model_eval_data_dir = os.path.abspath(model_eval_data_dir)
    metrics_path = os.path.join(model_eval_data_dir, f"{infer_type.value}_metrics.json")

    logger.info(f"Looking for metrics file: {metrics_path}")

    if os.path.exists(metrics_path):
        logger.info(f"Metrics found. Loading: {metrics_path}")
        with open(metrics_path, "r") as f:
            return json.load(f)

    logger.info(f"Metrics file not found. Evaluating: {model_eval_data_dir}")
    evaluate_tool = EvaluateTool(model_eval_data_dir, infer_type)
    metrics_results = evaluate_tool.evaluate()
    logger.info(f"Metrics evaluated and saved to: {metrics_path}")

    return metrics_results

# Convert metrics dict → multiple metrics tables
def dict_to_tables(results: dict) -> Dict[str, pd.DataFrame]:
    """
    Convert nested metrics dict into a group of tables.

    Structure:
    results[model][dataset][metric_group][metric_name] = value
    """
    models = sorted(results.keys())
    datasets = set()
    metric_groups = set()
    metric_names_by_group = {}

    # Collect all keys
    for model_dict in results.values():
        for dataset, ds_dict in model_dict.items():
            datasets.add(dataset)

            for group, metrics_dict in ds_dict.items():
                metric_groups.add(group)
                metric_names_by_group.setdefault(group, set()).update(metrics_dict.keys())

    datasets = sorted(datasets)
    metric_groups = sorted(metric_groups)

    tables = {}

    # Build tables
    for group in metric_groups:
        metric_names = sorted(metric_names_by_group[group])

        columns = pd.MultiIndex.from_product([datasets, metric_names])
        df = pd.DataFrame(index=models, columns=columns)
        df.index.name = "models"

        for model, model_dict in results.items():
            for dataset, ds_dict in model_dict.items():
                if group in ds_dict:
                    for metric_name, value in ds_dict[group].items():
                        df.loc[model, (dataset, metric_name)] = value

        tables[group] = df

    logger.info(f"Constructed {len(tables)} metric tables")
    return tables

# Evaluation pipeline
def evaluate_pipeline(configs: dict):
    """
    Run evaluation pipeline:
    - Evaluate each model
    - Collect metrics
    - Build metrics tables
    - Save results
    """
    infer_type = infer_type_mapping(configs["infer_type"])
    data_dir = configs["data_dir"]
    model_list = configs["model_list"]

    logger.info(f"Starting evaluation pipeline for infer_type: {infer_type.value}")

    total_metrics = {}

    for model_name in model_list:
        model_dir = os.path.join(data_dir, model_name)
        model_dir = os.path.abspath(model_dir)

        logger.info(f"Evaluating model: {model_name}")

        if not os.path.exists(model_dir):
            logger.error(f"Model directory not found: {model_dir}")
            continue

        metrics = get_metrics(infer_type, model_dir)
        total_metrics[model_name] = metrics

    logger.info(f"Collected metrics from {len(total_metrics)} models")

    metrics_tables = dict_to_tables(total_metrics)

    # Save tables
    for group, df in metrics_tables.items():
        out_path = os.path.join(data_dir, f"{group}_{len(metrics_tables)}_models.csv")
        results2csv(df, out_path)
    output_json_path = os.path.join(data_dir, f"{infer_type.value}_metrics.json")
    results2json(total_metrics, output_json_path)
    return metrics_tables


if __name__ == "__main__":
    args = args_parser()
    configs = load_evaluation_config(args.config)
    logger.info(f"Loaded config: {configs}")
    evaluate_pipeline(configs)
