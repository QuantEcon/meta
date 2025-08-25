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

### QuantEcon Style Guide Checker

An AI-enabled GitHub Action that checks lecture compliance with the QuantEcon Style Guide and provides intelligent suggestions for improvements.

**Location**: `.github/actions/qe-style-check`

**Usage**:
```yaml
# PR Mode (triggered by @qe-style-check mention)
- name: Style Guide Check
  uses: QuantEcon/meta/.github/actions/qe-style-check@main
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    lectures: 'lectures'
    mode: 'pr'

# Scheduled Mode (complete review)
- name: Weekly Style Review
  uses: QuantEcon/meta/.github/actions/qe-style-check@main
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    mode: 'scheduled'
    create-individual-prs: 'true'
```

**Features**:
- **Dual Operation Modes**: PR-triggered checks and scheduled complete reviews
- **Intelligent Analysis**: Rule-based checking with confidence levels (high/medium/low)
- **Automated Fixes**: High confidence suggestions can be auto-committed
- **Comprehensive Reporting**: Detailed tables with suggestions organized by confidence
- **Flexible Configuration**: Customizable paths, exclusions, and thresholds

**Use case**: Automated style guide compliance checking for QuantEcon lectures, ensuring consistent formatting, proper mathematical notation, code style, and figure presentation across all content.

See the [action documentation](./.github/actions/qe-style-check/README.md) for detailed usage instructions and examples.

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
