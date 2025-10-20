import json
import os

DEFAULT_CONFIG = {
    "exclude": ["venv", ".venv", "env", "build", "dist", "__pycache__", ".git"],
    "include": [],
    "ignore_warnings": True
}

def load_config(repo_path):
    """Load .auto-reqs.json if present; otherwise use defaults."""
    cfg_path = os.path.join(repo_path, ".auto-reqs.json")
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
            return {**DEFAULT_CONFIG, **user_cfg}
        except Exception:
            pass
    return DEFAULT_CONFIG
