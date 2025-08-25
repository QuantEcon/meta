# QuantEcon Style Guide Checker

An AI-enabled GitHub Action that checks lecture compliance with the QuantEcon Style Guide and provides intelligent suggestions for improvements.

## Features

- **Dual Operation Modes**: PR-triggered checks and scheduled complete reviews
- **Intelligent Analysis**: Uses rule-based checking with confidence levels
- **Automated Fixes**: High confidence suggestions can be auto-committed
- **Comprehensive Reporting**: Detailed tables with suggestions organized by confidence
- **Flexible Configuration**: Customizable paths, exclusions, and thresholds

## Usage

### PR Mode (Comment Trigger)

Add this to your workflow to trigger style checks when mentioned in PR comments:

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
      - name: Check style guide compliance
        uses: QuantEcon/meta/.github/actions/qe-style-check@main
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          lectures: 'lectures'
          mode: 'pr'
          confidence-threshold: 'high'
```

### Scheduled Mode

For comprehensive reviews of all lectures:

```yaml
name: Weekly Style Check
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM UTC
  workflow_dispatch:

jobs:
  style-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Complete style guide review
        uses: QuantEcon/meta/.github/actions/qe-style-check@main
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          lectures: 'lectures'
          mode: 'scheduled'
          create-individual-prs: 'true'
```

## Inputs

| Input | Description | Default | Required |
|-------|-------------|---------|----------|
| `style-guide` | Path or URL to the QuantEcon style guide document | `.github/copilot-qe-style-guide.md` | No |
| `lectures` | Path to directory containing lecture documents (Myst Markdown .md files) | `lectures` | No |
| `exclude-files` | Comma-separated list of file patterns to exclude (supports regex) | `` | No |
| `mode` | Operation mode: "pr" for pull request mode, "scheduled" for complete review | `pr` | No |
| `confidence-threshold` | Minimum confidence level for auto-commit (high, medium, low) | `high` | No |
| `create-individual-prs` | Create individual PRs per lecture in scheduled mode | `false` | No |
| `github-token` | GitHub token for API access | | Yes |

## Outputs

| Output | Description |
|--------|-------------|
| `suggestions-found` | Whether style suggestions were found (true/false) |
| `high-confidence-count` | Number of high confidence suggestions |
| `medium-confidence-count` | Number of medium confidence suggestions |
| `low-confidence-count` | Number of low confidence suggestions |
| `files-processed` | Number of files processed |
| `summary-report` | Summary report of suggestions |
| `detailed-report` | Detailed report with suggestions table |

## Style Rules Checked

The action checks compliance with the QuantEcon Style Guide including:

### Writing Conventions
- **R001-R005**: General writing principles, sentence structure, capitalization
- One sentence paragraphs
- Proper heading capitalization
- Clear and concise language

### Code Style  
- **R006-R015**: Python code formatting, variable naming, performance patterns
- Unicode Greek letters (α, β, γ, etc.)
- PEP8 compliance
- Modern timing patterns with `qe.Timer()`

### Mathematical Notation
- **R016-R021**: LaTeX formatting, equation numbering, symbol usage
- Proper transpose notation (`\top`)
- Standard matrix/vector conventions
- Built-in equation numbering

### Figure Guidelines
- **R022-R029**: Matplotlib best practices, captions, sizing
- No embedded titles in plots
- Proper line width settings
- Lowercase axis labels

## Confidence Levels

- **High Confidence**: Clear rule violations that can be automatically fixed (e.g., Greek letter usage, transpose notation)
- **Medium Confidence**: Style improvements that likely need adjustment (e.g., paragraph structure, timing patterns)  
- **Low Confidence**: Suggestions that may need human review (e.g., content organization, complex style choices)

## Examples

### Basic PR Check
```yaml
- name: Style Guide Check
  uses: QuantEcon/meta/.github/actions/qe-style-check@main
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    lectures: 'source/lectures'
    exclude-files: 'intro.md,references.md'
```

### Scheduled Review with Individual PRs
```yaml
- name: Weekly Style Review
  uses: QuantEcon/meta/.github/actions/qe-style-check@main
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    mode: 'scheduled'
    create-individual-prs: 'true'
    confidence-threshold: 'medium'
```

### Custom Style Guide
```yaml
- name: Style Check with Custom Guide
  uses: QuantEcon/meta/.github/actions/qe-style-check@main
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    style-guide: 'https://raw.githubusercontent.com/MyOrg/style/main/guide.md'
    lectures: 'content'
```

## Integration with Existing Workflows

This action integrates well with:
- **Documentation builds**: Run after successful builds to check style
- **PR workflows**: Automatic style validation on pull requests  
- **Release workflows**: Ensure style compliance before releases
- **Content reviews**: Regular maintenance of lecture quality

## Troubleshooting

### No Files Found
- Verify the `lectures` path exists and contains `.md` files
- Check `exclude-files` patterns aren't too broad
- Ensure the repository structure matches the configured paths

### Permission Issues
- Verify `github-token` has appropriate permissions
- For PR creation, ensure token has `contents: write` and `pull-requests: write`
- Check repository settings allow action to create PRs

### Style Guide Loading
- If using a URL, ensure it's publicly accessible
- For local files, verify the path is relative to repository root
- Check that the style guide follows the expected markdown format

## Contributing

To extend or modify the style checking rules:

1. Update the rule definitions in `style_checker.py`
2. Add corresponding tests in the test suite
3. Update documentation with new rule descriptions
4. Ensure confidence levels are appropriately assigned

See the [contribution guidelines](../../../CONTRIBUTING.md) for more details.