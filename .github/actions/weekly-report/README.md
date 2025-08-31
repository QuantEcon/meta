# QuantEcon Weekly Report Action

A GitHub Action that generates a weekly report summarizing activity across all repositories in the QuantEcon organization.

## Features

This action generates a report containing:
- Number of issues opened by repository (last 7 days)
- Number of issues closed by repository (last 7 days)  
- Number of PRs merged by repository (last 7 days)
- Summary totals across all repositories

### Efficiency Features
- **Smart repository filtering**: Uses GitHub Search API to identify repositories with recent activity (commits in the last 7 days) before checking for issues and PRs
- **Fallback mechanism**: If no repositories are found with recent commits, falls back to checking all organization repositories to ensure complete coverage
- **Activity-based reporting**: Only includes repositories with actual activity in the generated report
- **Rate limit handling**: Automatically retries on rate limit errors with exponential backoff, and provides clear warnings when data is incomplete
- **Configurable delays**: Optional delays between API calls to reduce rate limit pressure
- **Comprehensive data collection**: Uses pagination to fetch all results, ensuring no PRs or issues are missed in repositories with high activity
- **Efficient PR counting**: Uses GitHub Search API for merged PR queries when possible, falling back to paginated API calls for reliability

## Usage

```yaml
- name: Generate weekly report
  uses: QuantEcon/meta/.github/actions/weekly-report@main
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    organization: 'QuantEcon'
    output-format: 'markdown'
    exclude-repos: 'lecture-python.notebooks,auto-updated-repo'
    api-delay: '1'  # Add 1 second delay between API calls to avoid rate limits
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `github-token` | GitHub token with access to the organization | Yes | - |
| `organization` | GitHub organization name | No | `QuantEcon` |
| `output-format` | Output format (`markdown` or `json`) | No | `markdown` |
| `exclude-repos` | Comma-separated list of repository names to exclude from the report | No | `''` |
| `api-delay` | Delay in seconds between API calls to avoid rate limits (0 = no delay) | No | `0` |

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
- Data completeness warnings if API calls failed due to rate limits or other errors
- Report metadata (generation date, period covered)

Only repositories with activity in the reporting period are included in the detailed table.

## Rate Limiting & Data Accuracy

GitHub's API has rate limits (5000 requests/hour for authenticated requests). For large organizations:

- **Monitor warnings**: The report will include warnings when rate limits are hit
- **Add delays**: Use the `api-delay` parameter to add delays between requests (e.g., `api-delay: '1'` for 1 second delays)
- **Run during off-peak**: Schedule reports during off-peak hours to avoid conflicts with other API usage
- **Incomplete data**: When rate limited, the report will show `0` for affected repositories and include a warning

### Data Accuracy Improvements

Recent enhancements ensure comprehensive data collection:

- **Pagination support**: All API calls now use pagination to fetch complete results, preventing undercounting in repositories with many issues or PRs
- **Dual API approach**: Uses GitHub Search API for efficient recent activity queries, with fallback to paginated list APIs for complete accuracy
- **Partial result handling**: When API limits are hit, the system returns partial results with clear warnings rather than failing completely

These improvements address potential counting discrepancies and ensure the weekly report provides accurate metrics.