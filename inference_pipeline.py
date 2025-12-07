import os
import sys
import json
import yaml
import logging
import argparse

from utils.llm_server import LLMServer
from inference.infer import Inference
from inference.infer_type import InferType

def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type = str, default = "infer_model_configs/DeepSeek-V3.1-Terminus.yaml")
    parser.add_argument('--infer_option', type = str, default = "all", help = "[all, syntax_error, missing_token, query_performance, query_equality]")
    return parser.parse_args()

logger = logging.getLogger(__name__)

def parse_config(config_path):
    logger.info(f"Loading config from {config_path}")
    with open(config_path, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    model_config = config["model"]
    infer_config = config["inference"]
    logger.info("model_config and inference_config loaded successfully")
    return model_config, infer_config

def infer_type_mapping(infer_option: str) -> InferType:
    if infer_option == "syntax_error":
        return InferType.SYNTAX_ERROR
    elif infer_option == "missing_token":
        return InferType.MISSING_TOKEN
    elif infer_option == "query_performance":
        return InferType.QUERY_PERFORMANCE
    elif infer_option == "query_equality":
        return InferType.QUERY_EQUALITY

def initialize_inference_system(model_config: dict, infer_config: dict, infer_type: InferType):
    llm_server = LLMServer(
        base_url = model_config["base_url"],
        api_key = model_config["api_key"],
        model_type= model_config["model_type"],
        reasoning_ability = model_config["reasoning_ability"],
    )

    inference = Inference(
        llms = llm_server,
        infer_type = infer_type,
        model_name = infer_config["model_name"],
        doubao_model_name = infer_config.get("doubao_model_name"),
        reasoning = infer_config["reasoning"],
        max_workers = infer_config["max_workers"],
    )
    logger.info("Inference system initialized")
    return inference

def single_infer_pipeline(config_path, infer_option):
    model_config, infer_config = parse_config(config_path)
    if infer_option == "all":
        logger.info("infer_option is all, not match single infer pipeline")
        return None

    infer_type = infer_type_mapping(infer_option)

    inference = initialize_inference_system(model_config, infer_config, infer_type)

    results = inference.infer_batch()
    if inference.llms.model_type == "doubao":
        logger.info(f"{inference.doubao_model_name} infer for {infer_option} has finished")
    else:
        logger.info(f"{inference.model_name} infer for {infer_option} has finished")

    return results

def all_infer_pipeline(config_path, infer_option = "all"):
    model_config, infer_config = parse_config(config_path)
    infer_options = ["syntax_error", "missing_token", "query_performance", "query_equality"]
    logger.info(f"infer_option is all, now infer in all pipeline for {infer_option}")

    for idx, infer_option in enumerate(infer_options):
        infer_type = infer_type_mapping(infer_option)
        logger.info(f"Now infer for {infer_type}")
        results = single_infer_pipeline(config_path, infer_option)
        if results is not None:
            logger.info(f"Dimension {idx+1} has successfully inferred")
    return None

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

    args = args_parser()

    config_path = args.config
    infer_option = args.infer_option

    # single_infer_pipeline(config_path, infer_option)
    if infer_option == "all":
        all_infer_pipeline(config_path, infer_option)
    else:
        single_infer_pipeline(config_path, infer_option)