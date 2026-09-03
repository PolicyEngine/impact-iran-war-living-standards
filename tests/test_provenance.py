"""The provenance block, and the staleness signal CI relies on."""

from iran_impact import provenance


def test_source_hashes_cover_the_calculation_and_the_environment():
    """A dependency change can move a result without touching a calculation
    file, so the environment definition is hashed too."""
    hashes = provenance.source_hashes()
    assert set(hashes) == set(provenance.HASHED_SOURCES) | set(
        provenance.HASHED_REPO_FILES
    )
    assert all(value and len(value) == 64 for value in hashes.values())


def test_the_lockfile_is_part_of_the_staleness_signal():
    assert "requirements.lock" in provenance.source_hashes()
    assert "pyproject.toml" in provenance.source_hashes()


def test_build_provenance_records_packages_and_hashes():
    block = provenance.build_provenance()
    assert block["source_hashes"] == provenance.source_hashes()
    assert set(block["packages"]) == set(provenance.TRACKED_PACKAGES)
    assert block["packages"]["numpy"]
    assert set(provenance.VOLATILE_FIELDS) <= set(block)


def test_build_provenance_without_a_bundle_reports_no_bundle():
    """Absent a simulation the model/data fields must be empty, not guessed."""
    assert provenance.build_provenance(bundle=None)["release_bundle"] is None


def test_build_provenance_keeps_only_portable_bundle_fields():
    bundle = {
        "bundle_id": "uk-5.3.0",
        "certified_data_build_id": "test-data-build",
        # A machine-local cache path must not reach the output.
        "runtime_dataset_source": "/home/someone/.cache/x.h5",
    }
    recorded = provenance.build_provenance(bundle=bundle)["release_bundle"]
    assert recorded["bundle_id"] == "uk-5.3.0"
    assert recorded["certified_data_build_id"] == "test-data-build"
    assert "runtime_dataset_source" not in recorded


def test_strip_volatile_removes_only_run_to_run_fields():
    results = {"year": 2027, "provenance": provenance.build_provenance()}
    stripped = provenance.strip_volatile(results)
    for field in provenance.VOLATILE_FIELDS:
        assert field not in stripped["provenance"]
    assert stripped["provenance"]["source_hashes"]
    assert stripped["year"] == 2027
    # The original must not be mutated.
    assert "generated_at" in results["provenance"]


def test_strip_volatile_makes_two_runs_comparable():
    first = {"provenance": provenance.build_provenance()}
    second = {"provenance": provenance.build_provenance()}
    assert provenance.strip_volatile(first) == provenance.strip_volatile(second)
