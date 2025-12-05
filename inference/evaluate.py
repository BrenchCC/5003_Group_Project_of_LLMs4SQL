import os
import json
import logging
import pandas as pd

import json_repair
from inference.infer_type import InferType

logger = logging.getLogger("Evaluate")

# TODO: Update evaluate tools for different kinds of problem
class EvaluateTool:
    def __init__(
        self,
        data_dir: str,
        infer_type: InferType,
    ):
        self.data_dir = data_dir
        self.infer_type = infer_type    