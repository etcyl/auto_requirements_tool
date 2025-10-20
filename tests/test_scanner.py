import os
import pytest
from auto_reqs.scanner import extract_imports_from_file, scan_project_for_imports, EXCLUDE_DIRS_DEFAULT


class TestExtractImportsFromFile:
    def test_simple_imports(self, tmp_path):
        """Should correctly extract import names from basic imports."""
        test_file = tmp_path / "simple.py"
        test_file.write_text(
            "import os\n"
            "import sys\n"
            "from collections import defaultdict\n"
            "from math import sqrt\n"
        )

        imports = extract_imports_from_file(test_file)
        assert imports == {"os", "sys", "collections", "math"}

    def test_syntax_error_file(self, tmp_path):
        """Should safely skip files with syntax errors and return an empty set."""
        test_file = tmp_path / "broken.py"
        test_file.write_text("def broken_func(: pass")  # invalid Python

        imports = extract_imports_from_file(test_file)
        assert imports == set()  # Must handle gracefully

    def test_ignores_nested_imports_comments_and_strings(self, tmp_path):
        """Should ignore imports inside strings or comments."""
        test_file = tmp_path / "weird.py"
        test_file.write_text(
            "# import fake_module\n"
            "some_text = 'import os'\n"
            "def func():\n"
            "    pass\n"
        )

        imports = extract_imports_from_file(test_file)
        assert imports == set()


class TestScanProjectForImports:
    def test_scans_all_python_files(self, tmp_path):
        """Should detect imports across multiple files in directory tree."""
        project_dir = tmp_path / "project"
        sub_dir = project_dir / "sub"
        sub_dir.mkdir(parents=True)

        (project_dir / "main.py").write_text("import os\nfrom sys import argv\n")
        (sub_dir / "helper.py").write_text("import json\n")

        imports = scan_project_for_imports(project_dir)
        assert "os" in imports
        assert "sys" in imports
        assert "json" in imports
        assert "collections" not in imports

    def test_respects_exclude_dirs(self, tmp_path):
        """Should skip scanning directories listed in exclude_dirs."""
        project_dir = tmp_path / "project"
        excluded = project_dir / "venv"
        included = project_dir / "src"
        excluded.mkdir(parents=True)
        included.mkdir(parents=True)

        (excluded / "skipme.py").write_text("import should_not_see\n")
        (included / "keepme.py").write_text("import visible\n")

        imports = scan_project_for_imports(project_dir, exclude_dirs={"venv"})
        assert "visible" in imports
        assert "should_not_see" not in imports

    def test_empty_project_returns_empty_set(self, tmp_path):
        """Should handle empty directories without error."""
        project_dir = tmp_path / "empty_project"
        project_dir.mkdir()

        imports = scan_project_for_imports(project_dir)
        assert imports == set()

    def test_exclude_dirs_default_constant_is_reasonable(self):
        """Sanity-check that EXCLUDE_DIRS_DEFAULT includes key standard dirs."""
        expected = {"__pycache__", ".git", "venv"}
        assert expected.issubset(EXCLUDE_DIRS_DEFAULT)
