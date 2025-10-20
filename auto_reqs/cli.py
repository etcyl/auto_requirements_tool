import argparse
import os
from auto_reqs.utils import validate_repo_path
from auto_reqs.scanner import scan_project_for_imports
from auto_reqs.resolver import get_installed_distributions, get_latest_version_from_pypi
from auto_reqs.updater import load_requirements, write_requirements, determine_changes
from auto_reqs.config import load_config


def main():
    parser = argparse.ArgumentParser(description="Auto Reqs - Smart dependency manager")
    parser.add_argument("action", choices=["scan", "update", "upgrade"], help="Action to perform")
    parser.add_argument("path", help="Path to Python project directory")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing file")

    args = parser.parse_args()
    repo_path = validate_repo_path(args.path)
    config = load_config(repo_path)

    print(f"Scanning repository at: {repo_path}")
    imports = scan_project_for_imports(repo_path, config["exclude"])
    installed = get_installed_distributions()
    req_path = os.path.join(repo_path, "requirements.txt")
    requirements = load_requirements(req_path)

    missing, unused = determine_changes(
        imports, installed, requirements, get_latest_version_from_pypi, repo_path
    )

    if args.dry_run:
        print("\nDry Run: no changes will be saved.")
    else:
        write_requirements(requirements, req_path)

    if missing:
        print(f"\nAdded {len(missing)} new packages:")
        for name, version in missing:
            print(f"  {name}=={version}")
    if unused:
        print(f"\nRemoved {len(unused)} unused packages:")
        for pkg in unused:
            print(f"  {pkg}")
    if not missing and not unused:
        print("\nNo changes required.")


if __name__ == "__main__":
    main()
