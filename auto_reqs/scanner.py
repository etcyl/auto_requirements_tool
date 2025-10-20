import ast
import os

EXCLUDE_DIRS_DEFAULT = {
    "__pycache__",
    ".git",
    "venv",
    ".venv",
    "env",
    "build",
    "dist",
    "site-packages",
}


def extract_imports_from_file(filepath):
    """Extract import names from a Python file."""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except SyntaxError:
            return set()

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    return imports


def scan_project_for_imports(root_dir, exclude_dirs=None):
    """Recursively scan the given directory for Python imports."""
    if exclude_dirs is None:
        exclude_dirs = EXCLUDE_DIRS_DEFAULT

    all_imports = set()
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith(".")]
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                all_imports.update(extract_imports_from_file(path))
    return all_imports

if __name__ == "__main__":
    import sys
    import json

    # --- Parse arguments ---
    debug = "--debug" in sys.argv
    # first positional arg (if any) is the repo path
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    repo_path = args[0] if args else "."

    # --- Run the scan ---
    imports = scan_project_for_imports(repo_path)

    # --- Output results ---
    if debug:
        print(f"🔍 Scanned directory: {os.path.abspath(repo_path)}")
        print(f"📁 Found {len(imports)} imports:\n")
        for imp in sorted(imports):
            print("   ", imp)
    else:
        # default JSON output (useful for programmatic calls)
        print(json.dumps(sorted(imports), indent=2))
