# devenv.nix
{ pkgs, config, ... }: {
  languages.python = {
    enable = true;
    version = "3.12";
    uv.enable = true;
  };

  packages = with pkgs; [
    python312Packages.copier
  ];

  scripts = {
    test.exec = "pytest \"$@\"";
    test-example.exec = ''
      set -euo pipefail

      timestamp="$(date +%Y%m%d%H%M%S)"
      output_dir="tests/templates/output/python_${timestamp}"

      mkdir -p "$output_dir"

      export NIXDEV_TEMPLATE_PYTHON="$(pwd)/tests/templates/python"

      python -m nixdev.cli create python "$output_dir" \
        --no-interactive \
        --project-name "Example Project" \
        --python-version "3.12"

      diff -ru tests/templates/expected/python "$output_dir"
    '';
    format.exec = "ruff format src/ tests/";
    lint.exec = "ruff check src/ tests/";
    type-check.exec = "mypy src/";
  };

  git-hooks.hooks = {
    ruff-format.enable = true;
    #ruff-check.enable = true;
  };

  profiles.dev.module = {
    git-hooks.enable = true;
  };

  outputs = {
    nixdev = config.languages.python.import ./. {};
  };
}
