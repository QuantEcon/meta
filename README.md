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
    # Uses comprehensive default warnings (all Python warning types)
    fail-on-warning: 'true'
```

**Use case**: Ideal for checking Jupyter Book builds or any HTML output from Python code execution to ensure no warnings are present in the final documentation.

See the [action documentation](./.github/actions/check-warnings/README.md) for detailed usage instructions and examples.

### Weekly Report Action

A GitHub Action that generates a weekly report summarizing issues and PR activity across all QuantEcon repositories.

**Location**: `.github/actions/weekly-report`

**Usage**:
```yaml
- name: Generate weekly report
  uses: QuantEcon/meta/.github/actions/weekly-report@main
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    organization: 'QuantEcon'
    output-format: 'markdown'
```

**Use case**: Automated weekly reporting on repository activity including opened/closed issues and merged PRs. Runs automatically every Saturday and creates an issue with the report.

See the [action documentation](./.github/actions/weekly-report/README.md) for detailed usage instructions and examples.
