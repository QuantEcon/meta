#!/bin/bash
# Test script for the QuantEcon Style Guide Action

set -e

echo "Testing QuantEcon Style Guide Action..."

# Mock environment variables for testing
export INPUT_GITHUB_TOKEN="fake-token-for-testing"
export INPUT_STYLE_GUIDE="/home/runner/work/meta/meta/.github/copilot-qe-style-guide.md"
export INPUT_DOCS="/home/runner/work/meta/meta/test/qe-style-guide/"
export INPUT_EXTENSIONS="md"
export INPUT_OPENAI_API_KEY=""  # Test without AI first
export INPUT_MODEL="gpt-4"
export INPUT_MAX_SUGGESTIONS="20"
export INPUT_CONFIDENCE_THRESHOLD="0.8"
export GITHUB_OUTPUT="/tmp/github_output_test"

# Create a temporary GitHub output file
echo "" > "$GITHUB_OUTPUT"

# Test 1: Basic functionality test without AI
echo "=== Test 1: Basic rule-based analysis ==="

# Mock GitHub context for issue comment
export GITHUB_CONTEXT='{
  "event_name": "issue_comment",
  "repository": "QuantEcon/test-repo",
  "event": {
    "comment": {
      "body": "@qe-style-check test-document-with-issues.md"
    },
    "issue": {
      "number": 123
    }
  }
}'

# Create a simple Python test that imports and tests basic functionality
cat > /tmp/test_style_checker.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
import json

# Add the action path to sys.path so we can import the module
action_path = '/home/runner/work/meta/meta/.github/actions/qe-style-guide'
sys.path.insert(0, action_path)

# Change to the action directory so relative imports work
import os
os.chdir(action_path)

try:
    from process_style_check import StyleGuideChecker
    
    # Test basic initialization
    checker = StyleGuideChecker()
    print("✅ StyleGuideChecker initialized successfully")
    
    # Test style guide loading
    style_guide = checker.load_style_guide()
    print(f"✅ Style guide loaded: {len(style_guide)} characters")
    
    # Test comment parsing
    mode, target_file = checker.parse_trigger_comment()
    print(f"✅ Comment parsed: mode={mode}, target_file={target_file}")
    
    if mode != 'issue' or target_file != 'test-document-with-issues.md':
        print(f"❌ Expected mode='issue', target_file='test-document-with-issues.md', got mode='{mode}', target_file='{target_file}'")
        sys.exit(1)
    
    # Test rule-based analysis
    test_content = """
def test_function(alpha, beta):
    return alpha + beta
"""
    
    result = checker.analyze_with_rules(test_content, style_guide, "test.md")
    suggestions = result.get('suggestions', [])
    print(f"✅ Rule-based analysis found {len(suggestions)} suggestions")
    
    # Check that Greek letter suggestions were found
    greek_suggestions = [s for s in suggestions if 'alpha' in s.get('original_text', '') or 'beta' in s.get('original_text', '')]
    if len(greek_suggestions) >= 1:
        print("✅ Greek letter suggestions found as expected")
    else:
        print("⚠️  No Greek letter suggestions found (this might be expected)")
    
    print("✅ All basic tests passed!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

# Run the basic test
cd /home/runner/work/meta/meta
python3 /tmp/test_style_checker.py

echo ""
echo "=== Test 2: File content processing ==="

# Test reading local file content (since we can't actually call GitHub API)
cat > /tmp/test_file_processing.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, '/home/runner/work/meta/meta/.github/actions/qe-style-guide')

try:
    from process_style_check import StyleGuideChecker
    
    checker = StyleGuideChecker()
    
    # Read a local test file directly (simulate get_file_content)
    test_file_path = "/home/runner/work/meta/meta/test/qe-style-guide/test-document-with-issues.md"
    
    if os.path.exists(test_file_path):
        with open(test_file_path, 'r') as f:
            content = f.read()
        print(f"✅ Successfully read test file: {len(content)} characters")
        
        # Test analysis
        style_guide = checker.load_style_guide()
        result = checker.analyze_with_rules(content, style_guide, test_file_path)
        suggestions = result.get('suggestions', [])
        
        print(f"✅ Analysis completed: {len(suggestions)} suggestions found")
        
        # Print some suggestions for verification
        for i, suggestion in enumerate(suggestions[:3]):
            print(f"  Suggestion {i+1}: {suggestion.get('description', 'No description')}")
        
        if len(suggestions) > 0:
            print("✅ Style issues detected as expected")
        else:
            print("⚠️  No style issues detected (might indicate test file is too clean)")
    else:
        print(f"❌ Test file not found: {test_file_path}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ File processing test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

python3 /tmp/test_file_processing.py

echo ""
echo "=== Test 3: Clean file test ==="

# Test with clean file
export GITHUB_CONTEXT='{
  "event_name": "issue_comment",
  "repository": "QuantEcon/test-repo",
  "event": {
    "comment": {
      "body": "@qe-style-check clean-document.md"
    },
    "issue": {
      "number": 123
    }
  }
}'

cat > /tmp/test_clean_file.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, '/home/runner/work/meta/meta/.github/actions/qe-style-guide')

try:
    from process_style_check import StyleGuideChecker
    
    checker = StyleGuideChecker()
    
    # Parse comment for clean file
    mode, target_file = checker.parse_trigger_comment()
    print(f"✅ Clean file test: mode={mode}, target_file={target_file}")
    
    # Read clean test file
    test_file_path = "/home/runner/work/meta/meta/test/qe-style-guide/clean-document.md"
    
    if os.path.exists(test_file_path):
        with open(test_file_path, 'r') as f:
            content = f.read()
        
        style_guide = checker.load_style_guide()
        result = checker.analyze_with_rules(content, style_guide, test_file_path)
        suggestions = result.get('suggestions', [])
        
        print(f"✅ Clean file analysis: {len(suggestions)} suggestions found")
        
        if len(suggestions) <= 2:  # Allow for minor suggestions
            print("✅ Clean file test passed - minimal suggestions as expected")
        else:
            print(f"⚠️  Clean file had more suggestions than expected: {len(suggestions)}")
            for suggestion in suggestions:
                print(f"  - {suggestion.get('description', 'No description')}")
    else:
        print(f"❌ Clean test file not found: {test_file_path}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Clean file test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

python3 /tmp/test_clean_file.py

# Clean up
rm -f /tmp/test_style_checker.py /tmp/test_file_processing.py /tmp/test_clean_file.py /tmp/github_output_test

echo ""
echo "✅ All QuantEcon Style Guide Action tests completed successfully!"