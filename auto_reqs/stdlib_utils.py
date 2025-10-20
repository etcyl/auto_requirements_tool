import sys
import sysconfig
import importlib.util

# Legacy stdlib aliases that may appear in old codebases or vendored libs
LEGACY_STDLIB_NAMES = {
    "Queue",
    "StringIO",
    "ConfigParser",
    "cPickle",
    "SocketServer",
    "SimpleHTTPServer",
    "BaseHTTPServer",
    "UserDict",
    "UserList",
    "UserString",
    "whichdb",
    "dbhash",
    "commands",
    "copy_reg",
    "dummy_thread",
    "dummy_threading",
    "repr",
    "urlparse",
    "urllib2",
    "htmlentitydefs",
    "httplib",
}


def is_stdlib_module(name: str) -> bool:
    """Return True if the module belongs to Python's stdlib or builtins."""
    if not name or name.startswith("_"):
        return True

    # Built-ins and modern stdlib names
    if name in sys.builtin_module_names or (
        hasattr(sys, "stdlib_module_names") and name in sys.stdlib_module_names
    ):
        return True

    if name in LEGACY_STDLIB_NAMES:
        return True

    try:
        spec = importlib.util.find_spec(name)
        if not spec or not getattr(spec, "origin", None):
            return False

        origin = spec.origin
        stdlib_path = sysconfig.get_paths().get("stdlib", "")
        purelib_path = sysconfig.get_paths().get("purelib", "")
        platlib_path = sysconfig.get_paths().get("platlib", "")

        # Normalize paths to lowercase for cross-platform comparison
        origin_lower = origin.lower().replace("\\", "/")
        stdlib_lower = stdlib_path.lower().replace("\\", "/")
        purelib_lower = purelib_path.lower().replace("\\", "/")
        platlib_lower = platlib_path.lower().replace("\\", "/")

        # Only count as stdlib if inside the stdlib directory
        # and NOT in any site-packages directory
        if stdlib_lower and origin_lower.startswith(stdlib_lower):
            if "site-packages" in origin_lower:
                return False
            return True

        # Explicitly exclude site-packages
        if purelib_lower and origin_lower.startswith(purelib_lower):
            return False
        if platlib_lower and origin_lower.startswith(platlib_lower):
            return False

        return False
    except Exception:
        return False
