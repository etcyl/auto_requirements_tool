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
    """
    missing, unused = [], []

    # Filter out stdlib and local imports
    imports_filtered = [
        imp
        for imp in imports
        if not is_stdlib(imp)
        and not is_local_module(imp, repo_path)
        and not imp.startswith("_")
    ]

    normalized_imports = {normalize_pkg_name(imp) for imp in imports_filtered}

    # Detect missing packages
    for norm_imp in sorted(normalized_imports):
        if norm_imp not in requirements:
            pkg_name = normalize_pkg_name(resolve_import_to_pkg(norm_imp))
            version = installed.get(pkg_name) or resolver(pkg_name)
            if version:
                requirements[pkg_name] = version
                missing.append((pkg_name, version))
            else:
                print(f"Warning: Could not find version for '{norm_imp}'")

    # Detect unused packages
    for pkg in list(requirements.keys()):
        if pkg not in normalized_imports:
            unused.append(pkg)
            del requirements[pkg]

    return missing, unused
