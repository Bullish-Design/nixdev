# src/nixdev/generator.py
"""Template generation logic using copier."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from copier import run_copy

from nixdev.models import PythonProjectConfig, TemplateResult


class TemplateGenerator:
    """Generate projects from templates."""

    def __init__(self, template_path: Path) -> None:
        """Initialize generator with template path."""
        self.template_path = template_path

    @classmethod
    def from_env(cls, template_name: str) -> TemplateGenerator:
        """Create generator using template path from environment."""
        env_var = f"NIXDEV_TEMPLATE_{template_name.upper()}"
        template_path = os.environ.get(env_var)
        if not template_path:
            raise RuntimeError(f"{env_var} not set. Import template via devenv.yaml")
        return cls(Path(template_path))

    def generate_python_project(
        self,
        config: PythonProjectConfig,
        destination: Path,
        *,
        force: bool = False,
    ) -> TemplateResult:
        """
        Generate Python project from template.

        Args:
            config: Project configuration
            destination: Target directory
            force: Overwrite existing files

        Returns:
            TemplateResult with generation details

        Raises:
            FileExistsError: If destination exists and force=False
            RuntimeError: If template generation fails
        """
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")

        if destination.exists() and not force:
            raise FileExistsError(f"Destination exists: {destination}")

        data = self._config_to_data(config)

        try:
            run_copy(
                src_path=str(self.template_path),
                dst_path=destination,
                data=data,
                unsafe=True,
                quiet=False,
            )
        except Exception as e:
            raise RuntimeError(f"Template generation failed: {e}") from e

        files = [f for f in destination.rglob("*") if f.is_file()]
        imports = self._collect_imports(config)

        return TemplateResult(
            destination=destination,
            files_created=files,
            imports_used=imports,
        )

    def _config_to_data(self, config: PythonProjectConfig) -> dict[str, Any]:
        """Convert PythonProjectConfig to copier data dictionary."""
        return {
            "project_name": config.project_name,
            "project_slug": config.project_slug,
            "package_name": config.package_name,
            "python_version": config.python_version.value,
            "has_cli": config.has_cli,
            "use_precommit": config.use_precommit,
            "services": ",".join(s.value for s in config.services),
        }

    def _collect_imports(self, config: PythonProjectConfig) -> list[str]:
        """Determine which devenv.yaml imports will be used."""
        imports = ["imports/python-base.yaml"]

        if config.use_precommit:
            imports.append("imports/precommit.yaml")

        if config.services:
            imports.append("imports/services.yaml")

        return imports
