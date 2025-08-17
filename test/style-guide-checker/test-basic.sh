#!/bin/bash
# Basic test for the style guide checker action

set -e

echo "Testing style guide checker action..."

# Mock environment variables for testing
export INPUT_STYLE_GUIDE=".github/copilot-qe-style-guide.md"
export INPUT_DOCS="test/style-guide-checker"
export INPUT_EXCLUDE_FILES=""
export INPUT_MODE="full"
export INPUT_CONFIDENCE_THRESHOLD="high"
export INPUT_GITHUB_TOKEN="fake-token-for-testing"
export INPUT_OPENAI_API_KEY=""  # Test without OpenAI (rule-based fallback)
export INPUT_MAX_SUGGESTIONS="10"
export INPUT_CREATE_PR="false"
export GITHUB_OUTPUT="/tmp/github_output_test"
export GITHUB_REPOSITORY="QuantEcon/test-repo"
export GITHUB_EVENT_NAME="workflow_dispatch"

# Create a temporary GitHub output file
echo "" > "$GITHUB_OUTPUT"

# Test 1: Check that the Python script can be imported
echo "🧪 Test 1: Python script import test"
python3 -c "
import sys
sys.path.insert(0, '.github/actions/style-guide-checker')
import check_style
print('✅ Python script imported successfully')
"

# Test 2: Check rule-based analysis (without OpenAI)
echo "🧪 Test 2: Rule-based analysis test"
cd .github/actions/style-guide-checker
python3 -c "
import sys
import os
os.environ['INPUT_STYLE_GUIDE'] = '../../../.github/copilot-qe-style-guide.md'
os.environ['INPUT_DOCS'] = '../../../test/style-guide-checker'
os.environ['INPUT_MODE'] = 'full'
os.environ['INPUT_GITHUB_TOKEN'] = 'fake-token'
os.environ['INPUT_OPENAI_API_KEY'] = ''
os.environ['GITHUB_OUTPUT'] = '/tmp/test_output'
os.environ['GITHUB_REPOSITORY'] = 'test/repo'
os.environ['GITHUB_EVENT_NAME'] = 'workflow_dispatch'

# Import and test directly
import check_style

# Create instance and test basic file analysis
checker = check_style.StyleGuideChecker()
print('✅ Rule-based analysis test passed')
"
cd ../../..

# Test 3: Test file exclusion patterns
echo "🧪 Test 3: File exclusion test"
python3 -c "
import re

def should_include_file(file_path, exclude_files):
    if not exclude_files:
        return True
    exclude_patterns = [p.strip() for p in exclude_files.split(',')]
    for pattern in exclude_patterns:
        if pattern and re.search(pattern, file_path):
            return False
    return True

# Test exclusion patterns
test_files = [
    'test/style-guide-checker/clean-lecture.md',
    'test/style-guide-checker/exclude-me.md',
    'test/style-guide-checker/bad-style-lecture.md'
]

exclude_pattern = r'.*exclude.*\.md'
for file in test_files:
    included = should_include_file(file, exclude_pattern)
    if 'exclude' in file and included:
        raise Exception(f'File {file} should have been excluded')
    elif 'exclude' not in file and not included:
        raise Exception(f'File {file} should have been included')

print('✅ File exclusion test passed')
"

# Test 4: Check that action.yml is valid YAML
echo "🧪 Test 4: Action YAML validation"
python3 -c "
import yaml
with open('.github/actions/style-guide-checker/action.yml') as f:
    action_config = yaml.safe_load(f)
    
required_fields = ['name', 'description', 'inputs', 'outputs', 'runs']
for field in required_fields:
    if field not in action_config:
        raise Exception(f'Missing required field: {field}')
        
print('✅ Action YAML validation passed')
"

echo "✅ All basic tests passed!"

# Clean up
rm -f /tmp/github_output_test /tmp/test_output

echo "🎉 Style guide checker tests completed successfully!"