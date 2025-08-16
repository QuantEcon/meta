#!/bin/bash
set -e

# Get inputs
GITHUB_TOKEN="${INPUT_GITHUB_TOKEN}"
ORGANIZATION="${INPUT_ORGANIZATION:-QuantEcon}"
OUTPUT_FORMAT="${INPUT_OUTPUT_FORMAT:-markdown}"
EXCLUDE_REPOS="${INPUT_EXCLUDE_REPOS:-}"

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

# Get repositories with recent activity using GitHub Search API
echo "Fetching repositories with recent activity for ${ORGANIZATION}..."

# Search for repositories with recent commits, issues, or PRs in the last week
WEEK_AGO_DATE=$(date -d "7 days ago" -u +"%Y-%m-%d")

# Use search API to find repos with recent activity
search_query="org:${ORGANIZATION} pushed:>${WEEK_AGO_DATE}"
search_response=$(curl -s -H "Authorization: token ${GITHUB_TOKEN}" \
                       -H "Accept: application/vnd.github.v3+json" \
                       "https://api.github.com/search/repositories?q=$(echo "$search_query" | sed 's/ /%20/g')&per_page=100")

repo_names=$(echo "$search_response" | jq -r '.items[]?.name // empty')

# If no repos found with recent commits, fall back to checking all org repos
# This ensures we don't miss repos that might have issues/PRs but no commits
if [ -z "$repo_names" ]; then
    echo "No repositories found with recent commits, checking all organization repositories..."
    repos_response=$(api_call "/orgs/${ORGANIZATION}/repos")
    repo_names=$(echo "$repos_response" | jq -r '.[].name // empty')
    
    if [ -z "$repo_names" ]; then
        echo "No repositories found or API call failed"
        exit 1
    fi
else
    echo "Found repositories with recent activity:"
    echo "$repo_names" | head -10  # Show first 10 for logging
fi

# Filter out excluded repositories if any are specified
if [ -n "$EXCLUDE_REPOS" ]; then
    echo "Excluding repositories: $EXCLUDE_REPOS"
    # Convert comma-separated list to array and filter out excluded repos
    IFS=',' read -ra exclude_array <<< "$EXCLUDE_REPOS"
    filtered_repos=""
    while IFS= read -r repo; do
        [ -z "$repo" ] && continue
        excluded=false
        for exclude_repo in "${exclude_array[@]}"; do
            # Trim whitespace and compare
            exclude_repo=$(echo "$exclude_repo" | xargs)
            if [ "$repo" = "$exclude_repo" ]; then
                excluded=true
                echo "Excluding repository: $repo"
                break
            fi
        done
        if [ "$excluded" = false ]; then
            if [ -z "$filtered_repos" ]; then
                filtered_repos="$repo"
            else
                filtered_repos="$filtered_repos"$'\n'"$repo"
            fi
        fi
    done <<< "$repo_names"
    repo_names="$filtered_repos"
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
        jq --arg since "$WEEK_AGO" 'if type == "array" then [.[] | select(.created_at >= $since and .pull_request == null)] | length else 0 end')
    
    # Count closed issues in the last week
    closed_issues=$(api_call "/repos/${ORGANIZATION}/${repo}/issues?state=closed" | \
        jq --arg since "$WEEK_AGO" 'if type == "array" then [.[] | select(.closed_at != null and .closed_at >= $since and .pull_request == null)] | length else 0 end')
    
    # Count merged PRs in the last week
    merged_prs=$(api_call "/repos/${ORGANIZATION}/${repo}/pulls?state=closed" | \
        jq --arg since "$WEEK_AGO" 'if type == "array" then [.[] | select(.merged_at != null and .merged_at >= $since)] | length else 0 end')
    
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