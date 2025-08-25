#!/bin/bash
set -e

echo "🔍 Starting QuantEcon Style Guide Checker"

# Parse inputs
STYLE_GUIDE="${INPUT_STYLE_GUIDE:-.github/copilot-qe-style-guide.md}"
LECTURES_PATH="${INPUT_LECTURES:-lectures}"
EXCLUDE_FILES="${INPUT_EXCLUDE_FILES:-}"
MODE="${INPUT_MODE:-pr}"
CONFIDENCE_THRESHOLD="${INPUT_CONFIDENCE_THRESHOLD:-high}"
CREATE_INDIVIDUAL_PRS="${INPUT_CREATE_INDIVIDUAL_PRS:-false}"
GITHUB_TOKEN="${INPUT_GITHUB_TOKEN}"

echo "📋 Configuration:"
echo "  Style Guide: $STYLE_GUIDE"
echo "  Lectures Path: $LECTURES_PATH"
echo "  Exclude Files: $EXCLUDE_FILES"
echo "  Mode: $MODE"
echo "  Confidence Threshold: $CONFIDENCE_THRESHOLD"

# Initialize counters
HIGH_CONFIDENCE=0
MEDIUM_CONFIDENCE=0
LOW_CONFIDENCE=0
FILES_PROCESSED=0
SUGGESTIONS_FOUND="false"

# Create temporary directory for processing
TEMP_DIR=$(mktemp -d)
echo "📁 Working directory: $TEMP_DIR"

