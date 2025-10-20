import os
import sys

def validate_repo_path(repo_path):
    """Ensure target directory exists and contains .py files."""
    if not os.path.exists(repo_path):
        print(f"Error: Path '{repo_path}' does not exist.")
        sys.exit(1)
    if not any(fname.endswith(".py") for _, _, files in os.walk(repo_path) for fname in files):
        print("No Python files found in target directory.")
        sys.exit(0)
    return os.path.abspath(repo_path)


def normalize_pkg_name(name: str) -> str:
    """Normalize package name for consistent comparison (PyPI standard)."""
    if not name:
        return ""
    return name.strip().lower().replace("_", "-")
