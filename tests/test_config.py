import json
import os
import pytest
from auto_reqs.config import load_config, DEFAULT_CONFIG


class TestLoadConfig:
    def test_returns_default_when_file_missing(self, tmp_path):
        """Should return default config when .auto-reqs.json does not exist."""
        repo_path = tmp_path
        result = load_config(str(repo_path))
        assert result == DEFAULT_CONFIG

    def test_loads_and_merges_user_config(self, tmp_path):
        """Should merge user config with defaults (user overrides take priority)."""
        repo_path = tmp_path
        user_cfg = {
            "exclude": ["venv", "build", "temp"],
            "ignore_warnings": False,
            "custom_key": True
        }

        cfg_path = repo_path / ".auto-reqs.json"
        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(user_cfg, f)

        result = load_config(str(repo_path))

        # It should merge, not replace defaults entirely
        assert isinstance(result, dict)
        assert result["exclude"] == ["venv", "build", "temp"]
        assert result["ignore_warnings"] is False
        assert result["custom_key"] is True
        # Ensure default "include" key still exists
        assert "include" in result

    def test_invalid_json_returns_default(self, tmp_path):
        """Should return defaults when JSON file is corrupted."""
        repo_path = tmp_path
        cfg_path = repo_path / ".auto-reqs.json"
        cfg_path.write_text("{invalid_json}")

        result = load_config(str(repo_path))
        assert result == DEFAULT_CONFIG
