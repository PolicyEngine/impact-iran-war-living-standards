"""Provenance for a pipeline run.

Records what produced a results file: the repository revision, the
policyengine.py release bundle that certifies the model and data, the
versions of every package that affects the numbers, and hashes of the
source files that define the calculation.

The bundle is policyengine.py's own certification record — it is the
authority on which policyengine-uk version and which data build were
used, so this module reads it rather than inspecting policyengine-uk
directly.
"""

import hashlib
import importlib.metadata
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Packages whose version can move a result. policyengine-uk is included
# because the bundle certifies it, not because the project pins it.
TRACKED_PACKAGES = [
    "policyengine",
    "policyengine-uk",
    "numpy",
    "pandas",
    "microdf-python",
]

# Source files that define the calculation. A change to any of them makes a
# committed results file stale; CI compares these hashes to the working tree.
HASHED_SOURCES = ["config.py", "pipeline.py", "provenance.py"]

# Bundle fields worth recording. `runtime_dataset_source` is deliberately
# excluded: it is a machine-local cache path, so including it would make the
# output differ between machines that ran identical models on identical data.
BUNDLE_FIELDS = [
    "bundle_id",
    "policyengine_version",
    "model_package",
    "model_version",
    "default_dataset",
    "runtime_dataset",
    "runtime_dataset_uri",
    "certified_data_build_id",
    "certified_data_artifact_sha256",
    "data_build_model_version",
    "compatibility_basis",
    "certified_by",
]

# Fields that change on every run even when code, model and data are
# identical. The regression test drops them before comparing.
VOLATILE_FIELDS = ["generated_at", "git_revision", "git_dirty"]


def _git(*args):
    """Run a git command in the repository, returning None outside a checkout."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=Path(__file__).resolve().parent,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip()


def _package_versions():
    versions = {}
    for name in TRACKED_PACKAGES:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return versions


def source_hashes():
    """SHA-256 of each source file that defines the calculation."""
    here = Path(__file__).resolve().parent
    hashes = {}
    for name in HASHED_SOURCES:
        path = here / name
        hashes[name] = (
            hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
        )
    return hashes


def build_provenance(bundle=None, input_hashes=None):
    """Assemble the provenance block for a results file.

    Parameters
    ----------
    bundle : dict or None
        ``sim.policyengine_bundle`` from a managed simulation. None when the
        pipeline ran without a simulation (unit tests), in which case the
        model and data fields are recorded as unavailable rather than guessed.
    input_hashes : dict or None
        Hashes of committed input data files, keyed by repository path.
    """
    status = _git("status", "--porcelain")
    provenance = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_revision": _git("rev-parse", "HEAD"),
        "git_dirty": bool(status) if status is not None else None,
        "packages": _package_versions(),
        "source_hashes": source_hashes(),
        "input_hashes": dict(input_hashes or {}),
        "release_bundle": (
            {field: bundle.get(field) for field in BUNDLE_FIELDS}
            if bundle
            else None
        ),
    }
    return provenance


def strip_volatile(results):
    """Copy of `results` with run-to-run varying provenance fields removed.

    Two runs of the same code against the same certified data build produce
    outputs that are identical under this transform. The regression test and
    the CI staleness check both compare stripped outputs.
    """
    import copy

    stripped = copy.deepcopy(results)
    provenance = stripped.get("provenance")
    if isinstance(provenance, dict):
        for field in VOLATILE_FIELDS:
            provenance.pop(field, None)
    return stripped
