#!/usr/bin/env python3
"""Cross-platform dependency checker for Thai ID Team OCR."""

import subprocess
import sys
import os
import shutil
import platform
from pathlib import Path

# Check for command-line arguments
STRICT_STARTUP = "--strict-startup" in sys.argv
IS_WINDOWS = platform.system() == "Windows"

class DependencyChecker:
    """Check system dependencies."""

    def __init__(self):
        self.results = []
        self.has_errors = False
        self.has_warnings = False

    def check_python(self) -> bool:
        """Check Python installation."""
        try:
            result = subprocess.run(
                [sys.executable, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            version = result.stdout.strip() or result.stderr.strip()
            self._log_ok(f"Python found: {version}")
            return True
        except Exception as e:
            self._log_error(f"Python not found: {str(e)}")
            return False

    def check_pip(self) -> bool:
        """Check pip installation."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self._log_ok(f"pip found: {result.stdout.strip()}")
                return True
        except Exception:
            pass
        self._log_error("pip not found")
        return False

    def check_nodejs(self) -> bool:
        """Check Node.js installation."""
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self._log_ok(f"Node.js found: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            pass

        # Node.js is critical only in strict startup mode
        if STRICT_STARTUP:
            self._log_error("Node.js not found")
        else:
            self._log_warn("Node.js not found - frontend may not work")
        return False

    def check_npm(self) -> bool:
        """Check npm installation."""
        try:
            # Try standard npm first
            result = subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=False
            )
            if result.returncode == 0:
                self._log_ok(f"npm found: {result.stdout.strip()}")
                return True

            # On Windows, try npm.cmd
            if IS_WINDOWS:
                result = subprocess.run(
                    ["npm.cmd", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    shell=True
                )
                if result.returncode == 0:
                    self._log_ok(f"npm found (via npm.cmd): {result.stdout.strip()}")
                    return True

        except Exception as e:
            pass

        # npm not found - handle based on mode
        if STRICT_STARTUP:
            self._log_error("npm not found - Node.js may not be in PATH")
        else:
            self._log_warn("npm not found - frontend may not work")

        # Provide helpful guidance on Windows
        if IS_WINDOWS:
            print("   Troubleshoot: Run these in Command Prompt:")
            print("     - where npm")
            print("     - where npm.cmd")
            print("   If npm.cmd exists, Node.js is installed but not in PATH")

        return False

    def check_tesseract(self) -> bool:
        """Check Tesseract OCR installation."""
        try:
            result = subprocess.run(
                ["tesseract", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version_line = (result.stdout.split('\n')[0] if result.stdout else
                               result.stderr.split('\n')[0] if result.stderr else "")
                self._log_ok(f"Tesseract found: {version_line}")
                return True
        except FileNotFoundError:
            pass
        self._log_warn("Tesseract OCR not found - OCR features will not work")
        return False

    def check_thai_language(self) -> bool:
        """Check Thai language data for Tesseract."""
        try:
            result = subprocess.run(
                ["tesseract", "--list-langs"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if "tha" in result.stdout:
                self._log_ok("Thai language data found")
                return True
            else:
                self._log_warn("Thai language data not found - install tesseract-ocr-tha")
                return False
        except FileNotFoundError:
            self._log_warn("Cannot check Thai language (Tesseract not installed)")
            return False

    def check_poppler(self) -> bool:
        """Check Poppler installation for PDF support."""
        try:
            result = subprocess.run(
                ["pdftoppm", "-v"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self._log_ok("Poppler found - PDF support available")
                return True
        except FileNotFoundError:
            pass
        self._log_warn("Poppler not found - PDF OCR support disabled (optional)")
        return False

    def check_venv(self) -> bool:
        """Check Python virtual environment."""
        venv_path = Path("apps/api/.venv")
        if venv_path.exists():
            self._log_ok("Python venv found: apps/api/.venv")
            return True
        else:
            self._log_warn("Python venv not found - run setup-windows.bat first")
            return False

    def check_node_modules(self) -> bool:
        """Check Node.js modules."""
        modules_path = Path("apps/web/node_modules")
        if modules_path.exists():
            self._log_ok("Node modules found: apps/web/node_modules")
            return True
        else:
            self._log_warn("Node modules not found - run setup-windows.bat first")
            return False

    def check_folders(self) -> bool:
        """Check required local folders."""
        folders = ["uploads", "exports", "temp", "backups"]
        all_exist = True
        for folder in folders:
            if Path(folder).exists():
                self._log_ok(f"Folder exists: {folder}/")
            else:
                self._log_warn(f"Folder missing: {folder}/ (will be created on startup)")
                all_exist = False
        return all_exist

    def _log_ok(self, message: str):
        """Log OK status."""
        self.results.append(("OK", message))
        print(f"[OK] {message}")

    def _log_warn(self, message: str):
        """Log warning status."""
        self.results.append(("WARN", message))
        self.has_warnings = True
        print(f"[WARN] {message}")

    def _log_error(self, message: str):
        """Log error status."""
        self.results.append(("ERROR", message))
        self.has_errors = True
        print(f"[ERROR] {message}")

    def run(self):
        """Run all checks."""
        print("\n" + "="*60)
        print("Thai ID Team OCR - Dependency Checker")
        print("="*60 + "\n")

        print("Checking Python environment...")
        self.check_python()
        self.check_pip()

        print("\nChecking Node.js environment...")
        self.check_nodejs()
        self.check_npm()

        print("\nChecking OCR dependencies...")
        self.check_tesseract()
        if not self.has_errors or "Tesseract" not in str(self.results[-1]):
            self.check_thai_language()
        self.check_poppler()

        print("\nChecking local setup...")
        self.check_venv()
        self.check_node_modules()
        self.check_folders()

        print("\n" + "="*60)
        print("Summary")
        print("="*60)

        errors = sum(1 for status, _ in self.results if status == "ERROR")
        warns = sum(1 for status, _ in self.results if status == "WARN")
        oks = sum(1 for status, _ in self.results if status == "OK")

        print(f"\nOK: {oks}")
        if warns > 0:
            print(f"WARN: {warns}")
        if errors > 0:
            print(f"ERROR: {errors}")

        print("\n" + "="*60)

        if self.has_errors:
            print("CRITICAL: Dependencies missing!")
            print("Run: setup-windows.bat")
            return False
        elif self.has_warnings:
            print("WARNING: Some optional features may not work")
            print("See above for details")
            return True
        else:
            print("SUCCESS: All dependencies OK!")
            return True

if __name__ == "__main__":
    checker = DependencyChecker()
    success = checker.run()
    sys.exit(0 if success else 1)
