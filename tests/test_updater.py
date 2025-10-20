import os
import pytest
from auto_reqs.updater import load_requirements, write_requirements, determine_changes


class TestLoadRequirements:
    def test_loads_existing_requirements(self, tmp_path):
        """Should correctly parse a requirements.txt file."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text(
            "# comment\n"
            "requests==2.31.0\n"
            "Flask\n"
            "\n"
            "numpy==1.26.0\n"
        )

        result = load_requirements(req_file)
        assert result == {
            "requests": "2.31.0",
            "flask": None,
            "numpy": "1.26.0",
        }

    def test_missing_file_returns_empty_dict(self, tmp_path):
        """Should return empty dict if file doesn't exist."""
        missing_path = tmp_path / "missing.txt"
        assert load_requirements(missing_path) == {}


class TestWriteRequirements:
    def test_writes_sorted_requirements_file(self, tmp_path):
        """Should write out a sorted and formatted requirements.txt file."""
        path = tmp_path / "requirements.txt"
        reqs = {"flask": "2.3.0", "requests": "2.31.0", "numpy": None}

        write_requirements(reqs, path)
        content = path.read_text().strip().splitlines()

        assert content[0].startswith("# Automatically maintained")
        assert content[1:] == ["flask==2.3.0", "numpy", "requests==2.31.0"]


class TestDetermineChanges:
    def test_detects_missing_and_unused_packages(self, monkeypatch, tmp_path):
        """Should detect new imports and remove unused ones accurately."""
        # Treat os/sys as stdlib and my_local as local module
        monkeypatch.setattr("auto_reqs.classifier.is_stdlib", lambda n: n in {"os", "sys"})
        monkeypatch.setattr("auto_reqs.classifier.is_local_module", lambda n, p: n == "my_local")

        # Patch normalization & resolver as used inside updater
        monkeypatch.setattr("auto_reqs.updater.normalize_pkg_name", lambda n: n.lower().replace("_", "-"))
        monkeypatch.setattr("auto_reqs.updater.resolve_import_to_pkg", lambda n: n.lower().replace("_", "-"))

        installed = {"requests": "2.31.0", "flask": "3.0.0"}
        resolver = lambda pkg: {"numpy": "1.26.0"}.get(pkg)

        requirements = {"flask": "3.0.0", "oldpkg": "0.9.0"}
        imports = {"requests", "os", "my_local"}

        missing, unused = determine_changes(imports, installed, requirements, resolver, str(tmp_path))

        # ---- Assertions ----
        assert ("requests", "2.31.0") in missing, f"Expected requests in missing, got {missing}"
        assert "oldpkg" in unused
        assert "requests" in requirements
        assert "oldpkg" not in requirements

    def test_warns_when_version_missing(self, monkeypatch, capsys, tmp_path):
        """Should warn and skip if resolver and installed cannot find version."""
        monkeypatch.setattr("auto_reqs.classifier.is_stdlib", lambda n: False)
        monkeypatch.setattr("auto_reqs.classifier.is_local_module", lambda n, p: False)
        monkeypatch.setattr("auto_reqs.resolver.resolve_import_to_pkg", lambda n: n)
        monkeypatch.setattr("auto_reqs.utils.normalize_pkg_name", lambda n: n.lower())

        imports = {"unknownlib"}
        installed = {}
        resolver = lambda pkg: None
        requirements = {}

        missing, unused = determine_changes(imports, installed, requirements, resolver, str(tmp_path))
        out = capsys.readouterr().out

        assert "Warning: Could not find version for 'unknownlib'" in out
        assert missing == []
        assert unused == []

    def test_normalizes_import_names(self, monkeypatch, tmp_path):
        """Should normalize all names before comparison."""
        monkeypatch.setattr("auto_reqs.classifier.is_stdlib", lambda n: False)
        monkeypatch.setattr("auto_reqs.classifier.is_local_module", lambda n, p: False)
        monkeypatch.setattr("auto_reqs.resolver.resolve_import_to_pkg", lambda n: n.lower())
        monkeypatch.setattr("auto_reqs.utils.normalize_pkg_name", lambda n: n.lower())

        installed = {"requests": "2.31.0"}
        resolver = lambda pkg: "9.9.9"
        requirements = {"numpy": "1.26.0"}
        imports = {"Requests", "NumPy"}

        missing, unused = determine_changes(imports, installed, requirements, resolver, str(tmp_path))

        assert ("requests", "2.31.0") in missing
        assert "numpy" in requirements
        assert "requests" in requirements
        assert unused == []
