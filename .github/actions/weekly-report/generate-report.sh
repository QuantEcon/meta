#!/bin/bash
set -e

# Get inputs
GITHUB_TOKEN="${INPUT_GITHUB_TOKEN}"
ORGANIZATION="${INPUT_ORGANIZATION:-QuantEcon}"
OUTPUT_FORMAT="${INPUT_OUTPUT_FORMAT:-markdown}"

# Date calculations for last week
WEEK_AGO=$(date -d "7 days ago" -u +"%Y-%m-%dT%H:%M:%SZ")
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "Generating weekly report for ${ORGANIZATION} organization"
echo "Period: ${WEEK_AGO} to ${NOW}"

# Function to make GitHub API calls
api_call() {
    local endpoint="$1"
    local page="${2:-1}"
    curl -s -H "Authorization: token ${GITHUB_TOKEN}" \
         -H "Accept: application/vnd.github.v3+json" \
         "https://api.github.com${endpoint}?page=${page}&per_page=100"
}

# Get all repositories in the organization
echo "Fetching repositories for ${ORGANIZATION}..."
repos_response=$(api_call "/orgs/${ORGANIZATION}/repos")
repo_names=$(echo "$repos_response" | jq -r '.[].name // empty')

if [ -z "$repo_names" ]; then
    echo "No repositories found or API call failed"
    exit 1
fi

# Initialize report variables
total_opened_issues=0
total_closed_issues=0
total_merged_prs=0
report_content=""

# Start building the report
if [ "$OUTPUT_FORMAT" = "markdown" ]; then
    report_content="# QuantEcon Weekly Report\n\n"
    report_content+="**Report Period:** $(date -d "$WEEK_AGO" '+%B %d, %Y') - $(date -d "$NOW" '+%B %d, %Y')\n\n"
    report_content+="## Summary\n\n"
    report_content+="| Repository | Opened Issues | Closed Issues | Merged PRs |\n"
    report_content+="|------------|---------------|---------------|------------|\n"
fi

# Process each repository
while IFS= read -r repo; do
    [ -z "$repo" ] && continue
    
    echo "Processing repository: $repo"
    
    # Count opened issues in the last week
    opened_issues=$(api_call "/repos/${ORGANIZATION}/${repo}/issues" | \
        jq --arg since "$WEEK_AGO" '[.[] | select(.created_at >= $since and .pull_request == null)] | length')
    
    # Count closed issues in the last week
    closed_issues=$(api_call "/repos/${ORGANIZATION}/${repo}/issues?state=closed" | \
        jq --arg since "$WEEK_AGO" '[.[] | select(.closed_at >= $since and .pull_request == null)] | length')
    
    # Count merged PRs in the last week
    merged_prs=$(api_call "/repos/${ORGANIZATION}/${repo}/pulls?state=closed" | \
        jq --arg since "$WEEK_AGO" '[.[] | select(.merged_at != null and .merged_at >= $since)] | length')
    
    # Handle null/empty values
    opened_issues=${opened_issues:-0}
    closed_issues=${closed_issues:-0}
    merged_prs=${merged_prs:-0}
    
    # Add to totals
    total_opened_issues=$((total_opened_issues + opened_issues))
    total_closed_issues=$((total_closed_issues + closed_issues))
    total_merged_prs=$((total_merged_prs + merged_prs))
    
    # Add to report if there's activity
    if [ $((opened_issues + closed_issues + merged_prs)) -gt 0 ]; then
        if [ "$OUTPUT_FORMAT" = "markdown" ]; then
            report_content+="| $repo | $opened_issues | $closed_issues | $merged_prs |\n"
        fi
    fi
    
done <<< "$repo_names"

# Add summary to report
if [ "$OUTPUT_FORMAT" = "markdown" ]; then
    report_content+="|**Total**|**$total_opened_issues**|**$total_closed_issues**|**$total_merged_prs**|\n\n"
    report_content+="## Details\n\n"
    report_content+="- **Total Repositories Checked:** $(echo "$repo_names" | wc -l)\n"
    report_content+="- **Total Issues Opened:** $total_opened_issues\n"
    report_content+="- **Total Issues Closed:** $total_closed_issues\n"
    report_content+="- **Total PRs Merged:** $total_merged_prs\n\n"
    report_content+="*Report generated on $(date) by QuantEcon Weekly Report Action*\n"
fi

# Create summary
summary="Week Summary: $total_opened_issues issues opened, $total_closed_issues issues closed, $total_merged_prs PRs merged"

# Save report to file
echo -e "$report_content" > weekly-report.md

# Set outputs
echo "report-content<<EOF" >> $GITHUB_OUTPUT
echo -e "$report_content" >> $GITHUB_OUTPUT
echo "EOF" >> $GITHUB_OUTPUT

echo "report-summary=$summary" >> $GITHUB_OUTPUT

echo "Weekly report generated successfully!"
echo "Summary: $summary"