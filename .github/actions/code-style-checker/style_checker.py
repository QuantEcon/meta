#!/usr/bin/env python3
"""
Code Style Checker Script
Extracts Python code from HTML code-cell blocks and runs style checkers.
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
import os
from pathlib import Path
from bs4 import BeautifulSoup


def extract_code_blocks(html_content):
    """Extract Python code blocks from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    code_blocks = []
    processed_content = set()  # Track processed content to avoid duplicates
    
    # Look for various patterns that indicate code cells
    patterns = [
        # Jupyter notebook style
        {'class': re.compile(r'.*cell_input.*')},
        {'class': re.compile(r'.*input_area.*')},
        {'class': re.compile(r'.*code-cell.*')},
        {'class': re.compile(r'.*highlight.*python.*')},
        # MyST-NB style
        {'class': re.compile(r'.*language-python.*')},
    ]
    
    for pattern in patterns:
        elements = soup.find_all(attrs=pattern)
        for element in elements:
            # Extract text content
            code_text = element.get_text()
            
            # Clean up the code
            cleaned_code = clean_code_block(code_text)
            
            # Use a hash of the cleaned content to detect duplicates
            content_hash = hash(cleaned_code.strip())
            if content_hash in processed_content:
                continue
            
            if cleaned_code and is_python_code(cleaned_code):
                processed_content.add(content_hash)
                code_blocks.append({
                    'content': cleaned_code,
                    'element_class': element.get('class', []),
                    'line_start': get_line_number(html_content, str(element)[:100])
                })
    
    # Also look for <pre><code> blocks with Python indicators
    pre_elements = soup.find_all('pre')
    for pre in pre_elements:
        code_element = pre.find('code')
        if code_element:
            # Check for language indicators
            classes = ' '.join(code_element.get('class', []))
            if 'python' in classes.lower() or 'py' in classes.lower():
                code_text = code_element.get_text()
                cleaned_code = clean_code_block(code_text)
                
                # Use a hash of the cleaned content to detect duplicates
                content_hash = hash(cleaned_code.strip())
                if content_hash in processed_content:
                    continue
                
                if cleaned_code and is_python_code(cleaned_code):
                    processed_content.add(content_hash)
                    code_blocks.append({
                        'content': cleaned_code,
                        'element_class': code_element.get('class', []),
                        'line_start': get_line_number(html_content, str(pre)[:100])
                    })
    
    return code_blocks


def clean_code_block(code_text):
    """Clean up extracted code text"""
    if not code_text:
        return ""
    
    lines = code_text.split('\n')
    cleaned_lines = []
    
    # First pass: remove prompts and find minimum indentation
    min_indent = float('inf')
    for line in lines:
        # Remove IPython prompts
        line = re.sub(r'^(In \[\d+\]:|>>> |\.\.\.)', '', line)
        
        # Skip empty lines for indentation calculation
        if line.strip():
            # Calculate indentation
            indent = len(line) - len(line.lstrip())
            min_indent = min(min_indent, indent)
        
        cleaned_lines.append(line)
    
    # Second pass: normalize indentation
    if min_indent != float('inf') and min_indent > 0:
        normalized_lines = []
        for line in cleaned_lines:
            if line.strip():  # Non-empty line
                # Remove the common indentation
                if len(line) >= min_indent:
                    line = line[min_indent:]
                normalized_lines.append(line.rstrip())
            else:
                normalized_lines.append('')
        cleaned_lines = normalized_lines
    else:
        # Just strip trailing whitespace
        cleaned_lines = [line.rstrip() for line in cleaned_lines]
    
    # Remove leading and trailing empty lines
    while cleaned_lines and not cleaned_lines[0].strip():
        cleaned_lines.pop(0)
    while cleaned_lines and not cleaned_lines[-1].strip():
        cleaned_lines.pop()
    
    return '\n'.join(cleaned_lines)


