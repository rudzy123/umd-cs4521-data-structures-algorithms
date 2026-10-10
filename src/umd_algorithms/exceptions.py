"""Algorithm-specific failures that callers can handle separately from bad arguments."""


class CycleError(ValueError):
    """A directed graph contains a cycle, so no topological order exists."""
