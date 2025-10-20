# Auto Requirements Tool (`auto_requirements_tool`)

Automatically detect and maintain accurate `requirements.txt` files for your Python projects.
This tool scans your codebase, compares imports against installed packages, and automatically adds or removes dependencies to keep your requirements clean and consistent.

---

##  Features
- Detects new imports and missing dependencies.
- Removes unused or stale entries from `requirements.txt`.
- Differentiates between **stdlib**, **local**, and **third-party** modules.
- Supports dry-run mode for safe previews.
- Lightweight CLI integration: `auto-reqs`.

---

##  Installation

### Using Conda (recommended)
```bash
conda create -n auto-reqs python=3.12 -y
conda activate auto-reqs
pip install -e .
```

### Using pip
```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .
```

---

##  Usage

### Basic Scan
Run from the root of your repository:
```bash
auto-reqs update .
```
This command scans all Python files and updates your `requirements.txt` automatically — adding missing packages and removing unused ones.

### Dry Run
Preview changes before applying:
```bash
auto-reqs dry-run .
```
This displays what would be added or removed without modifying your files.

### Example Output
```
Scanning repository at: /home/user/myproject

Added 2 new packages:
  requests==2.31.0
  numpy==1.26.0

Removed 1 unused package:
  oldlib
```

---

##  Project Structure
```
auto_requirements_tool/
├── auto_reqs/
│   ├── __init__.py
│   ├── cli.py
│   ├── classifier.py
│   ├── resolver.py
│   ├── updater.py
│   ├── stdlib_utils.py
│   └── utils.py
├── tests/
│   ├── test_updater.py
│   ├── test_utils.py
│   └── test_stdlib_utils.py
└── README.md
```

---

##  Developer Setup

### Run Tests
```bash
pytest -v
```

### Code Formatting
```bash
black auto_reqs tests
isort auto_reqs tests
flake8 auto_reqs
```

### Cleaning Up
```bash
find . -name "*.pyc" -delete
```

---

##  Example Development Workflow
```bash
git clone https://github.com/yourusername/auto_requirements_tool.git
cd auto_requirements_tool
conda create -n auto-reqs python=3.12 -y
conda activate auto-reqs
pip install -e .
auto-reqs dry-run .
auto-reqs update .
pytest -v
```

---

##  License
MIT License (omit if internal-only).

---

##  Notes
- The tool relies on `stdlib-list` to identify Python’s standard library modules.
- Tested with Python 3.11 and 3.12 on Linux.
- For maximum accuracy, ensure your virtual environment matches your active imports.

