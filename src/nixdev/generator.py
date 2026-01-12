# src/nixdev/generator.py
"""Template generation logic using copier."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from copier import run_copy

from nixdev.models import PythonProjectConfig, TemplateResult


class TemplateGenerator:
    """Generate projects from templates."""

    def __init__(self, templates_dir: Path) -> None:
        """Initialize generator with templates directory."""
        self.templates_dir = templates_dir

    @classmethod
    def from_package(cls) -> TemplateGenerator:
        """Create generator using bundled templates."""
        templates_dir = Path(__file__).parent.parent.parent / "templates"
        return cls(templates_dir)

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
        template_path = self.templates_dir / "python"

        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        if destination.exists() and not force:
            raise FileExistsError(f"Destination exists: {destination}")

        data = self._config_to_data(config)

        try:
            run_copy(
                src_path=str(template_path),
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
