# Check for Python Warnings Action

This GitHub Action scans HTML files for Python warnings and optionally fails the workflow if any are found. It's designed to be used after building documentation or running code that generates HTML output, to ensure that no warnings are present in the final output.

## Features

- Scans HTML files for configurable Python warnings
- Supports multiple warning types (SyntaxWarning, DeprecationWarning, FutureWarning)
- Provides detailed output about warnings found
- Optionally fails the workflow when warnings are detected
- Configurable search path and warning types

## Usage

### Basic Usage

```yaml
- name: Check for Python warnings
  uses: QuantEcon/meta/.github/actions/check-warnings@main
```

### Advanced Usage

```yaml
- name: Check for Python warnings in build output
  uses: QuantEcon/meta/.github/actions/check-warnings@main
  with:
    html-path: './_build/html'
    warnings: 'SyntaxWarning,DeprecationWarning,FutureWarning,UserWarning'
    fail-on-warning: 'true'
```

### Using Outputs

```yaml
- name: Check for Python warnings
  id: warning-check
  uses: QuantEcon/meta/.github/actions/check-warnings@main
  with:
    fail-on-warning: 'false'

- name: Report warnings
  if: steps.warning-check.outputs.warnings-found == 'true'
  run: |
    echo "Found ${{ steps.warning-check.outputs.warning-count }} warnings:"
    echo "${{ steps.warning-check.outputs.warning-details }}"
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `html-path` | Path to directory containing HTML files to scan | No | `.` |
| `warnings` | Comma-separated list of warnings to check for | No | `SyntaxWarning,DeprecationWarning,FutureWarning` |
| `fail-on-warning` | Whether to fail the workflow if warnings are found | No | `true` |

## Outputs

| Output | Description |
|--------|-------------|
| `warnings-found` | Whether warnings were found (`true`/`false`) |
| `warning-count` | Number of warnings found |
| `warning-details` | Details of warnings found |

## Example Workflow

Here's a complete example of how to use this action in a workflow:

```yaml
name: Build and Check Documentation

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-check:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Build documentation
      run: |
        jupyter-book build .
    
    - name: Check for Python warnings
      uses: QuantEcon/meta/.github/actions/check-warnings@main
      with:
        html-path: './_build/html'
        warnings: 'SyntaxWarning,DeprecationWarning,FutureWarning'
        fail-on-warning: 'true'
```

## Use Case

This action is particularly useful for:

1. **Documentation builds**: After building Jupyter Books or Sphinx documentation, check that no Python warnings appear in the generated HTML
2. **Code execution**: When running notebooks or Python scripts that generate HTML output, ensure no warnings are present
3. **Continuous Integration**: Maintain code quality by preventing warnings from being introduced

## How It Works

1. The action searches for all `.html` files in the specified directory
2. For each HTML file, it searches for the specified warning strings
3. If warnings are found, it reports the details and optionally fails the workflow
4. The action provides outputs that can be used by subsequent steps

## Error Handling

- If the specified HTML path doesn't exist, the action will fail with an error
- The action will report the exact location (file and line number) where warnings are found
- When `fail-on-warning` is `true`, the workflow will fail if any warnings are detected