#!/bin/bash
set -e

echo "DEBUG: Starting weekly report generation"
echo "DEBUG: Environment check - GITHUB_OUTPUT: ${GITHUB_OUTPUT:-NOT_SET}"

# Get inputs
GITHUB_TOKEN="${INPUT_GITHUB_TOKEN}"
ORGANIZATION="${INPUT_ORGANIZATION:-QuantEcon}"
OUTPUT_FORMAT="${INPUT_OUTPUT_FORMAT:-markdown}"
EXCLUDE_REPOS="${INPUT_EXCLUDE_REPOS:-}"
API_DELAY="${INPUT_API_DELAY:-0}"  # Optional delay between API calls in seconds

echo "DEBUG: Inputs - ORG: $ORGANIZATION, FORMAT: $OUTPUT_FORMAT, EXCLUDE: $EXCLUDE_REPOS"

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
        # Construct URL with proper query parameter handling
        local url="https://api.github.com${endpoint}"
        if [[ "$endpoint" == *"?"* ]]; then
            url="${url}&page=${page}&per_page=100"
        else
            url="${url}?page=${page}&per_page=100"
        fi
        
        local response=$(curl -s -w "\n%{http_code}" -H "Authorization: token ${GITHUB_TOKEN}" \
                            -H "Accept: application/vnd.github.v3+json" \
                            "$url")
        
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

