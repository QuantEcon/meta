#!/bin/bash
# Test script for PR mode functionality

set -e

echo "Testing PR mode functionality..."

# Create a temporary git repository for testing
TEST_DIR="/tmp/test-pr-mode"
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

# Initialize git repo
git init
git config user.email "test@example.com"
git config user.name "Test User"

# Create some test files
mkdir -p _build/html
echo '# Test Lecture 1' > lecture1.md
echo '# Test Lecture 2' > lecture2.md
echo '# Test Lecture 3' > lecture3.md

# Create corresponding HTML files with and without warnings
cat > _build/html/lecture1.html << 'EOF'
<!DOCTYPE html>
<html>
<head><title>Lecture 1</title></head>
<body>
    <h1>Lecture 1</h1>
    <div class="cell_output">
        <pre>/path/to/file.py:10: UserWarning: Test warning in lecture 1</pre>
    </div>
</body>
</html>
EOF

cat > _build/html/lecture2.html << 'EOF'
<!DOCTYPE html>
<html>
<head><title>Lecture 2</title></head>
<body>
    <h1>Lecture 2</h1>
    <div class="cell_output">
        <pre>Clean output with no warnings</pre>
    </div>
</body>
</html>
EOF

cat > _build/html/lecture3.html << 'EOF'
<!DOCTYPE html>
<html>
<head><title>Lecture 3</title></head>
<body>
    <h1>Lecture 3</h1>
    <div class="cell_output">
        <pre>/path/to/file.py:15: DeprecationWarning: Test warning in lecture 3</pre>
    </div>
</body>
</html>
EOF

# Commit initial state
git add .
git commit -m "Initial commit"

# Rename master to main for consistency
git branch -m master main

# Create a branch to simulate PR
git checkout -b feature-branch

# Modify only lecture1.md (simulate editing the lecture)
echo '# Test Lecture 1 - Updated' > lecture1.md
git add lecture1.md
git commit -m "Update lecture1"

# Switch back to main to simulate remote
git checkout main
git checkout feature-branch

# Now test our PR mode logic
echo "Testing PR mode file detection..."

# Simulate the environment variables that would be present in a GitHub Action PR
export GITHUB_BASE_REF="main"
export GITHUB_EVENT_NAME="pull_request"

# Test the git diff logic that our action uses (compare with main branch)
echo "Changed .md files:"
git diff --name-only --diff-filter=AM main...HEAD | grep '\.md$' || echo "No .md files found"

# Test our file mapping logic
CHANGED_MD_FILES=()
mapfile -t CHANGED_MD_FILES < <(git diff --name-only --diff-filter=AM main...HEAD | grep '\.md$' || true)

echo "Number of changed .md files: ${#CHANGED_MD_FILES[@]}"
if [ ${#CHANGED_MD_FILES[@]} -gt 0 ]; then
    echo "Changed files:"
    printf '%s\n' "${CHANGED_MD_FILES[@]}"
    
    # Test mapping to HTML files
    HTML_PATH="_build/html"
    for md_file in "${CHANGED_MD_FILES[@]}"; do
        base_name=$(basename "$md_file" .md)
        html_file="$HTML_PATH/$base_name.html"
        if [ -f "$html_file" ]; then
            echo "✅ Found corresponding HTML file: $html_file"
        else
            echo "❌ Missing HTML file: $html_file"
        fi
    done
fi

# Clean up
cd /
rm -rf "$TEST_DIR"

echo "✅ PR mode test completed successfully"