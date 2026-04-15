"""Energy price shock impact on UK living standards analysis using PolicyEngine."""

from .config import (
    YEAR,
    CURRENT_ENERGY_CAP,
    SCENARIOS,
)


def run_full_pipeline(*args, **kwargs):
    from .pipeline import run_full_pipeline as _run_full_pipeline

    return _run_full_pipeline(*args, **kwargs)

__all__ = [
    "YEAR",
    "CURRENT_ENERGY_CAP",
    "SCENARIOS",
    "run_full_pipeline",
]
