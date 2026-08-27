"""In-memory display state for dashboard status reporting."""

_mode = None


def set_mode(mode):
    global _mode
    _mode = mode


def get_mode(fallback):
    return _mode or fallback
