from threading import Thread
from typing import Any, Callable


def getattr_or_default(_o: Any, __name: str, __default: Any = None, /) -> Any:
    if hasattr(_o, __name):
        return getattr(_o, __name)
    return __default


def execute_in_background(function: Callable[..., Any]):
    def start_thread(*args: Any, **kwargs: Any):
        thread = Thread(target=function, args=args, kwargs=kwargs)
        thread.start()

    return start_thread
