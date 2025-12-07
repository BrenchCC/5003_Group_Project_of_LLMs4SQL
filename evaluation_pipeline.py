import os
import sys
import json
import yaml
import logging
import argparse
from typing import Dict, Tuple, List

sys.path.append(os.getcwd())
from inference.evaluate import EvaluateTool 
from inference.infer_type import InferType 

import pandas as pd

logger = logging.getLogger("Evaluation_Pipeline")  
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ]
)

def args_parser():
    parser = argparse.ArgumentParser(description="Evaluation Pipeline for LLMs4SQL")
    parser.add_argument("--config", type=str, default = "eval_configs/demo.yaml", help="Path to the evaluation config file")
    return parser.parse_args()

def load_evaluation_config(config_path: str) -> list:
    config_path = os.path.abspath(config_path)

    if not os.path.exists(config_path):
        logger.error(f"Config file {config_path} not found")
        raise FileNotFoundError(f"Config file {config_path} not found")
    
    with open(config_path, "r") as f:
        configs = yaml.safe_load(f)
    logger.info(f"Evaluation config loaded from {config_path}")
    logger.info(f"Evaluation config: {configs}")
    return configs["evaluation"]

def infer_type_mapping(infer_type: str) -> InferType:
    if infer_type == "syntax_error":
        return InferType.SYNTAX_ERROR
    elif infer_type == "missing_token":
        return InferType.MISSING_TOKEN
    elif infer_type == "query_performance": 
        return InferType.QUERY_PERFORMANCE
    elif infer_type == "query_equality":
        return InferType.QUERY_EQUALITY

def results2csv(df:pd.DataFrame, output_path):
    os.makedirs(os.path.dirname(output_path),exist_ok = True)
    df.to_csv(output_path)

def get_mertrics(infer_type: InferType, model_eval_data_dir: str):
    model_eval_data_dir = os.path.abspath(model_eval_data_dir)
    metrics_data_path = os.path.join(model_eval_data_dir, f"{infer_type.value}_metrics.json")
    logger.info(f"The Target metrics file of {infer_type.value} is {metrics_data_path}")

    if os.path.exists(metrics_data_path):
        with open(metrics_data_path, "r") as f:
            metrics_results = json.load(f)
            logger.info(f"Metrics results loaded from {metrics_data_path}")
            return metrics_results
    else:
        logger.info(f"Metrics file {metrics_data_path} not found, start to evaluate")
        evaluate_tool = EvaluateTool(model_eval_data_dir, infer_type)
        metrics_results = evaluate_tool.evaluate()
        logger.info(f"Metrics results evaluated and saved to {metrics_data_path}")
        return metrics_results



def evaluate_pipeline(configs: dict):
    infer_type = infer_type_mapping(configs["infer_type"])
    data_dir = configs["data_dir"]
    model_list = configs["model_list"]

    total_metrics_results = {}

    for model_name in model_list:
        model_eval_data_dir = os.path.join(data_dir, model_name)
        logger.info(f"Start to evaluate {infer_type} for: model {model_name}")
        
        model_eval_data_dir = os.path.abspath(model_eval_data_dir)
        if not os.path.exists(model_eval_data_dir):
            logger.error(f"Model evaluation data directory {model_eval_data_dir} not found")
            continue
        
        metrics_results = get_mertrics(infer_type, model_eval_data_dir)
        total_metrics_results[model_name] = metrics_results

    logger.info(f"Total metrics results have been evaluated, model_nums = {len(model_list)}")

    total_metrics_tables = dict_to_tables(total_metrics_results)

    for metric, metric_df in total_metrics_tables.items():
        output_path =  os.path.join(data_dir, f"{metric}_{len(total_metrics_results)}_models_evaluation.csv")
        results2csv(metric_df, output_path)
        logger.info(f"{metric} results have been saved to {output_path}")
    return total_metrics_tables



def dict_to_tables(results: dict) -> Dict[str, pd.DataFrame]:
    models = list(results.keys())
    datasets = set()
    metric_groups = set()  
    metric_names_by_group = {}  
    
    # groupby
    for model_dict in results.values():
        for dataset, ds_dict in model_dict.items():
            datasets.add(dataset)
            for metric_group, metrics_dict in ds_dict.items():
                metric_groups.add(metric_group)
                if metric_group not in metric_names_by_group:
                    metric_names_by_group[metric_group] = set()
                metric_names_by_group[metric_group].update(metrics_dict.keys())
    
    # sorted
    models = sorted(models)
    datasets = sorted(datasets)
    metric_groups = sorted(metric_groups)
    
    dfs = {}
    
    for metric_group in metric_groups:
        metric_names = sorted(metric_names_by_group[metric_group])
        
        # build multi_index
        columns = pd.MultiIndex.from_product([datasets, metric_names])
        
        # create df
        df = pd.DataFrame(index=models, columns=columns)
        
        # fill data
        for model, model_dict in results.items():
            for dataset, ds_dict in model_dict.items():
                if metric_group in ds_dict:
                    for metric_name, value in ds_dict[metric_group].items():
                        df.loc[model, (dataset, metric_name)] = value
        
        dfs[metric_group] = df
    
    return dfs


if __name__ == "__main__":
    args = args_parser()
    configs = load_evaluation_config(args.config)
    logger.info(configs)
    total_metrics_tables = evaluate_pipeline(configs)