def is_python_code(code_text):
    """Heuristically determine if text is Python code"""
    if not code_text or len(code_text.strip()) < 5:
        return False
    
    # Clean up text for analysis
    lines = code_text.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    
    if not non_empty_lines:
        return False
    
    # Python keywords and common patterns
    python_indicators = [
        'import ', 'from ', 'def ', 'class ', 'if ', 'for ', 'while ',
        'try:', 'except:', 'print(', 'return ', '= ', 'lambda ',
        '__init__', '__name__', 'self.', '.append(', '.join(',
        'numpy', 'pandas', 'matplotlib', 'plt.', 'np.', 'pd.',
        'quantecon', 'qe.', 'scipy', 'sklearn', 'with ', 'as '
    ]
    
    # Check for Python indicators
    code_lower = code_text.lower()
    python_count = sum(1 for indicator in python_indicators if indicator in code_lower)
    
    # Also check line-by-line for Python-like syntax
    syntax_count = 0
    for line in non_empty_lines[:5]:  # Check first 5 non-empty lines
        if re.search(r'^\s*(import|from|def|class|if|for|while|try|except|return|with)\b', line):
            syntax_count += 1
        elif re.search(r'=\s*[^=]', line):  # Assignment but not comparison
            syntax_count += 1
        elif re.search(r'\w+\(.*\)', line):  # Function calls
            syntax_count += 1
    
    # Must have at least some Python indicators
    if python_count < 1 and syntax_count < 1:
        return False
    
    # Check for obvious non-Python content
    non_python_indicators = [
        '<!DOCTYPE', '<html', '<head', '<body', '<div', '<span',
        '<?xml', '<?php', 'console.log', 'function(', 'var ', 'let ',
        'const ', '=>', '$$', '\\begin{', '\\end{', '\\frac',
        'ls -', 'cd /', 'wget ', 'curl ', 'sudo ', 'apt-get'
    ]
    
    non_python_count = sum(1 for indicator in non_python_indicators if indicator in code_text)
    
    # If too many non-Python indicators, probably not Python
    if non_python_count > max(python_count, syntax_count):
        return False
    
    return True


def get_line_number(html_content, element_str):
    """Get approximate line number of element in HTML"""
    try:
        index = html_content.find(element_str[:100])  # Use first 100 chars for search
        if index != -1:
            return html_content[:index].count('\n') + 1
    except:
        pass
    return 1


def should_exclude_code(code_content, exclude_patterns):
    """Check if code should be excluded based on patterns"""
    if not exclude_patterns:
        return False
    
    patterns = [p.strip() for p in exclude_patterns.split(',') if p.strip()]
    
    for pattern in patterns:
        if pattern in code_content:
            return True
    
    return False


def run_flake8(code_content, max_line_length):
    """Run flake8 on code content"""
    issues = []
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code_content)
        f.flush()
        
        try:
            # Run flake8 with custom configuration
            cmd = [
                'flake8',
                '--max-line-length', str(max_line_length),
                '--extend-ignore', 'E203,W503',  # Common black compatibility ignores
                '--format', '%(row)d:%(col)d: %(code)s %(text)s',
                f.name
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.stdout.strip():
                for line in result.stdout.strip().split('\n'):
                    if ':' in line:
                        parts = line.split(':', 2)
                        if len(parts) >= 3:
                            line_num = parts[0]
                            col_num = parts[1]
                            message = parts[2].strip()
                            issues.append({
                                'line': int(line_num),
                                'column': int(col_num),
                                'message': message,
                                'checker': 'flake8'
                            })
        
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, Exception) as e:
            # Don't fail on individual checker errors
            pass
        
        finally:
            try:
                os.unlink(f.name)
            except:
                pass
    
    return issues


def run_black_check(code_content, max_line_length):
    """Run black --check on code content"""
    issues = []
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code_content)
        f.flush()
        
        try:
            # Run black in check mode
            cmd = [
                'black',
                '--check',
                '--line-length', str(max_line_length),
                '--diff',
                f.name
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Black returns non-zero if formatting changes are needed
            if result.returncode != 0:
                # Parse the diff output to identify issues
                if result.stdout.strip():
                    # Count the number of formatting changes
                    diff_lines = result.stdout.count('\n')
                    issues.append({
                        'line': 1,
                        'column': 1,
                        'message': f'Code formatting issues detected ({diff_lines} line changes needed)',
                        'checker': 'black',
                        'diff': result.stdout
                    })
        
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, Exception) as e:
            # Don't fail on individual checker errors
            pass
        
        finally:
            try:
                os.unlink(f.name)
            except:
                pass
    
    return issues