# Function to get all pages of an API endpoint and combine results
api_call_all_pages() {
    local endpoint="$1"
    local combined_results="[]"
    local page=1
    local max_pages=10  # Safety limit to prevent infinite loops
    
    echo "Fetching all pages for endpoint: $endpoint" >&2
    
    while [ $page -le $max_pages ]; do
        echo "Fetching page $page..." >&2
        local response=$(api_call "$endpoint" "$page")
        local exit_code=$?
        
        # If API call failed, return what we have so far
        if [ $exit_code -ne 0 ]; then
            echo "API call failed on page $page, returning partial results" >&2
            echo "$combined_results"
            return $exit_code
        fi
        
        # Check if response contains an error
        if echo "$response" | jq -e '.error' >/dev/null 2>&1; then
            echo "Error response on page $page, returning partial results" >&2
            echo "$combined_results"
            return 1
        fi
        
        # Get the page results and ensure it's an array
        local page_results
        if echo "$response" | jq -e 'type == "array"' >/dev/null 2>&1; then
            page_results="$response"
        else
            echo "Response is not an array on page $page, stopping pagination" >&2
            break
        fi
        
        # If this page is empty, we've reached the end
        local page_length=$(echo "$page_results" | jq 'length')
        if [ "$page_length" -eq 0 ]; then
            echo "No more results on page $page, stopping pagination" >&2
            break
        fi
        
        # Combine results using jq array concatenation
        combined_results=$(jq -n --argjson current "$combined_results" --argjson new "$page_results" '$current + $new')
        
        # If we got less than 100 results, this is likely the last page, but let's check the next page to be sure
        if [ "$page_length" -lt 100 ]; then
            echo "Got less than 100 results on page $page, checking if this is the last page" >&2
            # For now, let's continue to the next page to be absolutely sure
            # The next iteration will get an empty page and break naturally
        fi
        
        page=$((page + 1))
    done
    
    echo "Fetched $(echo "$combined_results" | jq 'length') total results across $((page - 1)) pages" >&2
    echo "$combined_results"
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
total_current_issues=0
total_opened_issues=0
total_closed_issues=0
total_merged_prs=0
failed_repos=0
rate_limited_repos=0
report_content=""

# Start building the report
if [ "$OUTPUT_FORMAT" = "markdown" ]; then
    report_content="# QuantEcon Weekly Report

**Report Period:** $(date -d "$WEEK_AGO" '+%B %d, %Y') - $(date -d "$NOW" '+%B %d, %Y')

## Summary

| Repository | Total Current Issues | Opened Issues | Closed Issues | Merged PRs |
|------------|---------------------|---------------|---------------|------------|"
    echo "DEBUG: Initial report content set, length: ${#report_content}"
fi

# Process each repository
repo_count=0
while IFS= read -r repo; do
    [ -z "$repo" ] && continue
    repo_count=$((repo_count + 1))
    
    echo "Processing repository: $repo"
    
    # Count total current open issues (using pagination to get all results)
    current_issues_response=$(api_call_all_pages "/repos/${ORGANIZATION}/${repo}/issues?state=open")
    if [ $? -eq 0 ]; then
        current_issues=$(echo "$current_issues_response" | jq 'if type == "array" then [.[] | select(.pull_request == null)] | length else 0 end')
    else
        current_issues=0
        if echo "$current_issues_response" | jq -e '.error' 2>/dev/null | grep -q "rate_limit"; then
            rate_limited_repos=$((rate_limited_repos + 1))
        else
            failed_repos=$((failed_repos + 1))
        fi
    fi
    
    # Count opened issues in the last week (using pagination to get all results)
    opened_response=$(api_call_all_pages "/repos/${ORGANIZATION}/${repo}/issues")
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
    
    # Count closed issues in the last week (using pagination to get all results)
    closed_response=$(api_call_all_pages "/repos/${ORGANIZATION}/${repo}/issues?state=closed")
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
    
    # Count merged PRs in the last week using GitHub Search API (more efficient)
    # Format dates for search query (GitHub search uses different date format)
    SEARCH_WEEK_AGO=$(date -d "$WEEK_AGO" +"%Y-%m-%d")
    search_query="repo:${ORGANIZATION}/${repo} is:pr is:merged merged:>=${SEARCH_WEEK_AGO}"
    
    # Try search API first (more efficient for recent items)
    search_response=$(curl -s -H "Authorization: token ${GITHUB_TOKEN}" \
                           -H "Accept: application/vnd.github.v3+json" \
                           "https://api.github.com/search/issues?q=$(echo "$search_query" | sed 's/ /%20/g')&per_page=100")
    
    if echo "$search_response" | jq -e '.total_count' >/dev/null 2>&1; then
        # Search API worked, use its results
        merged_prs=$(echo "$search_response" | jq '.total_count // 0')
        echo "Used search API for $repo: found $merged_prs merged PRs" >&2
    else
        # Fall back to paginated pulls API
        echo "Search API failed for $repo, falling back to pulls API" >&2
        prs_response=$(api_call_all_pages "/repos/${ORGANIZATION}/${repo}/pulls?state=closed")
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
    fi
    
    # Handle null/empty values
    current_issues=${current_issues:-0}
    opened_issues=${opened_issues:-0}
    closed_issues=${closed_issues:-0}
    merged_prs=${merged_prs:-0}
    
    # Add to totals
    total_current_issues=$((total_current_issues + current_issues))
    total_opened_issues=$((total_opened_issues + opened_issues))
    total_closed_issues=$((total_closed_issues + closed_issues))
    total_merged_prs=$((total_merged_prs + merged_prs))
    
    # Add to report if there's activity or current open issues
    if [ $((current_issues + opened_issues + closed_issues + merged_prs)) -gt 0 ]; then
        if [ "$OUTPUT_FORMAT" = "markdown" ]; then
            report_content="${report_content}
| $repo | $current_issues | $opened_issues | $closed_issues | $merged_prs |"
        fi
    fi
    
done <<< "$repo_names"

echo "DEBUG: Processed $repo_count repositories"
echo "DEBUG: Final report content length: ${#report_content}"

# Add summary to report
if [ "$OUTPUT_FORMAT" = "markdown" ]; then
    report_content="${report_content}
|**Total**|**$total_current_issues**|**$total_opened_issues**|**$total_closed_issues**|**$total_merged_prs**|

## Details

- **Total Repositories Checked:** $(echo "$repo_names" | wc -l)
- **Total Current Open Issues:** $total_current_issues
- **Total Issues Opened:** $total_opened_issues
- **Total Issues Closed:** $total_closed_issues
- **Total PRs Merged:** $total_merged_prs"
    
    # Add warnings about incomplete data if any API calls failed
    if [ $rate_limited_repos -gt 0 ] || [ $failed_repos -gt 0 ]; then
        report_content="${report_content}

### ⚠️ Data Completeness Warnings
"
        if [ $rate_limited_repos -gt 0 ]; then
            report_content="${report_content}
- **Rate Limited:** $rate_limited_repos API calls hit rate limits. Data may be incomplete."
        fi
        if [ $failed_repos -gt 0 ]; then
            report_content="${report_content}
- **Failed Requests:** $failed_repos API calls failed. Data may be incomplete."
        fi
        report_content="${report_content}

*Consider adding API delays or running during off-peak hours to avoid rate limits.*"
    fi
    
    report_content="${report_content}

*Report generated on $(date) by QuantEcon Weekly Report Action*"
fi

# Create summary
summary="Week Summary: $total_current_issues current open issues, $total_opened_issues issues opened, $total_closed_issues issues closed, $total_merged_prs PRs merged"

# Save report to file
echo "$report_content" > weekly-report.md

# Debug: Check if GITHUB_OUTPUT is set and accessible
echo "DEBUG: GITHUB_OUTPUT environment variable: ${GITHUB_OUTPUT:-NOT_SET}"
echo "DEBUG: Report content length: ${#report_content}"
echo "DEBUG: Summary: $summary"

# Set outputs
if [ -n "$GITHUB_OUTPUT" ]; then
    echo "DEBUG: Writing to GITHUB_OUTPUT file"
    echo "DEBUG: Content preview (first 100 chars): ${report_content:0:100}"
    echo "DEBUG: Summary preview: $summary"
    
    # Use a unique delimiter to avoid conflicts with content
    delimiter="QUANTECON_REPORT_END_$(date +%s)"
    echo "report-content<<${delimiter}" >> "$GITHUB_OUTPUT"
    echo "$report_content" >> "$GITHUB_OUTPUT"
    echo "${delimiter}" >> "$GITHUB_OUTPUT"
    
    echo "report-summary=$summary" >> "$GITHUB_OUTPUT"
    
    echo "DEBUG: Outputs written to GITHUB_OUTPUT"
    echo "DEBUG: GITHUB_OUTPUT file size: $(wc -c < "$GITHUB_OUTPUT")"
else
    echo "ERROR: GITHUB_OUTPUT environment variable not set!"
fi

echo "Weekly report generated successfully!"
echo "Summary: $summary"