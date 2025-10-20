import pytest
import importlib.metadata
import requests
from auto_reqs.resolver import (
    get_installed_distributions,
    resolve_import_to_pkg,
    get_latest_version_from_pypi,
)
from auto_reqs.utils import normalize_pkg_name


class TestGetInstalledDistributions:
    def test_collects_distributions(self, monkeypatch):
        """Should return installed distributions with normalized names and versions."""

        class DummyDist:
            def __init__(self, name, version):
                self.metadata = {"Name": name}
                self.version = version

        dummy_dists = [
            DummyDist("Requests", "2.31.0"),
            DummyDist("NumPy", "1.26.2"),
        ]

        monkeypatch.setattr(importlib.metadata, "distributions", lambda: dummy_dists)

        result = get_installed_distributions()
        assert result == {"requests": "2.31.0", "numpy": "1.26.2"}

    def test_skips_invalid_distributions(self, monkeypatch):
        """Should gracefully skip broken dist metadata."""

        class BrokenDist:
            def __init__(self):
                self.metadata = {}  # Missing 'Name'
                self.version = "1.0.0"

        monkeypatch.setattr(importlib.metadata, "distributions", lambda: [BrokenDist()])
        result = get_installed_distributions()
        assert result == {}  # Should skip invalid


class TestResolveImportToPkg:
    def test_resolves_from_local_mapping(self, monkeypatch):
        """Should resolve package name using importlib mapping if available."""
        fake_mapping = {"requests": ["requests"]}
        monkeypatch.setattr(importlib.metadata, "packages_distributions", lambda: fake_mapping)

        result = resolve_import_to_pkg("requests")
        assert result == "requests"

    def test_fallback_checks_pypi_success(self, monkeypatch):
        """Should confirm package via PyPI if not in local mapping."""
        monkeypatch.setattr(importlib.metadata, "packages_distributions", lambda: {})
        class DummyResponse:
            status_code = 200
        monkeypatch.setattr(requests, "get", lambda *a, **kw: DummyResponse())

        result = resolve_import_to_pkg("Flask")
        assert result == "flask"

    def test_fallback_checks_pypi_failure(self, monkeypatch):
        """Should still return normalized name even if PyPI lookup fails."""
        monkeypatch.setattr(importlib.metadata, "packages_distributions", lambda: {})
        class DummyResponse:
            status_code = 404
        monkeypatch.setattr(requests, "get", lambda *a, **kw: DummyResponse())

        result = resolve_import_to_pkg("nonexistentpkg")
        assert result == "nonexistentpkg"


class TestGetLatestVersionFromPypi:
    def test_fetches_latest_version(self, monkeypatch):
        """Should return version string when PyPI responds successfully."""
        def fake_get(url, timeout):
            class DummyResp:
                status_code = 200
                def json(self):
                    return {"info": {"version": "9.9.9"}}
            return DummyResp()
        monkeypatch.setattr(requests, "get", fake_get)

        version = get_latest_version_from_pypi("pytest")
        assert version == "9.9.9"

    def test_returns_none_on_failure(self, monkeypatch):
        """Should return None if PyPI request fails."""
        def fake_get(url, timeout):
            class DummyResp:
                status_code = 404
            return DummyResp()
        monkeypatch.setattr(requests, "get", fake_get)

        version = get_latest_version_from_pypi("doesnotexist")
        assert version is None