def run_pep8_check(code_content, max_line_length):
    """Run pycodestyle (pep8) on code content"""
    issues = []
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code_content)
        f.flush()
        
        try:
            # Run pycodestyle
            cmd = [
                'pycodestyle',
                '--max-line-length', str(max_line_length),
                '--format', '%(row)d:%(col)d: %(code)s %(text)s',
                f.name
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.stdout.strip():
                for line in result.stdout.strip().split('\n'):
                    if ':' in line:
                        parts = line.split(':', 2)
                        if len(parts) >= 3:
                            line_num = parts[0]
                            col_num = parts[1]
                            message = parts[2].strip()
                            issues.append({
                                'line': int(line_num),
                                'column': int(col_num),
                                'message': message,
                                'checker': 'pep8'
                            })
        
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, Exception) as e:
            # Don't fail on individual checker errors
            pass
        
        finally:
            try:
                os.unlink(f.name)
            except:
                pass
    
    return issues


def check_code_style(html_file, checkers, max_line_length, exclude_patterns):
    """Main function to check code style in HTML file"""
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        return {
            'error': f"Failed to read HTML file: {e}",
            'total_code_blocks': 0,
            'flake8_issues': [],
            'black_issues': [],
            'pep8_issues': []
        }
    
    # Extract code blocks
    code_blocks = extract_code_blocks(html_content)
    
    # Filter out excluded code
    filtered_blocks = []
    for block in code_blocks:
        if not should_exclude_code(block['content'], exclude_patterns):
            filtered_blocks.append(block)
    
    code_blocks = filtered_blocks
    
    result = {
        'total_code_blocks': len(code_blocks),
        'flake8_issues': [],
        'black_issues': [],
        'pep8_issues': []
    }
    
    # Check each code block
    for i, block in enumerate(code_blocks):
        code_content = block['content']
        line_start = block.get('line_start', 1)
        
        # Run selected checkers
        if 'flake8' in checkers:
            flake8_issues = run_flake8(code_content, max_line_length)
            for issue in flake8_issues:
                issue['code_block'] = i + 1
                issue['html_line'] = line_start
                issue['code_preview'] = code_content[:100] + ('...' if len(code_content) > 100 else '')
            result['flake8_issues'].extend(flake8_issues)
        
        if 'black' in checkers:
            black_issues = run_black_check(code_content, max_line_length)
            for issue in black_issues:
                issue['code_block'] = i + 1
                issue['html_line'] = line_start
                issue['code_preview'] = code_content[:100] + ('...' if len(code_content) > 100 else '')
            result['black_issues'].extend(black_issues)
        
        if 'pep8' in checkers:
            pep8_issues = run_pep8_check(code_content, max_line_length)
            for issue in pep8_issues:
                issue['code_block'] = i + 1
                issue['html_line'] = line_start
                issue['code_preview'] = code_content[:100] + ('...' if len(code_content) > 100 else '')
            result['pep8_issues'].extend(pep8_issues)
    
    return result


def main():
    parser = argparse.ArgumentParser(description='Check Python code style in HTML files')
    parser.add_argument('html_file', help='HTML file to check')
    parser.add_argument('--checkers', default='flake8,black,pep8',
                        help='Comma-separated list of checkers to run')
    parser.add_argument('--max-line-length', type=int, default=88,
                        help='Maximum line length')
    parser.add_argument('--exclude-patterns', default='',
                        help='Comma-separated list of patterns to exclude')
    
    args = parser.parse_args()
    
    # Parse checkers list
    checkers = [c.strip().lower() for c in args.checkers.split(',') if c.strip()]
    
    # Run the check
    result = check_code_style(
        args.html_file,
        checkers,
        args.max_line_length,
        args.exclude_patterns
    )
    
    # Output results as JSON
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()