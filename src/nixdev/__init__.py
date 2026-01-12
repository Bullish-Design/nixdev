# src/nixdev/__init__.py
"""NixDev - Bootstrap devenv projects with composable templates."""

from __future__ import annotations

from nixdev.generator import TemplateGenerator
from nixdev.models import (
    PythonProjectConfig,
    PythonVersion,
    ServiceType,
    TemplateResult,
    ValidationResult,
)
from nixdev.validators import ProjectValidator

__version__ = "0.1.0"

__all__ = [
    "TemplateGenerator",
    "ProjectValidator",
    "PythonProjectConfig",
    "PythonVersion",
    "ServiceType",
    "TemplateResult",
    "ValidationResult",
]
