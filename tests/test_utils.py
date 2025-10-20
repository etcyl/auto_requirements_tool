import os
import sys
import pytest
from auto_reqs.utils import validate_repo_path, normalize_pkg_name


class TestNormalizePkgName:
    def test_normal_case(self):
        assert normalize_pkg_name("Requests") == "requests"
        assert normalize_pkg_name("stdlib_list") == "stdlib-list"
        assert normalize_pkg_name(" TensorFlow ") == "tensorflow"

    def test_empty_and_none(self):
        assert normalize_pkg_name("") == ""
        assert normalize_pkg_name(None) == ""


class TestValidateRepoPath:
    def test_path_does_not_exist(self, monkeypatch, tmp_path):
        fake_path = tmp_path / "nonexistent"
        monkeypatch.setattr(os.path, "exists", lambda p: False)

        # Patch sys.exit so it doesn't terminate the test runner
        called = {"exit_code": None}
        def fake_exit(code):
            called["exit_code"] = code
            raise SystemExit(code)
        monkeypatch.setattr(sys, "exit", fake_exit)

        with pytest.raises(SystemExit):
            validate_repo_path(str(fake_path))
        assert called["exit_code"] == 1

    def test_no_python_files_found(self, monkeypatch, tmp_path):
        monkeypatch.setattr(os.path, "exists", lambda p: True)
        # Simulate no .py files found in os.walk
        monkeypatch.setattr(os, "walk", lambda p: [(".", [], ["README.md", "data.txt"])])

        called = {"exit_code": None}
        def fake_exit(code):
            called["exit_code"] = code
            raise SystemExit(code)
        monkeypatch.setattr(sys, "exit", fake_exit)

        with pytest.raises(SystemExit):
            validate_repo_path(str(tmp_path))
        assert called["exit_code"] == 0

    def test_valid_python_files_found(self, monkeypatch, tmp_path):
        monkeypatch.setattr(os.path, "exists", lambda p: True)
        pyfile = tmp_path / "main.py"
        pyfile.write_text("print('hello')")
        monkeypatch.setattr(os, "walk", lambda p: [(".", [], ["main.py"])])

        result = validate_repo_path(str(tmp_path))
        assert result == os.path.abspath(tmp_path)

