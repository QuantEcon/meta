# QuantEcon Weekly Report Action

A GitHub Action that generates a weekly report summarizing activity across all repositories in the QuantEcon organization.

## Features

This action generates a report containing:
- Number of issues opened by repository (last 7 days)
- Number of issues closed by repository (last 7 days)  
- Number of PRs merged by repository (last 7 days)
- Summary totals across all repositories

## Usage

```yaml
- name: Generate weekly report
  uses: QuantEcon/meta/.github/actions/weekly-report@main
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    organization: 'QuantEcon'
    output-format: 'markdown'
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `github-token` | GitHub token with access to the organization | Yes | - |
| `organization` | GitHub organization name | No | `QuantEcon` |
| `output-format` | Output format (`markdown` or `json`) | No | `markdown` |

## Outputs

| Output | Description |
|--------|-------------|
| `report-content` | The full generated report content |
| `report-summary` | A brief summary of the report metrics |

## Permissions

The GitHub token must have read access to:
- Organization repositories
- Repository issues
- Repository pull requests

## Example Workflow

See the [weekly report workflow](../../workflows/weekly-report.yml) for a complete example that runs every Saturday and creates an issue with the report.

## Report Format

The generated markdown report includes:
- A summary table showing activity by repository
- Total counts across all repositories
- Report metadata (generation date, period covered)

Only repositories with activity in the reporting period are included in the detailed table.