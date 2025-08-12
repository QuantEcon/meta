#!/usr/bin/env python3
"""
Create translation PR for lecture files.

This script:
1. Gets the changes from the source PR
2. Translates the content from English to Chinese
3. Creates a new PR in the target repository with the translated changes
"""

import argparse
import json
import os
import sys
import requests
import base64
import openai
from pathlib import Path
import re


def get_github_headers():
    """Get headers for GitHub API requests."""
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is required")
    
    return {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }


def setup_openai():
    """Setup OpenAI client for translation."""
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    openai.api_key = api_key


def translate_content(content, source_lang='English', target_lang='Chinese'):
    """Translate content using OpenAI."""
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system", 
                    "content": f"""You are a professional translator specializing in academic and technical content, particularly economics and programming tutorials. 

Translate the following content from {source_lang} to {target_lang}. 

IMPORTANT RULES:
1. Preserve ALL markdown formatting exactly (headers, code blocks, math formulas, links, etc.)
2. Do NOT translate:
   - Code snippets and programming code
   - Mathematical formulas and equations
   - Variable names and function names
   - URLs and file paths
   - Technical terms that are commonly used in English in Chinese academic contexts
3. DO translate:
   - Regular text and explanations
   - Comments in code (but preserve the comment syntax)
   - Figure captions and labels
4. Maintain the exact same structure and formatting
5. Use simplified Chinese characters
6. Keep the same line breaks and spacing

The content is from an economics/programming lecture series, so maintain appropriate academic tone."""
                },
                {
                    "role": "user",
                    "content": content
                }
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Translation error: {e}")
        raise


def get_file_content(repo, file_path, ref='main'):
    """Get content of a file from GitHub repository."""
    headers = get_github_headers()
    url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
    
    params = {'ref': ref}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    content_data = response.json()
    content = base64.b64decode(content_data['content']).decode('utf-8')
    
    return content, content_data['sha']


def update_file_content(repo, file_path, content, commit_message, sha, branch='main'):
    """Update file content in GitHub repository."""
    headers = get_github_headers()
    url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
    
    data = {
        'message': commit_message,
        'content': base64.b64encode(content.encode('utf-8')).decode('utf-8'),
        'sha': sha,
        'branch': branch
    }
    
    response = requests.put(url, headers=headers, json=data)
    response.raise_for_status()
    
    return response.json()


def create_branch(repo, branch_name, base_branch='main'):
    """Create a new branch in the repository."""
    headers = get_github_headers()
    
    # Get the SHA of the base branch
    ref_url = f"https://api.github.com/repos/{repo}/git/refs/heads/{base_branch}"
    response = requests.get(ref_url, headers=headers)
    response.raise_for_status()
    base_sha = response.json()['object']['sha']
    
    # Create new branch
    create_url = f"https://api.github.com/repos/{repo}/git/refs"
    data = {
        'ref': f'refs/heads/{branch_name}',
        'sha': base_sha
    }
    
    response = requests.post(create_url, headers=headers, json=data)
    if response.status_code == 422:
        # Branch already exists
        print(f"Branch {branch_name} already exists")
        return
    
    response.raise_for_status()


def create_pull_request(repo, head_branch, base_branch, title, body):
    """Create a pull request in the repository."""
    headers = get_github_headers()
    url = f"https://api.github.com/repos/{repo}/pulls"
    
    data = {
        'title': title,
        'head': head_branch,
        'base': base_branch,
        'body': body
    }
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    
    return response.json()


def apply_diff_translation(original_content, patch, translated_patch):
    """Apply translated changes to the original content."""
    # This is a simplified approach - in a real implementation,
    # you'd want more sophisticated diff parsing and application
    
    # For now, we'll use a simple line-by-line replacement approach
    lines = original_content.split('\n')
    
    # Parse the patch to understand what changed
    patch_lines = patch.split('\n')
    
    # This is a simplified implementation
    # A more robust version would properly parse git diffs
    
    return translated_patch


def get_pr_details(repo, pr_number):
    """Get details of a pull request."""
    headers = get_github_headers()
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.json()


def main():
    parser = argparse.ArgumentParser(description='Create translation PR for lecture files')
    parser.add_argument('--source-repo', required=True, help='Source repository')
    parser.add_argument('--pr-number', required=True, type=int, help='Source PR number')
    parser.add_argument('--target-repo', required=True, help='Target repository')
    parser.add_argument('--translated-files', required=True, help='JSON string of files to translate')
    
    args = parser.parse_args()
    
    try:
        setup_openai()
        
        # Parse the translated files
        translated_files = json.loads(args.translated_files)
        
        if not translated_files:
            print("No files to process")
            return
        
        # Get PR details for context
        pr_details = get_pr_details(args.source_repo, args.pr_number)
        
        # Create a branch for the translation
        branch_name = f"translation-update-pr-{args.pr_number}"
        print(f"Creating branch: {branch_name}")
        create_branch(args.target_repo, branch_name)
        
        updated_files = []
        
        for file_info in translated_files:
            print(f"Processing file: {file_info['lecture_name']}")
            
            source_file = file_info['filename']
            target_file = f"lectures/{file_info['lecture_name']}.md"
            
            try:
                # Get current content from source repository
                source_content, _ = get_file_content(args.source_repo, source_file)
                
                # Get current content from target repository
                target_content, target_sha = get_file_content(args.target_repo, target_file)
                
                # For simplicity, translate the entire file content
                # In a more sophisticated implementation, you'd translate only the diff
                print(f"Translating content for {file_info['lecture_name']}")
                translated_content = translate_content(source_content)
                
                # Update the file in the target repository
                commit_message = f"Update {file_info['lecture_name']} translation from PR #{args.pr_number}"
                
                update_file_content(
                    args.target_repo,
                    target_file,
                    translated_content,
                    commit_message,
                    target_sha,
                    branch_name
                )
                
                updated_files.append(file_info['lecture_name'])
                print(f"Updated {target_file}")
                
            except Exception as e:
                print(f"Error processing {file_info['lecture_name']}: {e}")
                continue
        
        if updated_files:
            # Create pull request
            pr_title = f"Translation update from {args.source_repo} PR #{args.pr_number}"
            pr_body = f"""## Automated Translation Update

This PR contains translation updates for the following lectures based on changes in [{args.source_repo} PR #{args.pr_number}]({pr_details['html_url']}):

{chr(10).join(f'- {file}' for file in updated_files)}

### Original PR Details
- **Title**: {pr_details['title']}
- **Author**: @{pr_details['user']['login']}
- **URL**: {pr_details['html_url']}

### Review Instructions
Please review the translated content to ensure:
1. Technical accuracy is maintained
2. Chinese terminology is appropriate
3. Code examples and formulas are preserved correctly
4. Formatting and structure are consistent

@{os.environ.get('TRANSLATION_REVIEWER', 'nisha617')} please review this translation.

---
*This PR was automatically generated by the translation workflow.*"""
            
            pr = create_pull_request(
                args.target_repo,
                branch_name,
                'main',
                pr_title,
                pr_body
            )
            
            print(f"Created PR: {pr['html_url']}")
        else:
            print("No files were successfully updated")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()