from enum import Enum

class InferType(str, Enum):
    SYNTAX_ERROR = "syntax_error"
    MISSING_TOKEN = "missing_token"
    QUERY_PERFORMANCE = "query_performance"
    QUERY_EQUALITY = "query_equality"

OUTPUT_KEY = {
    "syntax_error": ["syntax_error", "syntax_type"],
    "missing_token": ["syntax_error", "missing_token", "missing_token_type", "missing_token_location"],
    "query_performance": ["performance_pred"],
    "query_equality": ["query_equility", "query_equility_type"]
}
