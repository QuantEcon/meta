# meta
For issues and discussion covering more than one repository

## GitHub Actions

QuantEcon maintains several reusable GitHub Actions that have been migrated to separate repositories for better organization and maintenance:

### Check Warnings Action

A GitHub Action that scans HTML files for Python warnings and optionally fails the workflow if any are found.

**Repository**: [QuantEcon/action-check-warnings](https://github.com/QuantEcon/action-check-warnings)

**Usage**:
```yaml
- name: Check for Python warnings
  uses: QuantEcon/action-check-warnings@main
  with:
    html-path: './_build/html'
    fail-on-warning: 'true'
```

**Use case**: Ideal for checking Jupyter Book builds or any HTML output from Python code execution to ensure no warnings are present in the final documentation.

### AI-Powered Link Checker Action

A GitHub Action that validates web links in HTML files with AI-powered suggestions for improvements. Designed to replace traditional link checkers like `lychee` with enhanced functionality.

**Repository**: [QuantEcon/action-link-checker](https://github.com/QuantEcon/action-link-checker)

**Usage**:
```yaml
- name: AI-powered link check
  uses: QuantEcon/action-link-checker@main
  with:
    html-path: './_build/html'
    mode: 'full'
    ai-suggestions: 'true'
    silent-codes: '403,503'
```

**Use case**: Perfect for MyST Markdown/Jupyter Book projects. Provides weekly scheduled scans and PR-specific validation with AI suggestions for broken or outdated links.

### Activity Reporting Action

A GitHub Action that generates activity reports summarizing issues, PRs, commits, and releases across QuantEcon repositories over any date range.

**Repository**: [QuantEcon/action-reporting](https://github.com/QuantEcon/action-reporting)

**Usage**:
```yaml
- name: Generate activity report
  uses: QuantEcon/action-reporting@v2
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    organization: 'QuantEcon'
```

**Use case**: Automated reporting on repository activity (opened/closed issues, opened/merged PRs, releases, commits). The recurring **weekly status report now runs in the [action-reporting](https://github.com/QuantEcon/action-reporting) repo itself** and records each report as an issue there (filter by the `status-report` label) — it no longer runs from this repo.
