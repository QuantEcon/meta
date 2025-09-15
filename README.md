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

### Code Style Formatter Action

A GitHub Action that automatically formats Python code in MyST markdown files and standard markdown code blocks using black.

**Location**: `.github/actions/code-style-checker`

**Usage**:
```yaml
- name: Format Python code in markdown files
  uses: QuantEcon/meta/.github/actions/code-style-checker@main
  with:
    files: 'lecture/aiyagari.md,lecture/mccall.md'
    check-myst-code-cells: 'true'
    check-markdown-blocks: 'true'
    python-languages: 'python,python3,ipython,ipython3'
    black-args: '--line-length=88'
    commit-files: 'true'
```

**Use case**: Perfect for maintaining consistent Python code formatting in MyST Markdown/Jupyter Book projects. Can be triggered by PR comments using `@quantecon-code-style` for on-demand formatting of changed files.

See the [action documentation](./.github/actions/code-style-checker/README.md) for detailed usage instructions and examples.

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
