import os
from auto_reqs.classifier import is_stdlib, is_local_module
from auto_reqs.resolver import resolve_import_to_pkg
from auto_reqs.utils import normalize_pkg_name


def load_requirements(path):
    """Load existing requirements into a dict of {package_name: version}."""
    reqs = {}
    if not os.path.exists(path):
        return reqs
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "==" in line:
                name, version = line.split("==", 1)
                reqs[normalize_pkg_name(name)] = version
            else:
                reqs[normalize_pkg_name(line)] = None
    return reqs


def write_requirements(requirements, path):
    """Write the final sorted requirements.txt file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Automatically maintained by auto-reqs\n")
        for name, version in sorted(requirements.items()):
            if version:
                f.write(f"{name}=={version}\n")
            else:
                f.write(f"{name}\n")


def determine_changes(imports, installed, requirements, resolver, repo_path):
    """
    Compare imports vs requirements and detect missing or unused packages.
    Filters out stdlib and local modules, normalizes all names.
    Dynamically imports helpers at runtime so monkeypatches take effect.
    """
    # --- Dynamic imports (ensures test patches are honored) ---
    from auto_reqs.classifier import is_stdlib, is_local_module
    from auto_reqs.resolver import resolve_import_to_pkg
    from auto_reqs.utils import normalize_pkg_name

    missing, unused = [], []

    def norm(name: str) -> str:
        """Normalize consistently across imports, installed, and requirements."""
        if not name:
            return ""
        return normalize_pkg_name(name).lower().replace("_", "-")

    # Normalize all dict keys for consistent comparison
    installed_norm = {norm(k): v for k, v in installed.items()}
    requirements_norm = {norm(k): v for k, v in requirements.items()}

    # Filter and normalize imports
    imports_norm = {
        norm(i)
        for i in imports
        if not is_stdlib(i)
        and not is_local_module(i, repo_path)
        and not i.startswith("_")
    }

    # --- Detect missing packages ---
    for pkg in sorted(imports_norm):
        if pkg not in requirements_norm:
            resolved = norm(resolve_import_to_pkg(pkg))
            version = (
                installed_norm.get(resolved)
                or installed_norm.get(pkg)
                or resolver(resolved)
                or resolver(pkg)
            )
            if version:
                requirements[resolved] = version
                requirements_norm[resolved] = version
                missing.append((resolved, version))
            else:
                print(f"Warning: Could not find version for '{pkg}'")

    # --- Detect unused packages ---
    imports_set = set(imports_norm)
    for pkg in list(requirements.keys()):
        if norm(pkg) not in imports_set:
            unused.append(pkg)
            del requirements[pkg]

    return missing, unused
