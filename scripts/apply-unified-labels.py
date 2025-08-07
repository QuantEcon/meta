#!/usr/bin/env python3
"""
Apply unified GitHub labels to QuantEcon lecture repositories.

This script helps implement the unified labeling system across all
QuantEcon lecture repositories by creating the required labels.

Requirements:
    pip install requests

Usage:
    python apply-unified-labels.py --token YOUR_GITHUB_TOKEN --org QuantEcon --dry-run
    python apply-unified-labels.py --token YOUR_GITHUB_TOKEN --org QuantEcon --repo lecture-python-intro
"""

import argparse
import json
import requests
import sys
from typing import Dict, List, Optional

# Unified label definitions
UNIFIED_LABELS = {
    # Issue Types
    "bug": {
        "color": "d73a4a",
        "description": "Something isn't working correctly"
    },
    "enhancement": {
        "color": "a2eeef", 
        "description": "New feature or improvement request"
    },
    "documentation": {
        "color": "0075ca",
        "description": "Improvements or additions to documentation"
    },
    "question": {
        "color": "d876e3",
        "description": "Further information is requested"
    },
    "maintenance": {
        "color": "fef2c0",
        "description": "Repository maintenance tasks"
    },
    
    # Priority
    "priority: critical": {
        "color": "b60205",
        "description": "Critical issues that break functionality"
    },
    "priority: high": {
        "color": "d93f0b", 
        "description": "High priority issues"
    },
    "priority: medium": {
        "color": "fbca04",
        "description": "Medium priority issues"
    },
    "priority: low": {
        "color": "0e8a16",
        "description": "Low priority issues"
    },
    
    # Status
    "status: ready": {
        "color": "23B685",
        "description": "Ready for implementation/review"
    },
    "status: in-progress": {
        "color": "fbca04",
        "description": "Currently being worked on"
    },
    "status: blocked": {
        "color": "e11d21",
        "description": "Blocked by external dependencies"
    },
    "status: needs-review": {
        "color": "0052cc",
        "description": "Awaiting code/content review"
    },
    "status: testing": {
        "color": "10947B",
        "description": "Under testing or quality assurance"
    },
    
    # Automation
    "automated issue": {
        "color": "ededed",
        "description": "Created by automated processes"
    },
    "dependencies": {
        "color": "0366d6",
        "description": "Dependency updates and management"
    },
    "github_actions": {
        "color": "000000",
        "description": "GitHub Actions workflows and CI/CD"
    },
    "linkchecker": {
        "color": "ededed",
        "description": "Link validation reports"
    },
    "report": {
        "color": "ededed",
        "description": "Automated reports and analytics"
    },
    
    # Special Categories  
    "good first issue": {
        "color": "7057ff",
        "description": "Good for newcomers"
    },
    "help wanted": {
        "color": "008672",
        "description": "Extra attention is needed"
    },
    "duplicate": {
        "color": "cfd3d7",
        "description": "Duplicate of another issue"
    },
    "invalid": {
        "color": "e4e669", 
        "description": "Invalid issue or request"
    },
    "wontfix": {
        "color": "ffffff",
        "description": "Will not be fixed/implemented"
    }
}

# Repository-specific labels
REPO_SPECIFIC_LABELS = {
    "content": {
        "content: intro": {
            "color": "c5def5",
            "description": "Python intro lecture series",
            "repos": ["lecture-python-intro"]
        },
        "content: intermediate": {
            "color": "bfd4f2", 
            "description": "Intermediate Python lectures",
            "repos": ["lecture-python.myst", "continuous_time_mcs"]
        },
        "content: advanced": {
            "color": "b8d4ff",
            "description": "Advanced Python lectures", 
            "repos": ["lecture-python-advanced.myst"]
        },
        "content: jax": {
            "color": "5319e7",
            "description": "JAX-based lectures",
            "repos": ["lecture-jax"]
        },
        "content: programming": {
            "color": "c7def8",
            "description": "Programming fundamentals",
            "repos": ["lecture-python-programming"]
        }
    },
    "components": {
        "component: build": {
            "color": "1d76db",
            "description": "Build system and compilation"
        },
        "component: infrastructure": {
            "color": "0052cc", 
            "description": "CI/CD, workflows, deployment"
        },
        "component: content": {
            "color": "006b75",
            "description": "Lecture content and materials"
        },
        "component: exercises": {
            "color": "0e8a16",
            "description": "Exercises and solutions"
        }
    },
    "format": {
        "format: myst": {
            "color": "79e0dc",
            "description": "MyST markdown format",
            "repos": ["lecture-python-intro", "lecture-python.myst", 
                     "lecture-python-advanced.myst", "lecture-jax", "continuous_time_mcs"]
        },
        "format: rst": {
            "color": "c7def8", 
            "description": "reStructuredText format",
            "repos": ["lecture-python-programming"]
        },
        "migration": {
            "color": "79e0dc",
            "description": "Content migration tasks"
        }
    }
}

