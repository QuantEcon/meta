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

### Weekly Report Action

A GitHub Action that generates a weekly report summarizing issues and PR activity across all QuantEcon repositories.

**Repository**: [QuantEcon/action-weekly-report](https://github.com/QuantEcon/action-weekly-report)

**Usage**:
```yaml
- name: Generate weekly report
  uses: QuantEcon/action-weekly-report@main
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    organization: 'QuantEcon'
    output-format: 'markdown'
```

**Use case**: Automated weekly reporting on repository activity including opened/closed issues and merged PRs. Runs automatically every Saturday and creates an issue with the report.
