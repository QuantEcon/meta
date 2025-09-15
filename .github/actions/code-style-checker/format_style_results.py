#!/usr/bin/env python3
"""
Format style checker results for reporting
"""
import json
import sys


def format_flake8_results(data):
    """Format flake8 issues for display"""
    issues = data.get('flake8_issues', [])
    if not issues:
        return ""
    
    formatted = []
    for issue in issues:
        line = f"Line {issue['line']}: {issue['message']}"
        if 'code_preview' in issue:
            line += f"\n  ```python\n  {issue['code_preview']}\n  ```"
        formatted.append(line)
    
    return '\n\n'.join(formatted)


def format_black_results(data):
    """Format black issues for display"""
    issues = data.get('black_issues', [])
    if not issues:
        return ""
    
    formatted = []
    for issue in issues:
        line = f"Formatting: {issue['message']}"
        if 'code_preview' in issue:
            line += f"\n  ```python\n  {issue['code_preview']}\n  ```"
        if 'diff' in issue and issue['diff']:
            # Limit diff output for readability
            diff_lines = issue['diff'].split('\n')[:10]
            if len(diff_lines) == 10:
                diff_lines.append('... (truncated)')
            line += f"\n  <details><summary>Diff preview</summary>\n\n  ```diff\n  " + '\n  '.join(diff_lines) + "\n  ```\n  </details>"
        formatted.append(line)
    
    return '\n\n'.join(formatted)


def format_pep8_results(data):
    """Format pep8 issues for display"""
    issues = data.get('pep8_issues', [])
    if not issues:
        return ""
    
    formatted = []
    for issue in issues:
        line = f"Line {issue['line']}: {issue['message']}"
        if 'code_preview' in issue:
            line += f"\n  ```python\n  {issue['code_preview']}\n  ```"
        formatted.append(line)
    
    return '\n\n'.join(formatted)


def main():
    if len(sys.argv) != 2:
        print("Usage: format_style_results.py <checker_type>", file=sys.stderr)
        sys.exit(1)
    
    checker_type = sys.argv[1].lower()
    
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    if checker_type == 'flake8':
        print(format_flake8_results(data))
    elif checker_type == 'black':
        print(format_black_results(data))
    elif checker_type == 'pep8':
        print(format_pep8_results(data))
    else:
        print(f"Unknown checker type: {checker_type}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()