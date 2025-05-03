import threading


class CatchThreadingException:
    """
    https://docs.python.org/3/library/test.html#test.support.catch_threading_exception
    Context manager catching threading.Thread exception using
    threading.excepthook.

    Attributes set when an exception is catched:

    * exc_type
    * exc_value
    * exc_traceback
    * thread

    See threading.excepthook() documentation for these attributes.

    These attributes are deleted at the context manager exit.

    Usage:

        with base.tests.utils.CatchThreadingException() as cm:
            # code spawning a thread which raises an exception
            ...

            # check the thread exception, use cm attributes:
            # exc_type, exc_value, exc_traceback, thread
            ...

        # exc_type, exc_value, exc_traceback, thread attributes of cm no longer
        # exists at this point
        # (to avoid reference cycles)
    """

    def __init__(self):
        self.exc_type = None
        self.exc_value = None
        self.exc_traceback = None
        self.thread = None
        self._old_hook = None

    def _hook(self, args):
        self.exc_type = args.exc_type
        self.exc_value = args.exc_value
        self.exc_traceback = args.exc_traceback
        self.thread = args.thread

    def __enter__(self):
        self._old_hook = threading.excepthook
        threading.excepthook = self._hook
        return self

    def __exit__(self, *exc_info):
        threading.excepthook = self._old_hook
        del self.exc_type
        del self.exc_value
        del self.exc_traceback
        del self.thread
