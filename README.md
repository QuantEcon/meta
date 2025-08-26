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

### QuantEcon Style Guide Action

An AI-powered GitHub Action that checks QuantEcon content for style guide compliance and provides automated suggestions and improvements.

**Location**: `.github/actions/qe-style-guide`

**Usage**:
Comment-triggered style checks:
- **Issues**: `@qe-style-check filename.md` - Creates a PR with comprehensive style review
- **Pull Requests**: `@qe-style-check` - Applies high-confidence style improvements to the PR

**Direct workflow usage**:
```yaml
- name: Check style guide compliance
  uses: QuantEcon/meta/.github/actions/qe-style-guide@main
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    openai-api-key: ${{ secrets.OPENAI_API_KEY }}  # Optional
    style-guide: '.github/copilot-qe-style-guide.md'
```

**Use case**: Automated style guide enforcement with AI-powered analysis, ensuring consistent writing style, code formatting, mathematical notation, and document structure across QuantEcon content.

See the [action documentation](./.github/actions/qe-style-guide/README.md) for detailed usage instructions and examples.