TARGET_REPOS = [
    "lecture-python-programming",
    "lecture-python-intro", 
    "lecture-python.myst",
    "lecture-python-advanced.myst",
    "lecture-jax",
    "continuous_time_mcs"
]

class GitHubLabelManager:
    def __init__(self, token: str, org: str):
        self.token = token
        self.org = org
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        })
    
    def get_existing_labels(self, repo: str) -> List[Dict]:
        """Get existing labels for a repository."""
        url = f"https://api.github.com/repos/{self.org}/{repo}/labels"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def create_label(self, repo: str, name: str, color: str, description: str, dry_run: bool = False) -> bool:
        """Create a new label in the repository."""
        if dry_run:
            print(f"[DRY RUN] Would create label '{name}' in {repo}")
            return True
            
        url = f"https://api.github.com/repos/{self.org}/{repo}/labels"
        data = {
            "name": name,
            "color": color,
            "description": description
        }
        
        response = self.session.post(url, json=data)
        if response.status_code == 201:
            print(f"✓ Created label '{name}' in {repo}")
            return True
        elif response.status_code == 422:
            # Label already exists, try to update it
            return self.update_label(repo, name, color, description, dry_run)
        else:
            print(f"✗ Failed to create label '{name}' in {repo}: {response.status_code}")
            return False
    
    def update_label(self, repo: str, name: str, color: str, description: str, dry_run: bool = False) -> bool:
        """Update an existing label."""
        if dry_run:
            print(f"[DRY RUN] Would update label '{name}' in {repo}")
            return True
            
        url = f"https://api.github.com/repos/{self.org}/{repo}/labels/{name}"
        data = {
            "name": name,
            "color": color, 
            "description": description
        }
        
        response = self.session.patch(url, json=data)
        if response.status_code == 200:
            print(f"↻ Updated label '{name}' in {repo}")
            return True
        else:
            print(f"✗ Failed to update label '{name}' in {repo}: {response.status_code}")
            return False
    
    def apply_labels_to_repo(self, repo: str, dry_run: bool = False) -> bool:
        """Apply unified labels to a specific repository."""
        print(f"\n--- Applying labels to {repo} ---")
        
        if dry_run:
            print("[DRY RUN MODE - No changes will be made]")
        
        success = True
        
        # Apply core unified labels
        for label_name, label_info in UNIFIED_LABELS.items():
            result = self.create_label(
                repo, label_name, label_info["color"], 
                label_info["description"], dry_run
            )
            success = success and result
        
        # Apply repository-specific labels
        for category, labels in REPO_SPECIFIC_LABELS.items():
            for label_name, label_info in labels.items():
                # Check if this label applies to this repo
                if "repos" in label_info:
                    if repo not in label_info["repos"]:
                        continue
                
                result = self.create_label(
                    repo, label_name, label_info["color"],
                    label_info["description"], dry_run
                )
                success = success and result
        
        return success
    
    def list_current_labels(self, repo: str):
        """List current labels in a repository."""
        try:
            labels = self.get_existing_labels(repo)
            print(f"\n--- Current labels in {repo} ---")
            for label in labels:
                print(f"  {label['name']} (#{label['color']}) - {label.get('description', '')}")
        except Exception as e:
            print(f"Error listing labels for {repo}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Apply unified GitHub labels to QuantEcon repositories')
    parser.add_argument('--token', required=True, help='GitHub personal access token')
    parser.add_argument('--org', default='QuantEcon', help='GitHub organization name')
    parser.add_argument('--repo', help='Specific repository to update (default: all target repos)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--list-current', action='store_true', help='List current labels in repositories')
    
    args = parser.parse_args()
    
    manager = GitHubLabelManager(args.token, args.org)
    
    repos_to_process = [args.repo] if args.repo else TARGET_REPOS
    
    if args.list_current:
        for repo in repos_to_process:
            manager.list_current_labels(repo)
        return
    
    print("QuantEcon Unified Label Application")
    print("==================================")
    print(f"Organization: {args.org}")
    print(f"Repositories: {', '.join(repos_to_process)}")
    
    if args.dry_run:
        print("Mode: DRY RUN (no changes will be made)")
    else:
        print("Mode: LIVE (changes will be applied)")
        confirm = input("\nProceed? (y/N): ")
        if confirm.lower() != 'y':
            print("Aborted")
            return
    
    overall_success = True
    for repo in repos_to_process:
        try:
            success = manager.apply_labels_to_repo(repo, args.dry_run)
            overall_success = overall_success and success
        except Exception as e:
            print(f"Error processing {repo}: {e}")
            overall_success = False
    
    if overall_success:
        print("\n✓ All labels applied successfully!")
    else:
        print("\n✗ Some labels failed to apply. Check output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()