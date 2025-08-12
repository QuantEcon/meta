#!/usr/bin/env python3
"""
Test script for the translation workflow.

This script tests the basic functionality without making actual API calls.
"""

import json
import sys
import os
from pathlib import Path

# Add the scripts directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_file_structure():
    """Test that all required files exist."""
    required_files = [
        '.github/workflows/lecture-translation-migration.yml',
        'scripts/check_translation_status.py',
        'scripts/create_translation_pr.py',
        'scripts/create_fallback_issue.py',
        'TRANSLATION_WORKFLOW.md'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files exist")
        return True


def test_script_syntax():
    """Test that all Python scripts have valid syntax."""
    script_files = [
        'scripts/check_translation_status.py',
        'scripts/create_translation_pr.py',
        'scripts/create_fallback_issue.py'
    ]
    
    all_valid = True
    for script_path in script_files:
        try:
            with open(script_path, 'r') as f:
                compile(f.read(), script_path, 'exec')
            print(f"✅ {script_path} has valid syntax")
        except SyntaxError as e:
            print(f"❌ {script_path} has syntax error: {e}")
            all_valid = False
    
    return all_valid


def test_workflow_syntax():
    """Test that the GitHub workflow file has valid YAML syntax."""
    try:
        import yaml
        with open('.github/workflows/lecture-translation-migration.yml', 'r') as f:
            yaml.safe_load(f)
        print("✅ Workflow YAML is valid")
        return True
    except yaml.YAMLError as e:
        print(f"❌ Workflow YAML is invalid: {e}")
        return False
    except ImportError:
        print("⚠️  PyYAML not available, skipping YAML validation")
        return True


def main():
    """Run all tests."""
    print("Testing Translation Workflow Setup")
    print("=" * 40)
    
    tests = [
        test_file_structure,
        test_script_syntax,
        test_workflow_syntax
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with error: {e}")
            results.append(False)
        print()
    
    if all(results):
        print("🎉 All tests passed! The workflow is ready to use.")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues before using the workflow.")
        return 1


if __name__ == '__main__':
    sys.exit(main())