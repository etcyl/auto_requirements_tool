import sys
import sysconfig
import importlib.util
from stdlib_list import stdlib_list

# Accurate stdlib detection using stdlib-list
STDLIB_MODULES = set(stdlib_list(f"{sys.version_info.major}.{sys.version_info.minor}"))

# Explicitly allowlist for modules that may look like stdlib but are external
THIRD_PARTY_WHITELIST = {"stdlib_list", "setuptools", "pkg_resources"}


def is_stdlib(name):
    """Return True if the module belongs to Python's stdlib."""
    if not name or name.startswith("_"):
        return True
    if name in THIRD_PARTY_WHITELIST:
        return False
    if name in sys.builtin_module_names or name in STDLIB_MODULES:
        return True
    try:
        spec = importlib.util.find_spec(name)
        if not spec or not spec.origin:
            return False
        stdlib_path = sysconfig.get_paths().get("stdlib", "")
        return spec.origin.startswith(stdlib_path)
    except Exception:
        return False


def is_local_module(name, repo_path):
    """Check if an import corresponds to a local file or package."""
    import os
    candidate_dir = os.path.join(repo_path, name)
    candidate_file = candidate_dir + ".py"
    return os.path.isdir(candidate_dir) or os.path.exists(candidate_file)
