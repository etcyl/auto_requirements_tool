import importlib.metadata
import requests
from auto_reqs.utils import normalize_pkg_name


def get_installed_distributions():
    """Return installed distributions as {package_name: version}."""
    dists = {}
    for dist in importlib.metadata.distributions():
        try:
            name = normalize_pkg_name(dist.metadata["Name"])
            dists[name] = dist.version
        except Exception:
            continue
    return dists


def resolve_import_to_pkg(name):
    """Resolve an import name to its PyPI package name."""
    mapping = importlib.metadata.packages_distributions()
    if name in mapping:
        return normalize_pkg_name(mapping[name][0])

    # Fallback: verify existence on PyPI
    pkg_name = normalize_pkg_name(name)
    try:
        resp = requests.get(f"https://pypi.org/pypi/{pkg_name}/json", timeout=3)
        if resp.status_code == 200:
            return pkg_name
    except Exception:
        pass
    return pkg_name


def get_latest_version_from_pypi(package_name):
    """Fetch latest version from PyPI for a given package."""
    pkg = normalize_pkg_name(package_name)
    try:
        r = requests.get(f"https://pypi.org/pypi/{pkg}/json", timeout=5)
        if r.status_code == 200:
            return r.json()["info"]["version"]
    except Exception:
        pass
    return None
