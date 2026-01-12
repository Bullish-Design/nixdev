# src/nixdev/validators.py
"""Validation utilities for generated projects."""

from __future__ import annotations

import subprocess
from pathlib import Path

from nixdev.models import ValidationResult


class ProjectValidator:
    """Validate generated projects."""

    def validate_structure(self, project_dir: Path) -> ValidationResult:
        """
        Validate project directory structure.

        Checks:
        - Required files exist (devenv.yaml, devenv.nix, pyproject.toml)
        - Source directory structure correct
        - Test directory exists
        """
        errors = []
        warnings = []

        required = ["devenv.yaml", "devenv.nix", "pyproject.toml"]
        for filename in required:
            if not (project_dir / filename).exists():
                errors.append(f"Missing required file: {filename}")

        if not (project_dir / "src").exists():
            errors.append("Missing src/ directory")

        if not (project_dir / "tests").exists():
            warnings.append("Missing tests/ directory")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def validate_devenv(self, project_dir: Path) -> ValidationResult:
        """
        Validate devenv configuration by actually running devenv.

        Runs:
        - devenv shell --clean python --version
        - devenv build

        This is the critical integration test.
        """
        errors = []
        warnings = []

        result = subprocess.run(
            ["devenv", "shell", "--clean", "--", "python", "--version"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            errors.append(f"devenv shell failed: {result.stderr}")

        result = subprocess.run(
            ["devenv", "build"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode != 0:
            errors.append(f"devenv build failed: {result.stderr}")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )
