#!/bin/bash
set -e

# Get inputs
GITHUB_TOKEN="${INPUT_GITHUB_TOKEN}"
ORGANIZATION="${INPUT_ORGANIZATION:-QuantEcon}"
OUTPUT_FORMAT="${INPUT_OUTPUT_FORMAT:-markdown}"
EXCLUDE_REPOS="${INPUT_EXCLUDE_REPOS:-}"
API_DELAY="${INPUT_API_DELAY:-0}"  # Optional delay between API calls in seconds

# Date calculations for last week
WEEK_AGO=$(date -d "7 days ago" -u +"%Y-%m-%dT%H:%M:%SZ")
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "Generating weekly report for ${ORGANIZATION} organization"
echo "Period: ${WEEK_AGO} to ${NOW}"

# Function to make GitHub API calls with rate limit handling
api_call() {
    local endpoint="$1"
    local page="${2:-1}"
    local max_retries=3
    local retry_count=0
    local delay="${API_DELAY:-0}"
    
    # Add delay between requests if specified
    if [ "$delay" -gt 0 ]; then
        sleep "$delay"
    fi
    
    while [ $retry_count -lt $max_retries ]; do
        local response=$(curl -s -w "\n%{http_code}" -H "Authorization: token ${GITHUB_TOKEN}" \
                            -H "Accept: application/vnd.github.v3+json" \
                            "https://api.github.com${endpoint}?page=${page}&per_page=100")
        
        local http_code=$(echo "$response" | tail -n1)
        local body=$(echo "$response" | head -n -1)
        
        case "$http_code" in
            200)
                echo "$body"
                return 0
                ;;
            403)
                # Check if it's a rate limit error
                if echo "$body" | jq -e '.message' 2>/dev/null | grep -q "rate limit"; then
                    retry_count=$((retry_count + 1))
                    if [ $retry_count -lt $max_retries ]; then
                        local wait_time=$((retry_count * retry_count * 60))  # Exponential backoff: 1min, 4min, 9min
                        echo "Rate limit exceeded for $endpoint. Waiting ${wait_time}s before retry $retry_count/$max_retries..." >&2
                        sleep "$wait_time"
                        continue
                    else
                        echo "Rate limit exceeded for $endpoint after $max_retries retries. Data will be incomplete." >&2
                        echo '{"error": "rate_limit_exceeded", "message": "API rate limit exceeded"}'
                        return 1
                    fi
                else
                    echo "Access forbidden for $endpoint: $body" >&2
                    echo '{"error": "forbidden", "message": "Access forbidden"}'
                    return 1
                fi
                ;;
            404)
                echo "Repository not found: $endpoint" >&2
                echo '{"error": "not_found", "message": "Repository not found"}'
                return 1
                ;;
            *)
                echo "API call failed for $endpoint with status $http_code: $body" >&2
                echo '{"error": "api_error", "message": "API call failed"}'
                return 1
                ;;
        esac
    done
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
failed_repos=0
rate_limited_repos=0
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
    opened_response=$(api_call "/repos/${ORGANIZATION}/${repo}/issues")
    if [ $? -eq 0 ]; then
        opened_issues=$(echo "$opened_response" | jq --arg since "$WEEK_AGO" 'if type == "array" then [.[] | select(.created_at >= $since and .pull_request == null)] | length else 0 end')
    else
        opened_issues=0
        if echo "$opened_response" | jq -e '.error' 2>/dev/null | grep -q "rate_limit"; then
            rate_limited_repos=$((rate_limited_repos + 1))
        else
            failed_repos=$((failed_repos + 1))
        fi
    fi
    
    # Count closed issues in the last week
    closed_response=$(api_call "/repos/${ORGANIZATION}/${repo}/issues?state=closed")
    if [ $? -eq 0 ]; then
        closed_issues=$(echo "$closed_response" | jq --arg since "$WEEK_AGO" 'if type == "array" then [.[] | select(.closed_at != null and .closed_at >= $since and .pull_request == null)] | length else 0 end')
    else
        closed_issues=0
        if echo "$closed_response" | jq -e '.error' 2>/dev/null | grep -q "rate_limit"; then
            rate_limited_repos=$((rate_limited_repos + 1))
        else
            failed_repos=$((failed_repos + 1))
        fi
    fi
    
    # Count merged PRs in the last week
    prs_response=$(api_call "/repos/${ORGANIZATION}/${repo}/pulls?state=closed")
    if [ $? -eq 0 ]; then
        merged_prs=$(echo "$prs_response" | jq --arg since "$WEEK_AGO" 'if type == "array" then [.[] | select(.merged_at != null and .merged_at >= $since)] | length else 0 end')
    else
        merged_prs=0
        if echo "$prs_response" | jq -e '.error' 2>/dev/null | grep -q "rate_limit"; then
            rate_limited_repos=$((rate_limited_repos + 1))
        else
            failed_repos=$((failed_repos + 1))
        fi
    fi
    
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
    report_content+="- **Total PRs Merged:** $total_merged_prs\n"
    
    # Add warnings about incomplete data if any API calls failed
    if [ $rate_limited_repos -gt 0 ] || [ $failed_repos -gt 0 ]; then
        report_content+="\n### ⚠️ Data Completeness Warnings\n\n"
        if [ $rate_limited_repos -gt 0 ]; then
            report_content+="- **Rate Limited:** $rate_limited_repos API calls hit rate limits. Data may be incomplete.\n"
        fi
        if [ $failed_repos -gt 0 ]; then
            report_content+="- **Failed Requests:** $failed_repos API calls failed. Data may be incomplete.\n"
        fi
        report_content+="\n*Consider adding API delays or running during off-peak hours to avoid rate limits.*\n"
    fi
    
    report_content+="\n"
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