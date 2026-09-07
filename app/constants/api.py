"""Common API response definitions."""

from typing import Any

NOT_FOUND_RESPONSE: dict[int, dict[str, Any]] = {404: {"description": "Not found"}}
