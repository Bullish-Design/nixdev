# src/nixdev/cli.py
"""CLI interface for NixDev."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from nixdev.generator import TemplateGenerator
from nixdev.models import PythonProjectConfig, PythonVersion, ServiceType
from nixdev.validators import ProjectValidator

app = typer.Typer(help="Bootstrap devenv projects with composable templates")


@app.command()
def list_templates() -> None:
    """List available templates."""
    templates = ["python", "rust", "go", "workspace", "devenv-only"]
    typer.echo("Available templates:")
    for template in templates:
        typer.echo(f"  {template}")


@app.command(name="create")
def create_project(
    template: Annotated[str, typer.Argument(help="Template name")],
    destination: Annotated[Path, typer.Argument(help="Destination directory")],
    project_name: Annotated[str | None, typer.Option(help="Human-readable project name")] = None,
    python_version: Annotated[str, typer.Option(help="Python version")] = "3.12",
    cli: Annotated[bool, typer.Option("--cli/--no-cli", help="Include CLI entry point")] = False,
    precommit: Annotated[bool, typer.Option("--precommit/--no-precommit")] = True,
    services: Annotated[str | None, typer.Option(help="Comma-separated services")] = None,
    interactive: Annotated[bool, typer.Option(help="Interactive prompts")] = True,
) -> None:
    """Create project from template."""
    if template != "python":
        typer.echo(f"Error: Only 'python' template supported in MVP", err=True)
        raise typer.Exit(1)

    project_slug = destination.name
    package_name = project_slug.replace("-", "_")

    if interactive and not project_name:
        project_name = typer.prompt("Project name", default=project_slug.replace("-", " ").title())

    if not project_name:
        project_name = project_slug.replace("-", " ").title()

    service_list = []
    if services:
        for svc in services.split(","):
            svc = svc.strip()
            if svc == "postgres":
                service_list.append(ServiceType.POSTGRES)
            elif svc == "redis":
                service_list.append(ServiceType.REDIS)

    try:
        py_version = PythonVersion(python_version)
    except ValueError:
        typer.echo(f"Error: Invalid Python version: {python_version}", err=True)
        raise typer.Exit(1)

    config = PythonProjectConfig(
        project_name=project_name,
        project_slug=project_slug,
        package_name=package_name,
        python_version=py_version,
        has_cli=cli,
        use_precommit=precommit,
        services=service_list,
    )

    generator = TemplateGenerator.from_package()

    try:
        result = generator.generate_python_project(config, destination)
        typer.echo(f"✓ Created project at {result.destination}")
        typer.echo(f"  Files created: {len(result.files_created)}")
        typer.echo(f"  Imports used: {', '.join(result.imports_used)}")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def init(
    directory: Annotated[Path, typer.Argument(help="Project directory")] = Path("."),
) -> None:
    """Add devenv to existing project."""
    typer.echo(f"Error: 'init' command not implemented in MVP", err=True)
    raise typer.Exit(1)


@app.command()
def validate(
    directory: Annotated[Path, typer.Argument(help="Project directory")] = Path("."),
    full: Annotated[bool, typer.Option(help="Run full devenv integration test")] = False,
) -> None:
    """Validate project structure and configuration."""
    validator = ProjectValidator()

    result = validator.validate_structure(directory)

    if not result.valid:
        typer.echo("Structure validation failed:", err=True)
        for error in result.errors:
            typer.echo(f"  ✗ {error}", err=True)
        raise typer.Exit(1)

    if result.warnings:
        for warning in result.warnings:
            typer.echo(f"  ⚠ {warning}")

    typer.echo("✓ Structure validation passed")

    if full:
        typer.echo("Running devenv integration tests (this may take 1-2 minutes)...")
        result = validator.validate_devenv(directory)

        if not result.valid:
            typer.echo("Devenv validation failed:", err=True)
            for error in result.errors:
                typer.echo(f"  ✗ {error}", err=True)
            raise typer.Exit(1)

        typer.echo("✓ Devenv validation passed")


def main() -> None:
    """Entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
