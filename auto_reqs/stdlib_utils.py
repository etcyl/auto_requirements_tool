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

    # Built-ins and standard library lists (Python 3.10+)
    if name in sys.builtin_module_names or (
        hasattr(sys, "stdlib_module_names") and name in sys.stdlib_module_names
    ):
        return True

    if name in LEGACY_STDLIB_NAMES:
        return True

    # Check via module spec
    try:
        spec = importlib.util.find_spec(name)
        if not spec or not spec.origin:
            return False
        stdlib_path = sysconfig.get_paths().get("stdlib", "")
        return spec.origin.startswith(stdlib_path) or spec.origin.startswith(sys.base_prefix)
    except (ImportError, AttributeError):
        return False
