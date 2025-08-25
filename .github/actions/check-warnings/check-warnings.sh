#!/bin/bash
set -e

# Parse inputs from environment variables set by GitHub Actions
HTML_PATH="${INPUT_HTML_PATH}"
WARNINGS="${INPUT_WARNINGS}"
EXCLUDE_WARNINGS="${INPUT_EXCLUDE_WARNING}"
FAIL_ON_WARNING="${INPUT_FAIL_ON_WARNING}"
PR_MODE="${INPUT_PR_MODE}"

echo "Scanning HTML files in: $HTML_PATH"
echo "Looking for warnings: $WARNINGS"
echo "PR mode: $PR_MODE"

# Convert comma-separated warnings to array
IFS=',' read -ra WARNING_ARRAY <<< "$WARNINGS"

# Handle exclude-warning parameter
if [ -n "$EXCLUDE_WARNINGS" ]; then
  echo "Excluding warnings: $EXCLUDE_WARNINGS"
  # Convert comma-separated exclude warnings to array
  IFS=',' read -ra EXCLUDE_ARRAY <<< "$EXCLUDE_WARNINGS"
  
  # Create a new array with warnings not in exclude list
  FILTERED_WARNING_ARRAY=()
  for warning in "${WARNING_ARRAY[@]}"; do
    # Remove leading/trailing whitespace from warning
    warning=$(echo "$warning" | xargs)
    exclude_warning=false
    
    # Check if this warning should be excluded
    for exclude in "${EXCLUDE_ARRAY[@]}"; do
      # Remove leading/trailing whitespace from exclude warning
      exclude=$(echo "$exclude" | xargs)
      if [ "$warning" = "$exclude" ]; then
        exclude_warning=true
        break
      fi
    done
    
    # Add to filtered array if not excluded
    if [ "$exclude_warning" = false ]; then
      FILTERED_WARNING_ARRAY+=("$warning")
    fi
  done
  
  # Replace WARNING_ARRAY with filtered array
  WARNING_ARRAY=("${FILTERED_WARNING_ARRAY[@]}")
  
  # Show final warning list
  if [ ${#WARNING_ARRAY[@]} -eq 0 ]; then
    echo "⚠️  All warnings have been excluded. No warnings will be checked."
  else
    echo "Final warning list after exclusions: ${WARNING_ARRAY[*]}"
  fi
fi

# Initialize counters
TOTAL_WARNINGS=0
WARNING_DETAILS=""
WARNINGS_FOUND="false"
DETAILED_REPORT=""

# Find HTML files to check
if [ ! -e "$HTML_PATH" ]; then
  echo "Error: HTML path '$HTML_PATH' does not exist"
  exit 1
fi

# Handle PR mode - only check HTML files corresponding to changed .md files
if [ "$PR_MODE" = "true" ]; then
  echo "Running in PR mode - detecting changed .md files..."
  
  # Get the list of changed .md files in this PR/push
  CHANGED_MD_FILES=()
  
  # Try to get changed files from git
  if command -v git >/dev/null 2>&1; then
    # For pull requests, compare against the base branch
    if [ -n "${GITHUB_BASE_REF:-}" ]; then
      # This is a pull request
      BASE_REF="${GITHUB_BASE_REF}"
      echo "Comparing against base branch: $BASE_REF"
      
      # Improved git diff logic with better fallback handling
      if git ls-remote --exit-code origin "$BASE_REF" >/dev/null 2>&1; then
        # Base branch exists in origin, fetch it
        echo "Fetching base branch: origin/$BASE_REF"
        git fetch origin "$BASE_REF" 2>/dev/null || echo "Warning: Could not fetch $BASE_REF"
        
        # Try different comparison strategies in order of preference
        if git rev-parse --verify "origin/$BASE_REF" >/dev/null 2>&1; then
          echo "Using origin/$BASE_REF for comparison"
          # Try three-dot syntax first, fallback to two-dot if no merge base
          if git merge-base "origin/$BASE_REF" HEAD >/dev/null 2>&1; then
            echo "Using three-dot syntax with origin/$BASE_REF"
            mapfile -t CHANGED_MD_FILES < <(git diff --name-only --diff-filter=AM "origin/$BASE_REF"...HEAD | grep '\.md$' || true)
          else
            echo "No merge base found, trying two-dot syntax with origin/$BASE_REF"
            mapfile -t CHANGED_MD_FILES < <(git diff --name-only --diff-filter=AM "origin/$BASE_REF"..HEAD | grep '\.md$' || true)
          fi
        elif git rev-parse --verify "FETCH_HEAD" >/dev/null 2>&1; then
          echo "Using FETCH_HEAD for comparison (after fetch)"
          # Try three-dot syntax first, fallback to two-dot if no merge base
          if git merge-base "FETCH_HEAD" HEAD >/dev/null 2>&1; then
            echo "Using three-dot syntax with FETCH_HEAD"
            mapfile -t CHANGED_MD_FILES < <(git diff --name-only --diff-filter=AM "FETCH_HEAD"...HEAD | grep '\.md$' || true)
          else
            echo "No merge base found, trying two-dot syntax with FETCH_HEAD"
            mapfile -t CHANGED_MD_FILES < <(git diff --name-only --diff-filter=AM "FETCH_HEAD"..HEAD | grep '\.md$' || true)
          fi
        elif git rev-parse --verify "$BASE_REF" >/dev/null 2>&1; then
          echo "Using $BASE_REF for comparison"
          # Try three-dot syntax first, fallback to two-dot if no merge base
          if git merge-base "$BASE_REF" HEAD >/dev/null 2>&1; then
            echo "Using three-dot syntax with $BASE_REF"
            mapfile -t CHANGED_MD_FILES < <(git diff --name-only --diff-filter=AM "$BASE_REF"...HEAD | grep '\.md$' || true)
          else
            echo "No merge base found, trying two-dot syntax with $BASE_REF"
            mapfile -t CHANGED_MD_FILES < <(git diff --name-only --diff-filter=AM "$BASE_REF"..HEAD | grep '\.md$' || true)
          fi
        else
          echo "Warning: Could not find base reference, using merge-base with origin/HEAD"
          # Try to find merge base with origin/HEAD
          if git rev-parse --verify "origin/HEAD" >/dev/null 2>&1; then
            MERGE_BASE=$(git merge-base HEAD origin/HEAD 2>/dev/null || echo "")
            if [ -n "$MERGE_BASE" ]; then
              echo "Using merge-base: $MERGE_BASE"
              mapfile -t CHANGED_MD_FILES < <(git diff --name-only --diff-filter=AM "$MERGE_BASE"...HEAD | grep '\.md$' || true)
            else
              echo "Warning: Could not find merge-base, falling back to HEAD~1"
              mapfile -t CHANGED_MD_FILES < <(git diff --name-only --diff-filter=AM HEAD~1...HEAD | grep '\.md$' || true)
            fi
          else
            echo "Warning: Could not find origin/HEAD, falling back to HEAD~1"
            mapfile -t CHANGED_MD_FILES < <(git diff --name-only --diff-filter=AM HEAD~1...HEAD | grep '\.md$' || true)
          fi
        fi
      else
        echo "Warning: Base branch $BASE_REF not found in origin, falling back to HEAD~1"
        mapfile -t CHANGED_MD_FILES < <(git diff --name-only --diff-filter=AM HEAD~1...HEAD | grep '\.md$' || true)
      fi
    else
      # This is a push event, compare with previous commit
      if [ "${GITHUB_EVENT_NAME:-}" = "push" ] && [ -n "${GITHUB_EVENT_BEFORE:-}" ] && [ "${GITHUB_EVENT_BEFORE}" != "0000000000000000000000000000000000000000" ]; then
        echo "Comparing against previous commit: ${GITHUB_EVENT_BEFORE}"
        mapfile -t CHANGED_MD_FILES < <(git diff --name-only --diff-filter=AM "${GITHUB_EVENT_BEFORE}"...HEAD | grep '\.md$' || true)
      else
        # Fallback to comparing with HEAD~1
        echo "Comparing against HEAD~1"
        mapfile -t CHANGED_MD_FILES < <(git diff --name-only --diff-filter=AM HEAD~1...HEAD | grep '\.md$' || true)
      fi
    fi
  else
    echo "Warning: git command not available, falling back to scanning all files"
    PR_MODE="false"
  fi
  
  # Only exit early if git is available but no .md files changed
  # If git is not available, we already fell back to normal mode above
  if [ "$PR_MODE" = "true" ] && [ ${#CHANGED_MD_FILES[@]} -eq 0 ]; then
    echo "📝 No .md files changed in this PR - no HTML files need to be checked"
    echo "✅ Exiting successfully as no documentation files were modified"
    
    # Set outputs for no warnings found
    echo "warnings-found=false" >> $GITHUB_OUTPUT
    echo "warning-count=0" >> $GITHUB_OUTPUT
    echo "warning-details=" >> $GITHUB_OUTPUT
    echo "detailed-report=" >> $GITHUB_OUTPUT
    
    exit 0
  fi
fi

# Handle file discovery (both for normal mode and PR mode fallback)
if [ "$PR_MODE" = "true" ]; then
  echo "Found ${#CHANGED_MD_FILES[@]} changed .md file(s):"
  printf '%s\n' "${CHANGED_MD_FILES[@]}"
  
  # Map changed .md files to corresponding .html files
  FILES=()
  for md_file in "${CHANGED_MD_FILES[@]}"; do
    # Convert .md file path to corresponding .html file in the build directory
    # Remove .md extension and add .html
    base_name=$(basename "$md_file" .md)
    
    # Look for the corresponding HTML file in the HTML_PATH
    if [ -f "$HTML_PATH" ]; then
      # HTML_PATH is a single file, only check if it matches
      html_file_name=$(basename "$HTML_PATH" .html)
      if [ "$base_name" = "$html_file_name" ]; then
        FILES+=("$HTML_PATH")
        echo "Mapped $md_file -> $HTML_PATH"
      fi
    else
      # HTML_PATH is a directory, search for corresponding HTML file
      # Try different possible mappings
      possible_paths=(
        "$HTML_PATH/$base_name.html"
        "$HTML_PATH/$(dirname "$md_file")/$base_name.html"
      )
      
      for html_path in "${possible_paths[@]}"; do
        if [ -f "$html_path" ]; then
          FILES+=("$html_path")
          echo "Mapped $md_file -> $html_path"
          break
        fi
      done
      
      # If no exact match found, search recursively
      if ! printf '%s\n' "${FILES[@]}" | grep -q "/$base_name.html"; then
        found_file=$(find "$HTML_PATH" -name "$base_name.html" -type f | head -1)
        if [ -n "$found_file" ]; then
          FILES+=("$found_file")
          echo "Mapped $md_file -> $found_file (found recursively)"
        else
          echo "Warning: No corresponding HTML file found for $md_file (searched for $base_name.html)"
        fi
      fi
    fi
  done
  
  if [ ${#FILES[@]} -eq 0 ]; then
    echo "No HTML files found corresponding to changed .md files"
  else
    echo "Will check ${#FILES[@]} HTML file(s) in PR mode"
  fi
else
  # Normal mode - find all HTML files or use specified file
  if [ -f "$HTML_PATH" ]; then
    # Single file
    if [[ "$HTML_PATH" == *.html ]]; then
      echo "Checking single HTML file: $HTML_PATH"
      FILES=("$HTML_PATH")
    else
      echo "Error: '$HTML_PATH' is not an HTML file"
      exit 1
    fi
  else
    # Directory - find all HTML files
    echo "Scanning all HTML files in directory: $HTML_PATH"
    mapfile -d '' FILES < <(find "$HTML_PATH" -name "*.html" -type f -print0)
  fi
fi

# Create temporary Python script for parsing HTML
cat > /tmp/check_warnings.py << 'EOF'
import re
import sys
import os

def find_warnings_in_cell_outputs(file_path, warning_text):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Find all HTML elements with cell_output in the class attribute
        pattern = r"<([^>]+)\s+class=\"[^\"]*cell_output[^\"]*\"[^>]*>(.*?)</\1>"
        
        matches = []
        
        # Search for cell_output blocks
        for match in re.finditer(pattern, content, re.DOTALL | re.IGNORECASE):
            block_content = match.group(2)
            block_start = match.start()
            
            # Count line number where this block starts
            block_line = content[:block_start].count("\n") + 1
            
            # Search for warning within this block
            if warning_text in block_content:
                # Find specific lines within the block that contain the warning
                block_lines = block_content.split("\n")
                for i, line in enumerate(block_lines):
                    if warning_text in line:
                        actual_line_num = block_line + i
                        # Clean up the line for display (remove extra whitespace, HTML tags)
                        clean_line = re.sub(r"<[^>]+>", "", line).strip()
                        if clean_line:  # Only add non-empty lines
                            matches.append(f"{actual_line_num}:{clean_line}")
        
        # Output results
        for match in matches:
            print(match)
            
    except Exception as e:
        print(f"Error processing file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    file_path = sys.argv[1]
    warning_text = sys.argv[2]
    find_warnings_in_cell_outputs(file_path, warning_text)
EOF

# Search for warnings in HTML files within cell_output elements
for file in "${FILES[@]}"; do
  echo "Checking file: $file"
  
  # Skip warning check if no warnings to check for
  if [ ${#WARNING_ARRAY[@]} -eq 0 ]; then
    echo "No warnings to check for in $file (all excluded)"
    continue
  fi
  
  for warning in "${WARNING_ARRAY[@]}"; do
    # Remove leading/trailing whitespace from warning
    warning=$(echo "$warning" | xargs)
    
    # Run the Python script and capture results
    matches=$(python3 /tmp/check_warnings.py "$file" "$warning" 2>/dev/null || true)
    
    if [ -n "$matches" ]; then
      WARNINGS_FOUND="true"
      count=$(echo "$matches" | wc -l)
      TOTAL_WARNINGS=$((TOTAL_WARNINGS + count))
      
      echo "⚠️  Found $count instance(s) of '$warning' in $file:"
      echo "$matches"
      
      # Add to basic details
      if [ -n "$WARNING_DETAILS" ]; then
        WARNING_DETAILS="$WARNING_DETAILS\n"
      fi
      WARNING_DETAILS="$WARNING_DETAILS$file: $count instance(s) of '$warning'"
      
      # Add to detailed report
      DETAILED_REPORT="$DETAILED_REPORT## $warning in $file\n\n"
      DETAILED_REPORT="$DETAILED_REPORT**Found $count instance(s):**\n\n"
      DETAILED_REPORT="$DETAILED_REPORT\`\`\`\n"
      DETAILED_REPORT="$DETAILED_REPORT$matches\n"
      DETAILED_REPORT="$DETAILED_REPORT\`\`\`\n\n"
    fi
  done
done

# Set outputs
echo "warnings-found=$WARNINGS_FOUND" >> $GITHUB_OUTPUT
echo "warning-count=$TOTAL_WARNINGS" >> $GITHUB_OUTPUT
echo "warning-details<<EOF" >> $GITHUB_OUTPUT
echo -e "$WARNING_DETAILS" >> $GITHUB_OUTPUT
echo "EOF" >> $GITHUB_OUTPUT
echo "detailed-report<<EOF" >> $GITHUB_OUTPUT
echo -e "$DETAILED_REPORT" >> $GITHUB_OUTPUT
echo "EOF" >> $GITHUB_OUTPUT

# Summary
if [ "$WARNINGS_FOUND" = "true" ]; then
  echo "❌ Found $TOTAL_WARNINGS warning(s) in HTML files"
  echo "::error::Found $TOTAL_WARNINGS Python warning(s) in HTML output"
else
  echo "✅ No warnings found in HTML files"
fi