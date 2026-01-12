# devenv.nix
{ pkgs, config, ... }: {
  languages.python = {
    enable = true;
    version = "3.12";
    uv.enable = true;
  };

  #packages = with pkgs; [
  #  python312Packages.copier
  #];

  scripts = {
    test.exec = "pytest \"$@\"";
    test-example.exec = "python tests/test_example.py";
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
