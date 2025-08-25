# QuantEcon Style Guide Checker Examples

This document provides practical examples of using the QuantEcon Style Guide Checker action in different scenarios.

## Quick Start

### 1. Enable PR Style Checking

Add this workflow to `.github/workflows/style-check-pr.yml`:

```yaml
name: Style Check on PR Comment
on:
  issue_comment:
    types: [created]

jobs:
  style-check:
    if: github.event.issue.pull_request && contains(github.event.comment.body, '@qe-style-check')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: QuantEcon/meta/.github/actions/qe-style-check@main
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          lectures: 'lectures'
```

**Usage**: Comment `@qe-style-check` on any PR to trigger style checking.

### 2. Weekly Automated Review

Add this workflow to `.github/workflows/weekly-style-check.yml`:

```yaml
name: Weekly Style Review
on:
  schedule:
    - cron: '0 9 * * 1'  # Monday 9 AM UTC

jobs:
  style-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: QuantEcon/meta/.github/actions/qe-style-check@main
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          mode: 'scheduled'
          create-individual-prs: 'true'
```

## Common Configuration Examples

### Custom Lecture Directory

```yaml
- uses: QuantEcon/meta/.github/actions/qe-style-check@main
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    lectures: 'source/rst'  # Custom path
```

### Exclude Specific Files

```yaml
- uses: QuantEcon/meta/.github/actions/qe-style-check@main
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    exclude-files: 'index.md,references.md,.*draft.*'
```

### External Style Guide

```yaml
- uses: QuantEcon/meta/.github/actions/qe-style-check@main
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    style-guide: 'https://raw.githubusercontent.com/MyOrg/docs/main/style.md'
```

### Lower Confidence Threshold

```yaml
- uses: QuantEcon/meta/.github/actions/qe-style-check@main
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    confidence-threshold: 'medium'  # Auto-commit medium confidence changes
```

## Integration Examples

### With Documentation Build

```yaml
name: Build and Style Check
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build documentation
        run: jupyter-book build lectures/
      - name: Check style compliance
        uses: QuantEcon/meta/.github/actions/qe-style-check@main
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          lectures: 'lectures'
```

### Pre-Release Style Validation

```yaml
name: Release Preparation
on:
  workflow_dispatch:
    inputs:
      create_release:
        description: 'Create release after style check'
        default: 'false'

jobs:
  style-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Comprehensive style check
        uses: QuantEcon/meta/.github/actions/qe-style-check@main
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          mode: 'scheduled'
          confidence-threshold: 'low'
      - name: Fail if issues found
        if: steps.style-check.outputs.suggestions-found == 'true'
        run: |
          echo "Style issues found, cannot proceed with release"
          exit 1
```

## Style Rules Reference

The action checks for compliance with these QuantEcon Style Guide rules:

### Writing (R001-R005)
- **R001**: Keep it clear and keep it short
- **R002**: Use one sentence paragraphs only  
- **R003**: Keep paragraphs short and clear
- **R004**: Choose the simplest option
- **R005**: Don't capitalize unless necessary

### Code Style (R006-R015)
- **R008**: Use Unicode Greek letters (α, β, γ, etc.)
- **R015**: Use `qe.Timer()` context manager

### Math Notation (R016-R021)
- **R016**: Use `\top` for transpose
- **R020**: Don't use `\tag` for manual numbering

### Figures (R022-R029)
- **R022**: No `ax.set_title()` in matplotlib
- **R028**: Use `lw=2` for line charts

## Troubleshooting

### No Files Found
```yaml
# Ensure correct path
lectures: 'source'  # Not 'source/'
```

### Too Many Suggestions
```yaml
# Start with high confidence only
confidence-threshold: 'high'
exclude-files: 'intro.md,index.md'
```

### Permission Errors
```yaml
# Ensure token has proper permissions
permissions:
  contents: write
  pull-requests: write
```

## Expected Output Examples

### Clean Files
```
✅ Excellent! All files comply with the QuantEcon Style Guide.
📊 Summary: 5 files processed, no issues found.
```

### Files with Issues
```
📊 Summary: 3 files processed
✨ Applied 12 high confidence suggestions and committed changes to this PR.
📋 Additional Suggestions:
| Confidence | Count | Description |
|------------|-------|-------------|
| Medium | 8 | Likely improvements that may need review |
| Low | 3 | Suggestions that need human review |
```

### Detailed Report (collapsed)
```
📝 Detailed Style Suggestions

## lecture1.md
### High Confidence Suggestions (4)
| Line | Rule | Description | Original | Proposed |
|------|------|-------------|----------|----------|
| 25 | R008 | Use α instead of alpha | `alpha=0.5` | `α=0.5` |
| 30 | R016 | Use \top for transpose | `A^T` | `A^\top` |
```

This action helps maintain consistent, high-quality documentation across all QuantEcon projects!