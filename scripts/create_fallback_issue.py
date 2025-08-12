#!/usr/bin/env python3
"""
Create fallback issue when translation PR cannot be created.

This script creates an issue in the target repository linking to the original PR
when automatic translation fails or when no translated files are found.
"""

import argparse
import os
import sys
import requests


def get_github_headers():
    """Get headers for GitHub API requests."""
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is required")
    
    return {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }


def get_pr_details(repo, pr_number):
    """Get details of a pull request."""
    headers = get_github_headers()
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.json()


def create_issue(repo, title, body, labels=None, assignees=None):
    """Create an issue in the repository."""
    headers = get_github_headers()
    url = f"https://api.github.com/repos/{repo}/issues"
    
    data = {
        'title': title,
        'body': body
    }
    
    if labels:
        data['labels'] = labels
    
    if assignees:
        data['assignees'] = assignees
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    
    return response.json()


def main():
    parser = argparse.ArgumentParser(description='Create fallback issue for translation updates')
    parser.add_argument('--source-repo', required=True, help='Source repository')
    parser.add_argument('--pr-number', required=True, type=int, help='Source PR number')
    parser.add_argument('--target-repo', required=True, help='Target repository')
    parser.add_argument('--reason', help='Reason for fallback (optional)')
    
    args = parser.parse_args()
    
    try:
        # Get PR details
        pr_details = get_pr_details(args.source_repo, args.pr_number)
        
        # Determine the reason for the fallback
        if args.reason == 'skipped':
            reason_text = "No translated lectures were found that needed updating."
        elif args.reason == 'failure':
            reason_text = "Automatic translation failed due to technical issues."
        else:
            reason_text = "Automatic translation could not be completed."
        
        # Create issue title and body
        issue_title = f"Manual translation review needed for {args.source_repo} PR #{args.pr_number}"
        
        issue_body = f"""## Manual Translation Review Required

A pull request in the English lecture repository requires manual review for potential translation updates.

### Source PR Details
- **Repository**: {args.source_repo}
- **PR Number**: #{args.pr_number}
- **Title**: {pr_details['title']}
- **Author**: @{pr_details['user']['login']}
- **URL**: {pr_details['html_url']}

### Reason for Manual Review
{reason_text}

### Action Required
Please review the changes in the source PR and determine if any translation updates are needed:

1. Review the modified files in the [source PR]({pr_details['html_url']})
2. Check if any of the modified lectures have been translated to Chinese
3. If translation updates are needed, create a new PR with the translated changes
4. If no updates are needed, close this issue

### Files Modified
The following files were modified in the source PR:
"""

        # Get the list of modified files
        headers = get_github_headers()
        files_url = f"https://api.github.com/repos/{args.source_repo}/pulls/{args.pr_number}/files"
        files_response = requests.get(files_url, headers=headers)
        files_response.raise_for_status()
        
        files = files_response.json()
        for file in files:
            if file['filename'].startswith('lectures/') and file['filename'].endswith('.md'):
                issue_body += f"\n- `{file['filename']}` ({file['status']})"
        
        issue_body += f"""

### Review Checklist
- [ ] Reviewed source PR changes
- [ ] Checked which lectures are translated
- [ ] Determined if translation updates are needed
- [ ] Created translation PR or closed this issue

@{os.environ.get('TRANSLATION_REVIEWER', 'nisha617')} please review this request.

---
*This issue was automatically created by the translation workflow.*"""
        
        # Create the issue
        issue = create_issue(
            args.target_repo,
            issue_title,
            issue_body,
            labels=['translation', 'manual-review'],
            assignees=[os.environ.get('TRANSLATION_REVIEWER', 'nisha617')]
        )
        
        print(f"Created issue: {issue['html_url']}")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()