from app.utils.tool_errors import (
    ToolAuthenticationError,
    ToolInvalidArgumentError,
    ToolPermissionError,
    ToolRateLimitError,
    ToolTimeoutError,
)


def classify_error(error: Exception):

    error_name = type(error).__name__

    if "Timeout" in error_name:

        return {
            "error_type": "timeout",
            "retryable": True,
        }

    if "RateLimit" in error_name:

        return {
            "error_type": "rate_limit",
            "retryable": True,
        }

    if isinstance(
        error,
        ToolAuthenticationError,
    ):

        return {
            "error_type": "authentication",
            "retryable": False,
        }

    if isinstance(
        error,
        ToolPermissionError,
    ):

        return {
            "error_type": "permission_denied",
            "retryable": False,
        }

    if isinstance(
        error,
        ToolInvalidArgumentError,
    ):

        return {
            "error_type": "invalid_argument",
            "retryable": False,
        }

    return {
        "error_type": "unknown",
        "retryable": False,
    }