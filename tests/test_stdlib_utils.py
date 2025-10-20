import sys
import sysconfig
import pytest
from auto_reqs.stdlib_utils import is_stdlib_module, LEGACY_STDLIB_NAMES


class TestIsStdlibModule:
    def test_builtin_modules(self):
        """Should return True for core built-in and stdlib modules."""
        assert is_stdlib_module("sys") is True
        assert is_stdlib_module("os") is True
        assert is_stdlib_module("math") is True
        assert is_stdlib_module("time") is True

    def test_private_and_empty_names(self):
        """Should treat empty strings and names starting with '_' as stdlib."""
        assert is_stdlib_module("") is True
        assert is_stdlib_module("_collections") is True
        assert is_stdlib_module("_random") is True

    def test_legacy_stdlib_aliases(self):
        """Should correctly identify legacy stdlib names as True."""
        for legacy_name in ["Queue", "StringIO", "cPickle", "httplib"]:
            assert legacy_name in LEGACY_STDLIB_NAMES
            assert is_stdlib_module(legacy_name) is True

    def test_non_stdlib_third_party(self):
        """Should return False for third-party modules in site-packages."""
        # Common third-party libs that should always be False
        for pkg in ["requests", "flask", "pytest"]:
            result = is_stdlib_module(pkg)
            assert result is False, f"{pkg} should not be detected as stdlib"

    def test_nonexistent_module_returns_false(self):
        """Should safely return False for nonexistent or invalid modules."""
        assert is_stdlib_module("definitely_not_a_real_module_12345") is False

    def test_simulated_import_error(self, monkeypatch):
        """Should safely handle ImportError from importlib.util.find_spec()."""
        def raise_importerror(name):
            raise ImportError("Simulated import failure")

        monkeypatch.setattr("importlib.util.find_spec", raise_importerror)
        assert is_stdlib_module("fake_module") is False

    def test_spec_origin_checking(self, monkeypatch):
        """Should distinguish between stdlib and site-packages origins."""
        class DummySpec:
            def __init__(self, origin):
                self.origin = origin

        # Dynamically get actual stdlib path for this environment
        stdlib_path = sysconfig.get_paths().get("stdlib", "")
        if not stdlib_path:
            pytest.skip("Cannot determine stdlib path dynamically.")

        # Build examples using correct environment paths
        stdlib_example = f"{stdlib_path}/os.py"
        sitepkg_example = f"{stdlib_path}/../site-packages/requests/__init__.py"
        windows_sitepkg_example = f"{stdlib_path}\\..\\site-packages\\requests\\__init__.py"

        # Pretend stdlib path → should return True
        monkeypatch.setattr("importlib.util.find_spec", lambda n: DummySpec(stdlib_example))
        assert is_stdlib_module("fake_stdlib_like") is True

        # Pretend Linux/macOS site-packages → should return False
        monkeypatch.setattr("importlib.util.find_spec", lambda n: DummySpec(sitepkg_example))
        assert is_stdlib_module("fake_external") is False

        # Pretend Windows site-packages → should return False
        monkeypatch.setattr("importlib.util.find_spec", lambda n: DummySpec(windows_sitepkg_example))
        assert is_stdlib_module("fake_external_windows") is False

    def test_invalid_spec_origin(self, monkeypatch):
        """Should return False if spec exists but has no origin or is invalid."""
        class DummySpec:
            origin = None

        monkeypatch.setattr("importlib.util.find_spec", lambda n: DummySpec())
        assert is_stdlib_module("fake_no_origin") is False
