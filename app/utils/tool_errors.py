class ToolError(Exception):
    """Base class for controlled tool errors."""


class ToolTimeoutError(ToolError):
    """The tool operation timed out."""


class ToolRateLimitError(ToolError):
    """The external service rate-limited us."""


class ToolAuthenticationError(ToolError):
    """Authentication failed."""


class ToolPermissionError(ToolError):
    """The operation is not permitted."""


class ToolInvalidArgumentError(ToolError):
    """The tool received invalid arguments."""