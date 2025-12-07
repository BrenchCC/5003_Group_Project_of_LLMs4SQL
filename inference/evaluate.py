import os
import sys
import math
import json
import logging
from typing import Dict, Any, List, Tuple

import pandas as pd

sys.path.append(os.getcwd())
from inference.infer_type import InferType

logger = logging.getLogger(__name__)

OUTPUT_DATA = {
    "syntax_error": ["syntax_error_join_results.csv", "syntax_error_sdss_results.csv", "syntax_error_sqlshare_results.csv"],
    "missing_token": ["missing_token_join_results.csv", "missing_token_sdss_results.csv", "missing_token_sqlshare_results.csv"],
    "query_performance": ["sdss_runtime_results.csv"],
    "query_equality": ["equi_join_mapping_results.csv", "equi_sdss_mapping_results.csv", "equi_sqlshare_mapping_results.csv"]
}


def clean_row(text):
    """Normalize individual CSV cell values to empty string when appropriate."""
    if isinstance(text, float) and math.isnan(text):
        return ""
    if text in ("N/A", "nan"):
        return ""
    return text


class EvaluateTool:
    """Evaluation helper that supports multiple infer types.

    This refactor extracts repeated logic into helper functions for clarity
    and easier maintenance.
    """

    def __init__(
        self,
        evaluate_data_dir: str,
        infer_type: InferType,
    ):
        self.evaluate_data_dir = os.path.abspath(evaluate_data_dir)
        self.infer_type = infer_type

        # load datasets for the given infer_type
        self.dataset = self._load_dataset()

    # --------------------- I/O helpers ---------------------
    def _load_dataset(self) -> Dict[str, pd.DataFrame]:
        """Load CSV files defined in OUTPUT_DATA for the current infer_type.

        Each file is assigned a human-friendly key: Join-Order, SDSS, SQLShare.
        """
        logger.info("Loading dataset for infer_type=%s from %s", self.infer_type, self.evaluate_data_dir)
        data_records: Dict[str, pd.DataFrame] = {}

        if self.infer_type.value not in OUTPUT_DATA:
            raise ValueError(f"Unknown infer_type `{self.infer_type.value}`.")

        for path in OUTPUT_DATA[self.infer_type.value]:
            if "join" in path:
                key = "Join-Order"
            elif "sdss" in path:
                key = "SDSS"
            elif "sqlshare" in path:
                key = "SQLShare"
            else:
                # If file name doesn't match known patterns we still attempt to load
                key = os.path.splitext(os.path.basename(path))[0]

            full_path = os.path.join(self.evaluate_data_dir, path)
            if not os.path.exists(full_path):
                logger.warning("Data file `%s` does not exist, skipping.", full_path)
                continue

            try:
                df = pd.read_csv(full_path, dtype=str)
            except Exception as e:
                logger.exception("Failed to read CSV `%s`: %s", full_path, e)
                continue

            # normalize cell values
            for col in df.columns:
                df[col] = df[col].apply(clean_row)

            df = df.fillna("").astype(str)
            data_records[key] = df
            logger.info("Loaded `%s` with %d rows and %d columns.", key, len(df), len(df.columns))

        if not data_records:
            logger.error("No datasets loaded for infer_type=%s", self.infer_type)
        return data_records

    def _results_save2json(self, data: Dict[str, Any]) -> None:
        """Save results JSON to the evaluate directory."""
        out_path = os.path.join(self.evaluate_data_dir, f"{self.infer_type.value}_metrics.json")
        try:
            with open(out_path, "w") as f:
                json.dump(data, f, indent=4)
            logger.info("Saved metrics JSON to %s", out_path)
        except Exception:
            logger.exception("Failed to save metrics JSON to %s", out_path)

    # --------------------- metric helpers ---------------------
    @staticmethod
    def _binary_metrics_from_series(y_true: pd.Series, y_pred: pd.Series) -> Dict[str, float]:
        """Compute precision, recall, f1 for binary labels (0/1 or YES/NO converted to 1/0)."""
        # allow series of strings 'YES'/'NO' or numeric 0/1
        def to_bin(s: pd.Series) -> pd.Series:
            return s.astype(str).str.upper().apply(lambda x: 1 if x == "YES" or x == "1" else 0)

        t = to_bin(y_true)
        p = to_bin(y_pred)

        tp = int(((t == 1) & (p == 1)).sum())
        fp = int(((t == 0) & (p == 1)).sum())
        fn = int(((t == 1) & (p == 0)).sum())

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        return {"precision": precision, "recall": recall, "f1": f1}

    @staticmethod
    def _multiclass_metrics_from_series(gt: pd.Series, pred: pd.Series, include_no: bool = True) -> Dict[str, float]:
        """Macro-average precision/recall/f1 for categorical labels.

        If include_no is False, empty or 'NO' labels can be filtered out upstream.
        """
        gt = gt.astype(str)
        pred = pred.astype(str)

        labels = sorted(set(gt.unique()) | set(pred.unique()))
        if not include_no:
            labels = [l for l in labels if l and l.upper() != "NO"]

        if not labels:
            return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

        per_p = []
        per_r = []
        per_f = []

        for c in labels:
            gt_c = (gt == c)
            pred_c = (pred == c)

            tp_c = int((gt_c & pred_c).sum())
            fp_c = int(((~gt_c) & pred_c).sum())
            fn_c = int((gt_c & ~pred_c).sum())

            p = tp_c / (tp_c + fp_c) if (tp_c + fp_c) else 0.0
            r = tp_c / (tp_c + fn_c) if (tp_c + fn_c) else 0.0
            f = 2 * p * r / (p + r) if (p + r) else 0.0

            per_p.append(p)
            per_r.append(r)
            per_f.append(f)

        return {"precision": float(sum(per_p) / len(labels)), "recall": float(sum(per_r) / len(labels)), "f1": float(sum(per_f) / len(labels))}

    @staticmethod
    def _regression_metrics_pos(gt_pos: pd.Series, pred_pos: pd.Series) -> Dict[str, float]:
        """Compute MAE and Hit-Rate for integer positions.

        Positions with invalid prediction or GT should be handled upstream (e.g., set to -1)
        """
        # coerce to numeric, invalid -> -1
        gt = pd.to_numeric(gt_pos, errors='coerce').fillna(-1).astype(int)
        pred = pd.to_numeric(pred_pos, errors='coerce').fillna(-1).astype(int)

        valid_mask = gt >= 0
        if not valid_mask.any():
            return {"mae": 0.0, "hr": 0.0}

        abs_err = (gt[valid_mask] - pred[valid_mask]).abs()
        mae = float(abs_err.mean())
        hr = float((gt[valid_mask] == pred[valid_mask]).sum() / valid_mask.sum())
        return {"mae": mae, "hr": hr}

    # --------------------- public evaluation API ---------------------
    def evaluate(self) -> Dict[str, Any]:
        """Dispatch to concrete evaluators based on infer_type."""
        logger.info("Starting evaluation for infer_type=%s", self.infer_type)
        if self.infer_type == InferType.SYNTAX_ERROR:
            return self.evaluate_syntax_error()
        if self.infer_type == InferType.QUERY_EQUALITY:
            return self.evaluate_query_equality()
        if self.infer_type == InferType.MISSING_TOKEN:
            return self.evaluate_missing_token()
        if self.infer_type == InferType.QUERY_PERFORMANCE:
            return self.evaluate_query_performance()

        logger.error("Unsupported infer_type: %s", self.infer_type)
        return {}

    def evaluate_syntax_error(self) -> Dict[str, Any]:
        """Evaluate syntax error detection and classification.

        Binary task: detect syntax error (YES/NO).
        Multi-class task: error category/type macro-F1.
        """
        if self.infer_type != InferType.SYNTAX_ERROR:
            logger.info("Now infer_type is %s, not syntax error, skip.", self.infer_type)
            return {}

        results: Dict[str, Any] = {}

        for ds_name, df in self.dataset.items():
            df = df.copy()
            # drop invalid rows where Modified_Statement is empty
            df = df[df.get("Modified_Statement", "") != ""]
            if df.empty:
                logger.warning("%s dataset is empty after cleaning.", ds_name)
                continue

            # normalize empty predictions
            df["syntax_error"] = df.get("syntax_error", "").replace("", "NO")
            df["syntax_type"] = df.get("syntax_type", "").replace("", "")

            # binary evaluation
            y_true = df["Original"].apply(lambda x: "YES" if str(x).upper() == "YES" else "NO")
            y_pred = df["syntax_error"].apply(lambda x: "YES" if str(x).upper() == "YES" else "NO")
            binary_metrics = self._binary_metrics_from_series(y_true, y_pred)

            # multi-class: only rows with ground truth Error_Category
            df_multi = df[df.get("Error_Category", "") != ""]
            if df_multi.empty:
                logger.warning("%s has no multi-class ground truth.", ds_name)
                multi_metrics = {"precision": 0.0, "recall": 0.0, "f1": 0.0}
            else:
                multi_metrics = self._multiclass_metrics_from_series(df_multi["Error_Category"], df_multi["syntax_type"], include_no=False)

            results[ds_name] = {"syntax_error": binary_metrics, "syntax_error_type": multi_metrics}
            logger.info("Computed syntax error metrics for %s: %s", ds_name, results[ds_name])

        self._results_save2json(results)
        return results

    def evaluate_query_equality(self) -> Dict[str, Any]:
        """Evaluate query equivalence detection and type classification."""
        if self.infer_type != InferType.QUERY_EQUALITY:
            logger.info("Now infer_type is %s, not query equality, skip.", self.infer_type)
            return {}

        results: Dict[str, Any] = {}

        for ds_name, df in self.dataset.items():
            df = df.copy()
            # drop invalid rows
            df = df[df.get("Equivalent_Queries", "") != ""]
            if df.empty:
                logger.warning("%s dataset is empty after cleaning.", ds_name)
                continue

            # normalize
            df["query_equility"] = df.get("query_equility", "").replace("", "NO")
            df["Original"] = df.get("Original", "").replace("", "NO")

            df["query_equility_type"] = df.get("query_equility_type", "").replace("", "NO")
            df["Modification_Method"] = df.get("Modification_Method", "").replace("", "NO")

            # binary
            binary_metrics = self._binary_metrics_from_series(df["Original"], df["query_equility"])

            # multi-class with 'NO' included
            multi_metrics = self._multiclass_metrics_from_series(df["Modification_Method"], df["query_equility_type"], include_no=True)

            results[ds_name] = {"query_equality": binary_metrics, "query_equality_type": multi_metrics}
            logger.info("Computed query equality metrics for %s: %s", ds_name, results[ds_name])

        self._results_save2json(results)
        return results

    def evaluate_missing_token(self) -> Dict[str, Any]:
        """Evaluate missing token detection (binary), type (multi-class) and location (regression).

        The implementation keeps behavior compatible with the previous version.
        """
        if self.infer_type != InferType.MISSING_TOKEN:
            logger.info("Now infer_type is %s, not missing token, skip.", self.infer_type)
            return {}

        results: Dict[str, Any] = {}

        for ds_name, df in self.dataset.items():
            df = df.copy()
            # drop invalid rows: need both SQL_Statement and Modified_Statements
            df = df[(df.get("SQL_Statement", "") != "") & (df.get("Modified_Statements", "") != "")]
            if df.empty:
                logger.warning("%s dataset is empty after cleaning.", ds_name)
                continue

            # --- Build GT binary: presence of any Missing_word* column ---
            def has_missing_word(row: pd.Series) -> str:
                for col in df.columns:
                    if col.startswith("Missing_word") and str(row[col]) != "":
                        return "YES"
                return "NO"

            df["gt_binary"] = df.apply(has_missing_word, axis=1)
            df["missing_token"] = df.get("missing_token", "").replace("", "NO")

            # binary metrics
            binary_metrics = self._binary_metrics_from_series(df["gt_binary"], df["missing_token"])

            # multi-class on positive rows
            pos_df = df[df["gt_binary"] == "YES"].copy()
            if pos_df.empty:
                multi_metrics = {"precision": 0.0, "recall": 0.0, "f1": 0.0}
                regression_metrics = {"mae": 0.0, "hr": 0.0}
            else:
                def get_missing_type(row: pd.Series) -> str:
                    for col in df.columns:
                        if col.startswith("Missing_type") and str(row[col]) != "":
                            return row[col]
                    return ""

                pos_df["gt_type"] = pos_df.apply(get_missing_type, axis=1)
                pos_df["missing_token_type"] = pos_df.get("missing_token_type", "").replace("", "NO_TYPE")

                labels = sorted(set(pos_df["gt_type"].unique()) | set(pos_df["missing_token_type"].unique()))
                multi_metrics = self._multiclass_metrics_from_series(pos_df["gt_type"], pos_df["missing_token_type"], include_no=False)

                # regression: find position columns
                def get_missing_pos(row: pd.Series) -> int:
                    for col in df.columns:
                        if col.startswith("Missing_position") and str(row[col]) != "":
                            try:
                                return int(row[col])
                            except Exception:
                                return -1
                    return -1

                pos_df["gt_pos"] = pos_df.apply(get_missing_pos, axis=1)

                def parse_pred_pos(v: Any) -> int:
                    if v is None or str(v).strip() == "":
                        return -1
                    try:
                        return int(v)
                    except Exception:
                        return -1

                pos_df["pred_pos"] = pos_df.get("missing_token_location", "").apply(parse_pred_pos)

                regression_metrics = self._regression_metrics_pos(pos_df["gt_pos"], pos_df["pred_pos"])

            results[ds_name] = {
                "missing_token": binary_metrics,
                "missing_token_type": multi_metrics,
                "missing_token_location": regression_metrics,
            }

            logger.info("Computed missing token metrics for %s: %s", ds_name, results[ds_name])

        self._results_save2json(results)
        return results

    def evaluate_query_performance(self) -> Dict[str, Any]:
        """Evaluate query performance prediction (binary YES/NO).

        Only SDSS dataset is considered in previous code; keep same logic.
        """
        if self.infer_type != InferType.QUERY_PERFORMANCE:
            logger.info("Now infer_type is %s, not query performance, skip.", self.infer_type)
            return {}

        df = self.dataset.get("SDSS", None)
        if df is None:
            logger.error("No SDSS dataset found for query performance evaluation.")
            return {}

        df = df[(df.get("SQL_Statement", "").astype(str).str.strip() != "")].copy()

        gt = df.get("Original", "").fillna("NO").replace({"": "NO"}).astype(str).str.upper()
        pred = df.get("performance_pred", "").fillna("NO").replace({"": "NO"}).astype(str).str.upper()

        metrics = self._binary_metrics_from_series(gt, pred)
        results = {"SDSS": {"query_performance": metrics}}
        logger.info("Computed query performance metrics: %s", results)

        self._results_save2json(results)
        return results


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    test_evaluate_tool = EvaluateTool(
        evaluate_data_dir = "outputs/query_performance/Doubao-Seed-1.6-251015",
        infer_type = InferType.QUERY_PERFORMANCE
    )
    test_evaluate_tool.evaluate()
