# Code Style Checker Examples

This document provides examples of how to use the Code Style Checker action in various scenarios.

## Basic Usage Examples

### 1. Simple Style Check

Check code style in a built documentation directory:

```yaml
name: Documentation Style Check
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  style-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # Build your documentation first
      - name: Build docs
        run: |
          # Your documentation build commands here
          jupyter-book build lectures/
      
      - name: Check code style
        uses: ./.github/actions/code-style-checker
        with:
          html-path: './lectures/_build/html'
```

### 2. PR Comment Integration

Automatically comment on PRs with style issues:

```yaml
- name: Check code style with PR comments
  uses: ./.github/actions/code-style-checker
  with:
    html-path: './_build/html'
    fail-on-style-issues: 'true'
    checkers: 'flake8,black'
    max-line-length: '88'
```

### 3. Issue Creation for Main Branch

Create issues when style problems are found on main branch:

```yaml
- name: Check code style and create issues
  if: github.ref == 'refs/heads/main'
  uses: ./.github/actions/code-style-checker
  with:
    html-path: './_build/html'
    fail-on-style-issues: 'false'
    create-issue: 'true'
    issue-title: 'Code Style Issues Found in Documentation'
    notify: 'maintainer1,maintainer2'
```

## Advanced Configuration Examples

### 4. Custom Checker Selection

Use only specific style checkers:

```yaml
# Only check formatting with black
- name: Check formatting only
  uses: ./.github/actions/code-style-checker
  with:
    html-path: './docs/_build'
    checkers: 'black'
    max-line-length: '100'

# Only check PEP8 compliance
- name: Check PEP8 compliance
  uses: ./.github/actions/code-style-checker
  with:
    html-path: './docs/_build'
    checkers: 'flake8,pep8'
```

### 5. Exclude Common Patterns

Exclude installation commands and display functions:

```yaml
- name: Check style with exclusions
  uses: ./.github/actions/code-style-checker
  with:
    html-path: './_build/html'
    exclude-patterns: '!pip install,!conda install,plt.show(),plt.figure(),# noqa,%%time'
    checkers: 'flake8,black'
```

### 6. Generate Artifacts for Analysis

Create downloadable reports:

```yaml
- name: Check style with artifact generation
  uses: ./.github/actions/code-style-checker
  with:
    html-path: './_build/html'
    fail-on-style-issues: 'false'
    create-artifact: 'true'
    artifact-name: 'weekly-style-report'
    checkers: 'flake8,black,pep8'
```

## Integration Examples

### 7. QuantEcon Lecture Series

Example for QuantEcon lecture repositories:

```yaml
name: Lecture Quality Check
on:
  pull_request:
    paths: 
      - 'lectures/**/*.md'
      - 'lectures/**/*.ipynb'

jobs:
  build-and-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install jupyter-book quantecon matplotlib numpy pandas
      
      - name: Build lectures
        run: |
          jupyter-book build lectures/
      
      - name: Check code style
        uses: ./.github/actions/code-style-checker
        with:
          html-path: './lectures/_build/html'
          checkers: 'flake8,black'
          max-line-length: '88'
          exclude-patterns: '!pip install,plt.show(),plt.figure(),# noqa'
          fail-on-style-issues: 'true'
```

### 8. Weekly Quality Reports

Scheduled checks with comprehensive reporting:

```yaml
name: Weekly Code Quality Report
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM UTC
  workflow_dispatch:

jobs:
  quality-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build documentation
        run: |
          # Build your docs
          make html
      
      - name: Comprehensive style check
        uses: ./.github/actions/code-style-checker
        with:
          html-path: './_build/html'
          checkers: 'flake8,black,pep8'
          fail-on-style-issues: 'false'
          create-issue: 'true'
          create-artifact: 'true'
          issue-title: 'Weekly Code Style Report'
          artifact-name: 'style-report'
          notify: 'code-maintainers'
```

### 9. Multi-Directory Checking

Check multiple documentation directories:

```yaml
- name: Check multiple directories
  strategy:
    matrix:
      docs-path: 
        - './python/_build/html'
        - './julia/_build/html'
        - './lectures/_build/html'
  uses: ./.github/actions/code-style-checker
  with:
    html-path: ${{ matrix.docs-path }}
    checkers: 'flake8,black'
    fail-on-style-issues: 'false'
```

### 10. Conditional Checking

Only check when relevant files change:

```yaml
name: Smart Style Checking
on:
  pull_request:
    paths:
      - '**.md'
      - '**.ipynb'
      - '**.py'

jobs:
  check-changes:
    runs-on: ubuntu-latest
    outputs:
      docs-changed: ${{ steps.changes.outputs.docs }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v2
        id: changes
        with:
          filters: |
            docs:
              - 'lectures/**'
              - 'docs/**'

  style-check:
    needs: check-changes
    if: needs.check-changes.outputs.docs-changed == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build and check
        run: |
          jupyter-book build lectures/
      
      - name: Style check
        uses: ./.github/actions/code-style-checker
        with:
          html-path: './lectures/_build/html'
```

## Configuration Best Practices

### Recommended Settings for Different Use Cases

**For Development/PR Checks:**
```yaml
checkers: 'flake8,black'
max-line-length: '88'
fail-on-style-issues: 'true'
exclude-patterns: '!pip install,plt.show(),# noqa'
```

**For Weekly Quality Reports:**
```yaml
checkers: 'flake8,black,pep8'
max-line-length: '88'
fail-on-style-issues: 'false'
create-issue: 'true'
create-artifact: 'true'
```

**For Documentation Repositories:**
```yaml
checkers: 'flake8,black'
exclude-patterns: '!pip install,!conda install,plt.show(),plt.figure(),%%time,# noqa'
max-line-length: '88'
```

### Common Exclude Patterns

- `!pip install` - Package installation commands
- `!conda install` - Conda package installations  
- `plt.show()` - Matplotlib display commands
- `plt.figure()` - Figure creation
- `# noqa` - Explicitly marked lines to ignore
- `%%time` - Jupyter magic commands
- `%%timeit` - Jupyter timing magic
- `%matplotlib` - Matplotlib magic commands

### Error Handling

Always include error handling for robust workflows:

```yaml
- name: Style check with error handling
  id: style-check
  continue-on-error: true
  uses: ./.github/actions/code-style-checker
  with:
    html-path: './_build/html'
    fail-on-style-issues: 'true'

- name: Handle style check results
  if: always()
  run: |
    if [ "${{ steps.style-check.outcome }}" = "failure" ]; then
      echo "Style issues found, but continuing workflow"
      # Add any cleanup or notification logic here
    fi
```