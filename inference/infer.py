import os
import sys
import math
import json
import logging
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import json_repair
from tqdm import tqdm

sys.path.append(os.getcwd())
from inference.infer_type import InferType, OUTPUT_KEY
from utils.llm_server import LLMServer


logger = logging.getLogger("Inference")


DATA = {
    "syntax_error": ["syntax_error_join.csv", "syntax_error_sdss.csv", "syntax_error_sqlshare.csv"],
    "missing_token": ["missing_token_join.csv", "missing_token_sdss.csv", "missing_token_sqlshare.csv"],
    "query_performance": ["sdss_runtime.csv"],
    "query_equality": ["equi_join_mapping.csv", "equi_sdss_mapping.csv", "equi_sqlshare_mapping.csv"]
}

TARGET_KEY = {
    "syntax_error": ["Modified_Statement"],
    "missing_token": ["Modified_Statements"],
    "query_performance": ["SQL_Statement"],
    "query_equality": ["SQL_Statement", "Equivalent_Queries"]
}

PROMPT = {
    "syntax_error": "prompts/syntax_error.md",
    "missing_token": "prompts/missing_token.md",
    "query_performance": "prompts/query_performance.md",
    "query_equality": "prompts/query_equality.md"
}



def clean_row(text):
    if isinstance(text, float) and math.isnan(text):
            text = ""
    if text == "N/A" or text == "nan":
        text = ""
    return text

class Inference:
    """
    Cleaned and modular version of your inference pipeline.
    The public usage remains unchanged.
    """

    def __init__(
        self,
        llms: LLMServer,
        model_name: str,
        infer_type: InferType,
        data_dir: str = "datasets/processed_data",
        model_identifier: str = None,
        stream: bool = False,
        reasoning: bool = False,
        max_workers: int = 10,
        **kwargs
    ):
        self.llms = llms
        self.model_name = model_name
        self.model_identifier = model_identifier
        self.data_dir = data_dir
        self.infer_type = infer_type
        self.reasoning = reasoning
        self.max_workers = max_workers
        self.stream = stream

        self.temperature = kwargs.get("temperature", 0.3)
        self.top_p = kwargs.get("top_p", 0.7)

        # set output dir based on model and infer type

        output_dir = os.path.join("outputs", infer_type, self.model_identifier)
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir

        # freeze data paths / prompt
        self.data_path_list = [
            os.path.abspath(os.path.join(self.data_dir, p)) for p in DATA[infer_type]
        ]
        self.prompt_path = os.path.abspath(PROMPT[infer_type])

        # preload
        self.prompt = self._load_prompt()
        self.dataset = self._load_dataset()

    # ----------------------------- I/O -----------------------------

    def _load_prompt(self):
        if not os.path.exists(self.prompt_path):
            raise FileNotFoundError(f"Prompt file {self.prompt_path} does not exist.")

        with open(self.prompt_path, "r") as f:
            prompt = f.read()

        logger.info(f"Loaded prompt for {self.infer_type} from {self.prompt_path}")
        return prompt

    def _load_dataset(self):
        """Load all datasets under this infer_type (multiple CSVs)."""
        data_records = []
        for path in self.data_path_list:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Data file `{path}` does not exist.")

            df = pd.read_csv(path)
            for item in df.columns:
                df[item] = df[item].apply(clean_row)
            df = df.astype(str)
            data_records.append(df.to_dict(orient="records"))
        return data_records

    # -------------------------- JSON parsing --------------------------

    @staticmethod
    def _parse_json(result: str):
        """Robust JSON extraction + repair."""

        # try extracting code fence
        try:
            if "```json" in result:
                json_str = result.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
        except Exception:
            pass

        # fallback to json_repair
        try:
            return json_repair.loads(result)
        except Exception as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.info(f"Raw response: {result}")
            return None

    # -------------------------- Prompt building --------------------------

    def construct_user_prompt(self, record: dict) -> str:
        keys = TARGET_KEY[self.infer_type]

        if self.infer_type == "query_equality":
            return (
                f"query1:\n{record[keys[0]]}\n\n"
                f"query2:\n{record[keys[1]]}"
            )
        else:
            return f"sql query:\n{record[keys[0]]}"

    # -------------------------- Core inference --------------------------

    def infer_single(self, record: dict, debug: bool = False):
        """Infer + parse JSON + update the record."""
        user_prompt = self.construct_user_prompt(record)

        reasoning, raw_result, _, _ = self.llms.chat(
            query = user_prompt,
            model_name = self.model_name,
            system_prompt = self.prompt,
            stream = self.stream,
            enable_thinking = self.reasoning,
            temperature = self.temperature,
            top_p = self.top_p,
        )

        parsed = self._parse_json(raw_result)
        if debug:
            logger.info(f"Input User prompt: {user_prompt}")
            if reasoning:
                logger.info(f"Model reasoning content: {reasoning}")
            logger.info(f"Model response result: {raw_result}")
        if not parsed or not isinstance(parsed, dict):
            logger.warning(f"Record failed JSON parse: {record}")
            parsed = {}

        for out_key in OUTPUT_KEY[self.infer_type]:
            record[out_key] = parsed.get(out_key)

        if self.reasoning:
            record["reasoning"] = reasoning

        return record

    # -------------------------- Batch inference --------------------------

    def infer_batch(self):
        """Return list-of-lists: one list per CSV."""
        all_results = []

        for idx, dataset in enumerate(self.dataset):
            with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
                results = list(
                    tqdm(pool.map(self.infer_single, dataset), total=len(dataset))
                )
            self.save_results(idx, results)
            all_results.append(results)

        return all_results

    def save_results(self, index: int, results: list[dict]):
        """Save results to CSV files."""
        df = pd.DataFrame(results)
        file_prefix_name = DATA[self.infer_type][index].split(".")[0]
        output_path = os.path.join(self.output_dir, f"{file_prefix_name}_results.csv")
        df.to_csv(output_path, index=False)
        logger.info(f"Saved results to {output_path}")

if __name__ == "__main__": 
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

    with open("utils/api_recording.json", "r") as f:
        apis = json.load(f)
    
    base_url = ""
    api_key = ""

    # batch test
    test_llm_server = LLMServer(
        base_url = base_url,
        api_key = api_key,    
        model_type = "doubao",
        reasoning_ability = False,
    )

    # reasoning_content, response, _, _ = test_llm_server.chat(
    #     query = "你好",
    #     model_name = "ep-20251205140315-zv8jn"
    # )

    # print(reasoning_content)
    # print(response)
    test_inference = Inference(
        llms = test_llm_server,
        model_name = "ep-20251117162016-2k2kx",
        model_identifier = "Doubao-Seed-1.6-251015",
        infer_type = InferType.SYNTAX_ERROR,
        reasoning = False,
    )

    results = test_inference.infer_batch()
