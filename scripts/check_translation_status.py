#!/usr/bin/env python3
"""
Check translation status for lecture files.

This script:
1. Gets the list of modified files from a PR in the source repository
2. Checks which of these files have been translated in the target repository
3. Outputs the list of translated files that need updates
"""

import argparse
import json
import os
import sys
import requests
import yaml
from pathlib import Path


def get_github_headers():
    """Get headers for GitHub API requests."""
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is required")
    
    return {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }


def get_pr_files(source_repo, pr_number):
    """Get list of files modified in a PR."""
    headers = get_github_headers()
    url = f"https://api.github.com/repos/{source_repo}/pulls/{pr_number}/files"
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    files = response.json()
    
    # Filter for lecture files (markdown files in lectures directory)
    lecture_files = []
    for file in files:
        filename = file['filename']
        if filename.startswith('lectures/') and filename.endswith('.md'):
            # Extract just the lecture name without path and extension
            lecture_name = Path(filename).stem
            if lecture_name not in ['intro', 'status', 'troubleshooting', 'zreferences']:
                lecture_files.append({
                    'filename': filename,
                    'lecture_name': lecture_name,
                    'status': file['status'],
                    'patch': file.get('patch', '')
                })
    
    return lecture_files


def get_translated_lectures(target_repo):
    """Get list of lectures that have been translated in the target repository."""
    headers = get_github_headers()
    
    # Get the _toc.yml file to see which lectures are translated
    url = f"https://api.github.com/repos/{target_repo}/contents/lectures/_toc.yml"
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    content = response.json()
    
    # Decode the base64 content
    import base64
    toc_content = base64.b64decode(content['content']).decode('utf-8')
    
    # Parse YAML
    toc_data = yaml.safe_load(toc_content)
    
    # Extract lecture names from the table of contents
    translated_lectures = set()
    
    def extract_files_from_chapters(chapters):
        files = []
        for chapter in chapters:
            if 'file' in chapter:
                files.append(chapter['file'])
            if 'sections' in chapter:
                files.extend(extract_files_from_chapters(chapter['sections']))
        return files
    
    # Extract from parts
    if 'parts' in toc_data:
        for part in toc_data['parts']:
            if 'chapters' in part:
                translated_lectures.update(extract_files_from_chapters(part['chapters']))
    
    # Extract from chapters at root level
    if 'chapters' in toc_data:
        translated_lectures.update(extract_files_from_chapters(toc_data['chapters']))
    
    return translated_lectures


def main():
    parser = argparse.ArgumentParser(description='Check translation status for lecture files')
    parser.add_argument('--source-repo', required=True, help='Source repository (e.g., QuantEcon/lecture-python.myst)')
    parser.add_argument('--pr-number', required=True, type=int, help='PR number in source repository')
    parser.add_argument('--target-repo', required=True, help='Target repository (e.g., QuantEcon/lecture-python.zh-cn)')
    
    args = parser.parse_args()
    
    try:
        # Get modified files from PR
        print(f"Getting modified files from PR #{args.pr_number} in {args.source_repo}")
        modified_files = get_pr_files(args.source_repo, args.pr_number)
        
        if not modified_files:
            print("No lecture files found in PR")
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                f.write(f"should-proceed=false\n")
                f.write(f"translated-files={json.dumps([])}\n")
            return
        
        print(f"Found {len(modified_files)} modified lecture files")
        
        # Get translated lectures from target repository
        print(f"Getting translated lectures from {args.target_repo}")
        translated_lectures = get_translated_lectures(args.target_repo)
        
        print(f"Found {len(translated_lectures)} translated lectures")
        
        # Find intersection - files that are modified AND translated
        translated_files = []
        for file_info in modified_files:
            if file_info['lecture_name'] in translated_lectures:
                translated_files.append(file_info)
                print(f"Found translated lecture to update: {file_info['lecture_name']}")
        
        if translated_files:
            print(f"Will process {len(translated_files)} translated lecture files")
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                f.write(f"should-proceed=true\n")
                f.write(f"translated-files={json.dumps(translated_files)}\n")
        else:
            print("No translated lectures found that need updating")
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                f.write(f"should-proceed=false\n")
                f.write(f"translated-files={json.dumps([])}\n")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()