# nixdev

Bootstrap devenv projects with composable templates. Templates are provided via external repositories
imported into your `devenv.yaml`, rather than bundled inside the nixdev package.

## Setup

Import the template you want in your `devenv.yaml`:

```yaml
inputs:
  python-template:
    url: github:USER/python-template
imports:
  - python-template
```

Then run nixdev inside a devenv shell:

```bash
devenv shell
nixdev create python ./my-project
```

## Migration

### Old workflow (bundled templates)

```bash
pip install nixdev
nixdev create python ./my-project
```

### New workflow (external templates)

```bash
pip install nixdev
mkdir my-project
cd my-project

cat > devenv.yaml << 'EOF'
inputs:
  nixdev:
    url: github:USER/nixdev
  python-template:
    url: github:USER/python-template

imports:
  - nixdev
  - python-template
EOF

devenv shell
nixdev create python .
```

## Troubleshooting

### Template not found

If you see:

```
Error: NIXDEV_TEMPLATE_PYTHON not set. Import template via devenv.yaml
```

Make sure your `devenv.yaml` includes the template import:

```yaml
inputs:
  python-template:
    url: github:USER/python-template
imports:
  - python-template
```
