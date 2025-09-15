#!/usr/bin/env python3
"""
Test script for the code style checker
"""
import json
import os
import subprocess
import sys
import tempfile

def test_style_checker():
    """Test the style checker functionality"""
    test_dir = os.path.dirname(__file__)
    action_dir = os.path.join(test_dir, '../../.github/actions/code-style-checker')
    style_checker = os.path.join(action_dir, 'style_checker.py')
    
    print("Testing Code Style Checker")
    print("=" * 50)
    
    # Test files
    test_files = [
        ('clean-code.html', 'Should have minimal or no issues'),
        ('style-issues.html', 'Should have multiple style issues'),
        ('mixed-content.html', 'Should detect Python code and ignore non-Python content')
    ]
    
    all_passed = True
    
    for filename, description in test_files:
        print(f"\nTesting {filename}: {description}")
        print("-" * 40)
        
        file_path = os.path.join(test_dir, filename)
        if not os.path.exists(file_path):
            print(f"❌ FAIL: Test file {file_path} not found")
            all_passed = False
            continue
        
        try:
            # Run the style checker
            cmd = [
                sys.executable, style_checker,
                file_path,
                '--checkers', 'flake8,black,pep8',
                '--max-line-length', '88',
                '--exclude-patterns', '!pip install,!conda install,plt.show()'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                print(f"❌ FAIL: Style checker failed with return code {result.returncode}")
                print(f"stderr: {result.stderr}")
                all_passed = False
                continue
            
            # Parse JSON output
            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                print(f"❌ FAIL: Invalid JSON output: {e}")
                print(f"stdout: {result.stdout}")
                all_passed = False
                continue
            
            # Analyze results
            total_blocks = data.get('total_code_blocks', 0)
            flake8_issues = len(data.get('flake8_issues', []))
            black_issues = len(data.get('black_issues', []))
            pep8_issues = len(data.get('pep8_issues', []))
            total_issues = flake8_issues + black_issues + pep8_issues
            
            print(f"✅ PASS: Successfully processed {total_blocks} code blocks")
            print(f"   Issues found: {total_issues} total (flake8: {flake8_issues}, black: {black_issues}, pep8: {pep8_issues})")
            
            # Validate expectations
            if filename == 'clean-code.html':
                if total_issues > 2:  # Allow for minor issues
                    print(f"⚠️  WARNING: Expected minimal issues for clean code, but found {total_issues}")
                else:
                    print(f"✅ PASS: Clean code has acceptable number of issues ({total_issues})")
            
            elif filename == 'style-issues.html':
                if total_issues < 5:  # Should have multiple issues
                    print(f"⚠️  WARNING: Expected multiple issues for problematic code, but found {total_issues}")
                else:
                    print(f"✅ PASS: Problematic code has expected number of issues ({total_issues})")
            
            elif filename == 'mixed-content.html':
                if total_blocks < 2:  # Should detect at least 2 Python code blocks
                    print(f"⚠️  WARNING: Expected at least 2 Python code blocks, but found {total_blocks}")
                else:
                    print(f"✅ PASS: Mixed content correctly identified {total_blocks} Python code blocks")
            
            # Show a sample of issues
            if total_issues > 0:
                print("   Sample issues:")
                for checker in ['flake8_issues', 'black_issues', 'pep8_issues']:
                    issues = data.get(checker, [])
                    if issues:
                        issue = issues[0]
                        checker_name = checker.replace('_issues', '')
                        print(f"     {checker_name}: {issue.get('message', 'No message')}")
        
        except subprocess.TimeoutExpired:
            print(f"❌ FAIL: Style checker timed out")
            all_passed = False
        except Exception as e:
            print(f"❌ FAIL: Unexpected error: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False


def test_exclude_patterns():
    """Test that exclude patterns work correctly"""
    print("\nTesting exclude patterns")
    print("-" * 30)
    
    test_dir = os.path.dirname(__file__)
    action_dir = os.path.join(test_dir, '../../.github/actions/code-style-checker')
    style_checker = os.path.join(action_dir, 'style_checker.py')
    
    # Create temporary HTML file with pip install commands
    html_content = '''
    <html><body>
    <div class="cell_input">
        <pre><code class="language-python">
!pip install numpy
import numpy as np
x=1+2  # This should be caught
        </code></pre>
    </div>
    </body></html>
    '''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(html_content)
        f.flush()
        
        try:
            # Test without exclude patterns
            cmd1 = [sys.executable, style_checker, f.name, '--checkers', 'flake8']
            result1 = subprocess.run(cmd1, capture_output=True, text=True, timeout=30)
            
            # Test with exclude patterns
            cmd2 = [sys.executable, style_checker, f.name, '--checkers', 'flake8', '--exclude-patterns', '!pip install']
            result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=30)
            
            if result1.returncode == 0 and result2.returncode == 0:
                data1 = json.loads(result1.stdout)
                data2 = json.loads(result2.stdout)
                
                blocks1 = data1.get('total_code_blocks', 0)
                blocks2 = data2.get('total_code_blocks', 0)
                
                if blocks2 < blocks1:
                    print("✅ PASS: Exclude patterns working correctly")
                    print(f"   Code blocks without exclusion: {blocks1}")
                    print(f"   Code blocks with exclusion: {blocks2}")
                    return True
                else:
                    print("⚠️  WARNING: Exclude patterns may not be working as expected")
                    return False
            else:
                print("❌ FAIL: Style checker failed during exclude pattern test")
                return False
        
        finally:
            os.unlink(f.name)


if __name__ == "__main__":
    success1 = test_style_checker()
    success2 = test_exclude_patterns()
    
    if success1 and success2:
        print("\n🎉 All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed")
        sys.exit(1)