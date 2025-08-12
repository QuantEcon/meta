#!/usr/bin/env python3
"""
Example workflow trigger for testing.

This script simulates triggering the workflow with sample data.
"""

import json
import requests
import os
import argparse


def trigger_workflow_dispatch(repo, token, inputs):
    """Trigger workflow dispatch event."""
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    url = f"https://api.github.com/repos/{repo}/actions/workflows/lecture-translation-migration.yml/dispatches"
    
    data = {
        'ref': 'main',
        'inputs': inputs
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response


def main():
    parser = argparse.ArgumentParser(description='Test workflow trigger')
    parser.add_argument('--token', help='GitHub token (or use GITHUB_TOKEN env var)')
    parser.add_argument('--repo', default='QuantEcon/meta', help='Target repository')
    parser.add_argument('--source-repo', default='QuantEcon/lecture-python.myst', help='Source repository')
    parser.add_argument('--pr-number', type=int, default=1, help='PR number to test with')
    parser.add_argument('--target-repo', default='QuantEcon/lecture-python.zh-cn', help='Target repository')
    
    args = parser.parse_args()
    
    token = args.token or os.environ.get('GITHUB_TOKEN')
    if not token:
        print("Error: GitHub token required (use --token or GITHUB_TOKEN env var)")
        return 1
    
    inputs = {
        'source_repo': args.source_repo,
        'pr_number': str(args.pr_number),
        'target_repo': args.target_repo
    }
    
    print(f"Triggering workflow in {args.repo}")
    print(f"Inputs: {json.dumps(inputs, indent=2)}")
    
    try:
        response = trigger_workflow_dispatch(args.repo, token, inputs)
        
        if response.status_code == 204:
            print("✅ Workflow triggered successfully!")
        else:
            print(f"❌ Failed to trigger workflow: {response.status_code}")
            print(response.text)
            return 1
    
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())