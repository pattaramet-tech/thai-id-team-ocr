#!/usr/bin/env python3
"""Check current version and latest available version."""

import subprocess
import sys
from pathlib import Path

def get_current_version():
    """Get current app version from version.py."""
    try:
        version_file = Path("apps/api/app/version.py")
        if version_file.exists():
            with open(version_file) as f:
                for line in f:
                    if "APP_VERSION" in line:
                        # Parse: APP_VERSION = "0.5.0"
                        version = line.split('"')[1]
                        return version
    except Exception as e:
        print(f"[ERROR] Could not read version: {str(e)}")
    return None

def get_latest_tag():
    """Get latest git tag (version)."""
    try:
        # First fetch to get latest tags
        subprocess.run(
            ["git", "fetch", "--tags", "-q"],
            timeout=10,
            capture_output=True
        )

        # Get latest tag
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            tag = result.stdout.strip()
            # Remove 'v' prefix if present
            if tag.startswith("v"):
                tag = tag[1:]
            return tag
    except Exception:
        pass

    return None

def get_latest_commit():
    """Get latest commit info."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=format:%h %s"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass

    return None

def main():
    """Check and display version info."""
    print("\n" + "="*60)
    print("Version Information")
    print("="*60 + "\n")

    # Current version
    current = get_current_version()
    if current:
        print(f"Current Local Version: v{current}")
    else:
        print("Current Local Version: Unknown")

    # Latest git tag
    latest_tag = get_latest_tag()
    if latest_tag:
        print(f"Latest Git Tag:        v{latest_tag}")
    else:
        print("Latest Git Tag:        Not found")

    # Latest commit
    latest_commit = get_latest_commit()
    if latest_commit:
        print(f"Latest Commit:         {latest_commit}")

    print("\n" + "="*60)

    # Check if update available
    if current and latest_tag:
        if current == latest_tag:
            print("Status: Already on latest version ✓")
            return True
        else:
            print(f"Status: Update available (v{current} → v{latest_tag})")
            return False
    else:
        print("Status: Could not determine version status")
        return None

if __name__ == "__main__":
    result = main()
    sys.exit(0)