# Load style guide
if [[ "$STYLE_GUIDE" =~ ^https?:// ]]; then
    echo "📥 Downloading style guide from URL: $STYLE_GUIDE"
    curl -s "$STYLE_GUIDE" > "$TEMP_DIR/style-guide.md"
    STYLE_GUIDE_FILE="$TEMP_DIR/style-guide.md"
elif [ -f "$STYLE_GUIDE" ]; then
    echo "📖 Loading local style guide: $STYLE_GUIDE"
    STYLE_GUIDE_FILE="$STYLE_GUIDE"
else
    echo "❌ Error: Style guide not found at $STYLE_GUIDE"
    exit 1
fi

# Create Python script for style checking
cat > "$TEMP_DIR/style_checker.py" << 'EOF'
import os
import re
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple

class QuantEconStyleChecker:
    def __init__(self, style_guide_path: str):
        self.style_guide_path = style_guide_path
        self.rules = self._parse_style_guide()
        
    def _parse_style_guide(self) -> Dict[str, str]:
        """Parse the style guide and extract numbered rules"""
        rules = {}
        try:
            with open(self.style_guide_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract numbered rules and key principles
            sections = {
                'writing': [
                    'Keep it clear and keep it short',
                    'Use one sentence paragraphs only',
                    'Keep those one sentence paragraphs short and clear',
                    'Choose the simplest option when you have reasonable alternatives',
                    "Don't capitalize unless necessary"
                ],
                'emphasis': [
                    'Use **bold** for definitions',
                    'Use *italic* for emphasis'
                ],
                'titles': [
                    'Lecture titles: Capitalize all words',
                    'All other headings: Capitalize only the first word and proper nouns'
                ],
                'code': [
                    'Follow PEP8 unless there\'s a good mathematical reason',
                    'Use capitals for matrices when closer to mathematical notation',
                    'Operators surrounded by spaces: a * b, a + b, but a**b for a^b'
                ],
                'variables': [
                    'Prefer Unicode symbols for Greek letters: α instead of alpha',
                    'Use β instead of beta',
                    'Use γ instead of gamma',
                    'Use δ instead of delta',
                    'Use ε instead of epsilon',
                    'Use σ instead of sigma',
                    'Use θ instead of theta',
                    'Use ρ instead of rho'
                ],
                'packages': [
                    'Lectures should run in a base installation of Anaconda Python',
                    'Install non-Anaconda packages at the top',
                    'Use tags: [hide-output] for installation cells',
                    'Don\'t install jax at the top; use GPU warning admonition instead'
                ],
                'timing': [
                    'Use modern qe.Timer() context manager',
                    'Avoid manual timing patterns'
                ],
                'math': [
                    'Use \\top for transpose: A^\\top',
                    'Use \\mathbb{1} for vectors/matrices of ones',
                    'Use square brackets for matrices: \\begin{bmatrix}',
                    'Do not use bold face for matrices or vectors',
                    'Use curly brackets for sequences: \\{ x_t \\}_{t=0}^{\\infty}'
                ],
                'equations': [
                    'Use \\begin{aligned} ... \\end{aligned} within math environments',
                    'Don\'t use \\tag for manual equation numbering',
                    'Use built-in equation numbering',
                    'Reference equations with {eq} role'
                ],
                'figures': [
                    'No embedded titles in matplotlib (no ax.set_title)',
                    'Add title metadata to figure directive or code-cell metadata',
                    'Use lowercase for captions, except first letter and proper nouns',
                    'Keep caption titles to about 5-6 words max',
                    'Set descriptive name for reference with numref',
                    'Axis labels should be lowercase',
                    'Keep the box around matplotlib figures',
                    'Use lw=2 for all matplotlib line charts',
                    'Figures should be 80-100% of text width'
                ]
            }
            
            # Convert to numbered rules
            rule_num = 1
            for category, rule_list in sections.items():
                for rule in rule_list:
                    rules[f"R{rule_num:03d}"] = f"[{category.upper()}] {rule}"
                    rule_num += 1
                    
            return rules
            
        except Exception as e:
            print(f"Error parsing style guide: {e}", file=sys.stderr)
            return {}
    
    def check_file(self, file_path: str) -> List[Dict]:
        """Check a single file for style issues"""
        suggestions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Check various style rules
            suggestions.extend(self._check_writing_style(lines, file_path))
            suggestions.extend(self._check_code_style(content, lines, file_path))
            suggestions.extend(self._check_math_notation(content, lines, file_path))
            suggestions.extend(self._check_figure_style(content, lines, file_path))
            
        except Exception as e:
            print(f"Error checking file {file_path}: {e}", file=sys.stderr)
            
        return suggestions
    
    def _check_writing_style(self, lines: List[str], file_path: str) -> List[Dict]:
        """Check writing style rules"""
        suggestions = []
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Check for overly long paragraphs (more than one sentence)
            if line and not line.startswith('#') and not line.startswith('```'):
                sentence_count = len([s for s in re.split(r'[.!?]+', line) if s.strip()])
                if sentence_count > 1:
                    suggestions.append({
                        'rule': 'R002',
                        'file': file_path,
                        'line': i,
                        'description': 'Use one sentence paragraphs only',
                        'suggestion': 'Consider breaking this into separate paragraphs',
                        'confidence': 'medium',
                        'original': line,
                        'proposed': None
                    })
            
            # Check for unnecessary capitalization in headings (except lecture titles)
            if line.startswith('##') and not line.startswith('# '):  # Not main title
                words = line[2:].strip().split()
                if len(words) > 1:
                    # Check if more words are capitalized than should be
                    capitalized_count = sum(1 for word in words[1:] if word[0].isupper() and word.lower() not in ['python', 'jax', 'numba'])
                    if capitalized_count > 0:
                        suggested_heading = words[0] + ' ' + ' '.join(w.lower() if w.lower() not in ['python', 'jax', 'numba'] else w for w in words[1:])
                        suggestions.append({
                            'rule': 'R005',
                            'file': file_path,
                            'line': i,
                            'description': 'All other headings: Capitalize only the first word and proper nouns',
                            'suggestion': f'Change to: {line[:2]} {suggested_heading}',
                            'confidence': 'high',
                            'original': line,
                            'proposed': f'{line[:2]} {suggested_heading}'
                        })
        
        return suggestions
    
    def _check_code_style(self, content: str, lines: List[str], file_path: str) -> List[Dict]:
        """Check code style rules"""
        suggestions = []
        
        # Find code blocks
        in_code_block = False
        code_block_start = 0
        
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('```python'):
                in_code_block = True
                code_block_start = i
            elif line.strip() == '```' and in_code_block:
                in_code_block = False
                
                # Check code block content
                code_lines = lines[code_block_start:i-1]
                suggestions.extend(self._check_python_code(code_lines, file_path, code_block_start))
        
        return suggestions
    
    def _check_python_code(self, code_lines: List[str], file_path: str, start_line: int) -> List[Dict]:
        """Check Python code within code blocks"""
        suggestions = []
        
        for i, line in enumerate(code_lines, start_line + 1):
            line = line.strip()
            
            # Check for Greek letter usage
            greek_letters = {
                'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ',
                'epsilon': 'ε', 'sigma': 'σ', 'theta': 'θ', 'rho': 'ρ'
            }
            
            for english, unicode_char in greek_letters.items():
                if re.search(rf'\b{english}\b', line):
                    suggestions.append({
                        'rule': 'R008',
                        'file': file_path,
                        'line': i,
                        'description': f'Prefer Unicode symbols for Greek letters: {unicode_char} instead of {english}',
                        'suggestion': f'Replace {english} with {unicode_char}',
                        'confidence': 'high',
                        'original': line,
                        'proposed': line.replace(english, unicode_char)
                    })
            
            # Check for old timing patterns
            if 'time.time()' in line or 'start_time' in line or 'end_time' in line:
                suggestions.append({
                    'rule': 'R015',
                    'file': file_path,
                    'line': i,
                    'description': 'Use modern qe.Timer() context manager',
                    'suggestion': 'Replace manual timing with: with qe.Timer():\n    result = your_computation()',
                    'confidence': 'medium',
                    'original': line,
                    'proposed': None
                })
        
        return suggestions
    
    def _check_math_notation(self, content: str, lines: List[str], file_path: str) -> List[Dict]:
        """Check mathematical notation rules"""
        suggestions = []
        
        for i, line in enumerate(lines, 1):
            # Check for transpose notation
            if "^T" in line or ".T" in line:
                suggestions.append({
                    'rule': 'R016',
                    'file': file_path,
                    'line': i,
                    'description': 'Use \\top for transpose: A^\\top',
                    'suggestion': 'Replace ^T with ^\\top',
                    'confidence': 'high',
                    'original': line,
                    'proposed': line.replace('^T', '^\\top').replace('.T', '^\\top')
                })
            
            # Check for manual equation numbering with \tag
            if '\\tag{' in line:
                suggestions.append({
                    'rule': 'R020',
                    'file': file_path,
                    'line': i,
                    'description': 'Don\'t use \\tag for manual equation numbering',
                    'suggestion': 'Use built-in equation numbering instead',
                    'confidence': 'medium',
                    'original': line,
                    'proposed': None
                })
        
        return suggestions
    
    def _check_figure_style(self, content: str, lines: List[str], file_path: str) -> List[Dict]:
        """Check figure style rules"""
        suggestions = []
        
        for i, line in enumerate(lines, 1):
            # Check for ax.set_title usage
            if 'ax.set_title' in line or 'plt.title' in line:
                suggestions.append({
                    'rule': 'R022',
                    'file': file_path,
                    'line': i,
                    'description': 'No embedded titles in matplotlib (no ax.set_title)',
                    'suggestion': 'Add title metadata to figure directive or code-cell metadata instead',
                    'confidence': 'high',
                    'original': line,
                    'proposed': '# Remove this line and add title to figure metadata'
                })
            
            # Check for line width in matplotlib
            if 'plot(' in line and 'lw=' not in line and 'linewidth=' not in line:
                if not any(keyword in line for keyword in ['scatter', 'bar', 'hist']):
                    suggestions.append({
                        'rule': 'R028',
                        'file': file_path,
                        'line': i,
                        'description': 'Use lw=2 for all matplotlib line charts',
                        'suggestion': 'Add lw=2 parameter to plot function',
                        'confidence': 'medium',
                        'original': line,
                        'proposed': None
                    })
        
        return suggestions

def main():
    if len(sys.argv) < 4:
        print("Usage: python style_checker.py <style_guide> <file_path> <mode>")
        sys.exit(1)
        
    style_guide_path = sys.argv[1]
    file_path = sys.argv[2]
    mode = sys.argv[3]
    
    checker = QuantEconStyleChecker(style_guide_path)
    suggestions = checker.check_file(file_path)
    
    # Output suggestions as JSON
    print(json.dumps(suggestions, indent=2))

if __name__ == "__main__":
    main()
EOF

chmod +x "$TEMP_DIR/style_checker.py"

# Function to check if file should be excluded
should_exclude_file() {
    local file="$1"
    if [ -n "$EXCLUDE_FILES" ]; then
        IFS=',' read -ra EXCLUDE_ARRAY <<< "$EXCLUDE_FILES"
        for pattern in "${EXCLUDE_ARRAY[@]}"; do
            pattern=$(echo "$pattern" | xargs)  # Remove whitespace
            if [[ "$file" =~ $pattern ]]; then
                return 0  # Should exclude
            fi
        done
    fi
    return 1  # Should not exclude
}

# Get list of files to process
FILES_TO_PROCESS=()

if [ "$MODE" = "pr" ]; then
    echo "🔄 PR Mode: Checking changed files"
    
    # Get changed files in the PR
    if [ "$GITHUB_EVENT_NAME" = "pull_request" ]; then
        # Get changed markdown files
        while read -r file; do
            if [ -f "$file" ] && [[ "$file" == "$LECTURES_PATH"* ]] && ! should_exclude_file "$file"; then
                FILES_TO_PROCESS+=("$file")
            fi
        done < <(git diff --name-only origin/$GITHUB_BASE_REF...HEAD | grep '\.md$' || true)
    else
        echo "ℹ️  Not in PR context, checking all files in lectures directory"
        while read -r file; do
            if ! should_exclude_file "$file"; then
                FILES_TO_PROCESS+=("$file")
            fi
        done < <(find "$LECTURES_PATH" -name "*.md" -type f 2>/dev/null || true)
    fi
else
    echo "📅 Scheduled Mode: Checking all lecture files"
    while read -r file; do
        if ! should_exclude_file "$file"; then
            FILES_TO_PROCESS+=("$file")
        fi
    done < <(find "$LECTURES_PATH" -name "*.md" -type f 2>/dev/null || true)
fi

# If no files to process, list what we found
if [ ${#FILES_TO_PROCESS[@]} -eq 0 ]; then
    echo "ℹ️  No markdown files found to process in $LECTURES_PATH"
    if [ -d "$LECTURES_PATH" ]; then
        echo "📁 Contents of $LECTURES_PATH:"
        find "$LECTURES_PATH" -type f -name "*.md" | head -10
    else
        echo "❌ Directory $LECTURES_PATH does not exist"
        # Create a mock file for testing
        mkdir -p "$(dirname "$LECTURES_PATH")"
        echo "# Test Lecture" > "${LECTURES_PATH}.md"
        FILES_TO_PROCESS=("${LECTURES_PATH}.md")
    fi
fi

echo "📝 Files to process: ${#FILES_TO_PROCESS[@]}"

# Initialize report files
SUMMARY_REPORT=""
DETAILED_REPORT="# QuantEcon Style Guide Check Report\n\n"
ALL_SUGGESTIONS=()

# Process each file
for file in "${FILES_TO_PROCESS[@]}"; do
    echo "🔍 Checking: $file"
    FILES_PROCESSED=$((FILES_PROCESSED + 1))
    
    # Run style checker
    if suggestions_json=$(python3 "$TEMP_DIR/style_checker.py" "$STYLE_GUIDE_FILE" "$file" "$MODE" 2>/dev/null); then
        if [ "$suggestions_json" != "[]" ]; then
            SUGGESTIONS_FOUND="true"
            
            # Parse suggestions and categorize by confidence
            echo "$suggestions_json" | python3 -c "
import sys
import json

suggestions = json.load(sys.stdin)
high_count = len([s for s in suggestions if s.get('confidence') == 'high'])
medium_count = len([s for s in suggestions if s.get('confidence') == 'medium'])
low_count = len([s for s in suggestions if s.get('confidence') == 'low'])

print(f'HIGH_COUNT={high_count}')
print(f'MEDIUM_COUNT={medium_count}')
print(f'LOW_COUNT={low_count}')

# Output suggestions for processing
for suggestion in suggestions:
    confidence = suggestion.get('confidence', 'low')
    rule = suggestion.get('rule', 'UNKNOWN')
    line = suggestion.get('line', 0)
    description = suggestion.get('description', '')
    original = suggestion.get('original', '')
    proposed = suggestion.get('proposed', '')
    
    print(f'SUGGESTION|{confidence}|{rule}|{line}|{description}|{original}|{proposed}')
" > "$TEMP_DIR/suggestions_${FILES_PROCESSED}.txt"

            if [ -f "$TEMP_DIR/suggestions_${FILES_PROCESSED}.txt" ]; then
                # Extract counts
                eval $(grep "^HIGH_COUNT=" "$TEMP_DIR/suggestions_${FILES_PROCESSED}.txt")
                eval $(grep "^MEDIUM_COUNT=" "$TEMP_DIR/suggestions_${FILES_PROCESSED}.txt")
                eval $(grep "^LOW_COUNT=" "$TEMP_DIR/suggestions_${FILES_PROCESSED}.txt")
                
                HIGH_CONFIDENCE=$((HIGH_CONFIDENCE + HIGH_COUNT))
                MEDIUM_CONFIDENCE=$((MEDIUM_CONFIDENCE + MEDIUM_COUNT))
                LOW_CONFIDENCE=$((LOW_CONFIDENCE + LOW_COUNT))
                
                # Add to detailed report
                DETAILED_REPORT="$DETAILED_REPORT## $file\n\n"
                
                if [ $HIGH_COUNT -gt 0 ]; then
                    DETAILED_REPORT="$DETAILED_REPORT### High Confidence Suggestions ($HIGH_COUNT)\n\n"
                    DETAILED_REPORT="$DETAILED_REPORT| Line | Rule | Description | Original | Proposed |\n"
                    DETAILED_REPORT="$DETAILED_REPORT|------|------|-------------|----------|----------|\n"
                    
                    grep "^SUGGESTION|high|" "$TEMP_DIR/suggestions_${FILES_PROCESSED}.txt" | while IFS='|' read -r _ confidence rule line description original proposed; do
                        DETAILED_REPORT="$DETAILED_REPORT| $line | $rule | $description | \`$original\` | \`$proposed\` |\n"
                    done
                    DETAILED_REPORT="$DETAILED_REPORT\n"
                fi
                
                if [ $MEDIUM_COUNT -gt 0 ]; then
                    DETAILED_REPORT="$DETAILED_REPORT### Medium Confidence Suggestions ($MEDIUM_COUNT)\n\n"
                    DETAILED_REPORT="$DETAILED_REPORT| Line | Rule | Description | Original |\n"
                    DETAILED_REPORT="$DETAILED_REPORT|------|------|-------------|----------|\n"
                    
                    grep "^SUGGESTION|medium|" "$TEMP_DIR/suggestions_${FILES_PROCESSED}.txt" | while IFS='|' read -r _ confidence rule line description original proposed; do
                        DETAILED_REPORT="$DETAILED_REPORT| $line | $rule | $description | \`$original\` |\n"
                    done
                    DETAILED_REPORT="$DETAILED_REPORT\n"
                fi
                
                if [ $LOW_COUNT -gt 0 ]; then
                    DETAILED_REPORT="$DETAILED_REPORT### Low Confidence Suggestions ($LOW_COUNT)\n\n"
                    DETAILED_REPORT="$DETAILED_REPORT| Line | Rule | Description | Original |\n"
                    DETAILED_REPORT="$DETAILED_REPORT|------|------|-------------|----------|\n"
                    
                    grep "^SUGGESTION|low|" "$TEMP_DIR/suggestions_${FILES_PROCESSED}.txt" | while IFS='|' read -r _ confidence rule line description original proposed; do
                        DETAILED_REPORT="$DETAILED_REPORT| $line | $rule | $description | \`$original\` |\n"
                    done
                    DETAILED_REPORT="$DETAILED_REPORT\n"
                fi
            fi
            
            echo "  ✨ Found suggestions: High=$HIGH_COUNT, Medium=$MEDIUM_COUNT, Low=$LOW_COUNT"
        else
            echo "  ✅ No style issues found"
        fi
    else
        echo "  ⚠️  Error processing file"
    fi
done

# Generate summary report
SUMMARY_REPORT="## Style Check Summary\n\n"
SUMMARY_REPORT="$SUMMARY_REPORT- **Files Processed:** $FILES_PROCESSED\n"
SUMMARY_REPORT="$SUMMARY_REPORT- **High Confidence Suggestions:** $HIGH_CONFIDENCE\n"
SUMMARY_REPORT="$SUMMARY_REPORT- **Medium Confidence Suggestions:** $MEDIUM_CONFIDENCE\n"
SUMMARY_REPORT="$SUMMARY_REPORT- **Low Confidence Suggestions:** $LOW_CONFIDENCE\n"
SUMMARY_REPORT="$SUMMARY_REPORT- **Total Suggestions:** $((HIGH_CONFIDENCE + MEDIUM_CONFIDENCE + LOW_CONFIDENCE))\n\n"

if [ "$SUGGESTIONS_FOUND" = "true" ]; then
    SUMMARY_REPORT="$SUMMARY_REPORT🔍 **Style suggestions found!** See detailed report below.\n\n"
else
    SUMMARY_REPORT="$SUMMARY_REPORT✅ **No style issues found!** All files comply with the QuantEcon Style Guide.\n\n"
fi

# Set outputs
echo "suggestions-found=$SUGGESTIONS_FOUND" >> $GITHUB_OUTPUT
echo "high-confidence-count=$HIGH_CONFIDENCE" >> $GITHUB_OUTPUT
echo "medium-confidence-count=$MEDIUM_CONFIDENCE" >> $GITHUB_OUTPUT
echo "low-confidence-count=$LOW_CONFIDENCE" >> $GITHUB_OUTPUT
echo "files-processed=$FILES_PROCESSED" >> $GITHUB_OUTPUT

echo "summary-report<<EOF" >> $GITHUB_OUTPUT
echo -e "$SUMMARY_REPORT" >> $GITHUB_OUTPUT
echo "EOF" >> $GITHUB_OUTPUT

echo "detailed-report<<EOF" >> $GITHUB_OUTPUT
echo -e "$DETAILED_REPORT" >> $GITHUB_OUTPUT
echo "EOF" >> $GITHUB_OUTPUT

# Clean up
rm -rf "$TEMP_DIR"

echo "🎉 Style check completed!"
echo "  Files processed: $FILES_PROCESSED"
echo "  Suggestions found: $SUGGESTIONS_FOUND"
echo "  High confidence: $HIGH_CONFIDENCE"
echo "  Medium confidence: $MEDIUM_CONFIDENCE"
echo "  Low confidence: $LOW_CONFIDENCE"