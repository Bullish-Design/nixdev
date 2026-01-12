# src/nixdev/models.py
"""Pydantic models for NixDev configuration and results."""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class PythonVersion(str, Enum):
    """Supported Python versions."""

    PY312 = "3.12"
    PY311 = "3.11"
    PY310 = "3.10"


class ServiceType(str, Enum):
    """Available services."""

    POSTGRES = "postgres"
    REDIS = "redis"


class PythonProjectConfig(BaseModel):
    """Configuration for Python project template."""

    project_name: str = Field(..., description="Human-readable project name")
    project_slug: str = Field(..., description="Filesystem-safe project name")
    package_name: str = Field(..., description="Python package import name")
    python_version: PythonVersion = Field(default=PythonVersion.PY312)
    has_cli: bool = Field(default=False, description="Include CLI entry point")
    use_precommit: bool = Field(default=True, description="Enable pre-commit hooks")
    services: list[ServiceType] = Field(default_factory=list)

    model_config = {
        "frozen": True,
        "extra": "forbid",
    }

    @field_validator("project_slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        """Ensure slug is filesystem-safe."""
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("project_slug must be alphanumeric with hyphens/underscores")
        return v

    @field_validator("package_name")
    @classmethod
    def validate_package(cls, v: str) -> str:
        """Ensure package name is valid Python identifier."""
        if not v.replace("_", "").isalnum():
            raise ValueError("package_name must be valid Python identifier")
        if v[0].isdigit():
            raise ValueError("package_name cannot start with digit")
        return v


class TemplateResult(BaseModel):
    """Result of template generation."""

    destination: Path = Field(..., description="Generated project directory")
    files_created: list[Path] = Field(default_factory=list)
    imports_used: list[str] = Field(default_factory=list)

    model_config = {
        "frozen": True,
    }


class ValidationResult(BaseModel):
    """Result of project validation."""

    valid: bool = Field(..., description="Whether validation passed")
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    model_config = {
        "frozen": True,
    }
