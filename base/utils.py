from typing import Any


def getattr_or_default(_o: Any, __name: str, __default: Any = None, /) -> Any:
    if hasattr(_o, __name):
        return getattr(_o, __name)
    return __default
