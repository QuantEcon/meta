# meta
For issues and discussion covering more than one repository

## GitHub Actions

This repository contains reusable GitHub Actions for QuantEcon projects:

### Check Warnings Action

A GitHub Action that scans HTML files for Python warnings and optionally fails the workflow if any are found.

**Location**: `.github/actions/check-warnings`

**Usage**:
```yaml
- name: Check for Python warnings
  uses: QuantEcon/meta/.github/actions/check-warnings@main
  with:
    html-path: './_build/html'
    warnings: 'SyntaxWarning,DeprecationWarning,FutureWarning'
    fail-on-warning: 'true'
```

**Use case**: Ideal for checking Jupyter Book builds or any HTML output from Python code execution to ensure no warnings are present in the final documentation.

See the [action documentation](./.github/actions/check-warnings/README.md) for detailed usage instructions and examples.

### AI-Powered Link Checker Action

A GitHub Action that validates web links in HTML files with AI-powered suggestions for improvements. Designed to replace traditional link checkers like `lychee` with enhanced functionality.

**Location**: `.github/actions/link-checker`

**Usage**:
```yaml
- name: AI-powered link check
  uses: QuantEcon/meta/.github/actions/link-checker@main
  with:
    html-path: './_build/html'
    mode: 'full'
    ai-suggestions: 'true'
    silent-codes: '403,503'
```

**Use case**: Perfect for MyST Markdown/Jupyter Book projects. Provides weekly scheduled scans and PR-specific validation with AI suggestions for broken or outdated links.

See the [action documentation](./.github/actions/link-checker/README.md) for detailed usage instructions and examples.
