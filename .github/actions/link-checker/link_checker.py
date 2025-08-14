#!/usr/bin/env python3
"""
AI-Powered Link Checker Script
Checks external links in HTML files and provides AI suggestions for improvements.
"""
import re
import sys
import requests
import urllib.parse
from bs4 import BeautifulSoup
import json
import time
import os
import argparse

def is_external_link(url):
    """Check if URL is external (starts with http/https)"""
    return url.startswith(('http://', 'https://'))

def check_link(url, timeout, max_redirects, silent_codes):
    """Check a single link and return status info"""
    try:
        # Set up session with redirects tracking
        session = requests.Session()
        session.max_redirects = max_redirects
        
        response = session.get(
            url, 
            timeout=timeout,
            allow_redirects=True,
            headers={'User-Agent': 'QuantEcon-LinkChecker/1.0'}
        )
        
        result = {
            'url': url,
            'status_code': response.status_code,
            'final_url': response.url,
            'redirect_count': len(response.history),
            'redirected': len(response.history) > 0,
            'broken': False,
            'silent': False,
            'error': None
        }
        
        # Check if status code should be silently reported
        if response.status_code in silent_codes:
            result['silent'] = True
        elif not response.ok:
            result['broken'] = True
        
        return result
        
    except requests.exceptions.Timeout:
        return {
            'url': url, 'status_code': 0, 'final_url': url,
            'redirect_count': 0, 'redirected': False, 'broken': True,
            'silent': False, 'error': 'Timeout'
        }
    except requests.exceptions.ConnectionError:
        return {
            'url': url, 'status_code': 0, 'final_url': url,
            'redirect_count': 0, 'redirected': False, 'broken': True,
            'silent': False, 'error': 'Connection Error'
        }
    except Exception as e:
        return {
            'url': url, 'status_code': 0, 'final_url': url,
            'redirect_count': 0, 'redirected': False, 'broken': True,
            'silent': False, 'error': str(e)
        }

def extract_links_from_html(file_path):
    """Extract all external links from HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        links = []
        
        # Find all anchor tags with href
        for tag in soup.find_all('a', href=True):
            href = tag['href']
            if is_external_link(href):
                # Store link with context
                links.append({
                    'url': href,
                    'text': tag.get_text(strip=True)[:100],  # First 100 chars
                    'line': None  # We could calculate line numbers if needed
                })
        
        return links
        
    except Exception as e:
        print(f"Error parsing {file_path}: {e}", file=sys.stderr)
        return []

def generate_ai_suggestions(broken_results, redirect_results):
    """Generate AI-powered suggestions for broken and redirected links"""
    suggestions = []
    
    # Simple rule-based AI suggestions (can be enhanced with actual AI services)
    for result in broken_results:
        url = result['url']
        suggestion = {
            'original_url': url,
            'issue': f"Broken link (Status: {result['status_code']})",
            'suggestions': []
        }
        
        # Common URL fixes
        if 'github.com' in url:
            # GitHub-specific suggestions
            if '/blob/master/' in url:
                new_url = url.replace('/blob/master/', '/blob/main/')
                suggestion['suggestions'].append({
                    'type': 'branch_update',
                    'url': new_url,
                    'reason': 'GitHub default branch changed from master to main'
                })
            if 'github.io' in url and 'http://' in url:
                new_url = url.replace('http://', 'https://')
                suggestion['suggestions'].append({
                    'type': 'https_upgrade',
                    'url': new_url,
                    'reason': 'GitHub Pages now requires HTTPS'
                })
        
        # Documentation site migrations
        elif 'readthedocs.org' in url and 'http://' in url:
            new_url = url.replace('http://', 'https://')
            suggestion['suggestions'].append({
                'type': 'https_upgrade',
                'url': new_url,
                'reason': 'Read the Docs now requires HTTPS'
            })
        
        # Python.org domain changes
        elif 'docs.python.org' in url:
            if '/2.7/' in url:
                new_url = url.replace('/2.7/', '/3/')
                suggestion['suggestions'].append({
                    'type': 'version_update',
                    'url': new_url,
                    'reason': 'Python 2.7 is deprecated, consider Python 3 documentation'
                })
        
        # General HTTPS upgrade
        elif url.startswith('http://') and 'localhost' not in url:
            new_url = url.replace('http://', 'https://')
            suggestion['suggestions'].append({
                'type': 'https_upgrade',
                'url': new_url,
                'reason': 'HTTPS is more secure and widely supported'
            })
        
        if suggestion['suggestions']:
            suggestions.append(suggestion)
    
    # Handle redirects
    for result in redirect_results:
        if result['redirect_count'] > 0:
            suggestion = {
                'original_url': result['url'],
                'issue': f"Redirected {result['redirect_count']} times",
                'suggestions': [{
                    'type': 'redirect_update',
                    'url': result['final_url'],
                    'reason': f'Update to final destination to avoid {result["redirect_count"]} redirect(s)'
                }]
            }
            suggestions.append(suggestion)
    
    return suggestions

def main():
    parser = argparse.ArgumentParser(description='Check links in HTML files')
    parser.add_argument('file_path', help='Path to HTML file')
    parser.add_argument('--timeout', type=int, default=30, help='Timeout in seconds')
    parser.add_argument('--max-redirects', type=int, default=5, help='Maximum redirects')
    parser.add_argument('--silent-codes', default='403,503', help='Silent status codes')
    parser.add_argument('--ai-suggestions', action='store_true', help='Enable AI suggestions')
    
    args = parser.parse_args()
    
    silent_codes = [int(x.strip()) for x in args.silent_codes.split(',') if x.strip()]
    
    # Extract links
    links = extract_links_from_html(args.file_path)
    if not links:
        print(json.dumps({
            'broken_results': [], 'redirect_results': [], 
            'ai_suggestions': [], 'total_links': 0
        }))
        return
    
    broken_results = []
    redirect_results = []
    
    print(f"Checking {len(links)} links in {args.file_path}...", file=sys.stderr)
    
    # Check each link
    for i, link_info in enumerate(links):
        url = link_info['url']
        result = check_link(url, args.timeout, args.max_redirects, silent_codes)
        result['file'] = args.file_path
        result['text'] = link_info['text']
        
        if result['broken'] and not result['silent']:
            broken_results.append(result)
        elif result['redirected']:
            redirect_results.append(result)
        
        # Add small delay to be respectful
        if i < len(links) - 1:
            time.sleep(0.1)
    
    # Generate AI suggestions
    ai_suggestions = []
    if args.ai_suggestions:
        ai_suggestions = generate_ai_suggestions(broken_results, redirect_results)
    
    # Output results
    print(json.dumps({
        'broken_results': broken_results,
        'redirect_results': redirect_results, 
        'ai_suggestions': ai_suggestions,
        'total_links': len(links)
    }))

if __name__ == "__main__":
    main()