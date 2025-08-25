#!/usr/bin/env python3
"""
Style Guide Checker for QuantEcon Lectures
==========================================

AI-powered style guide compliance checker that reviews MyST Markdown files
for adherence to QuantEcon style guidelines.

Supports two modes:
1. PR mode: Reviews only changed files in a pull request, provides all suggestions as GitHub review comments
2. Full mode: Reviews all files in the specified directory, auto-commits high-confidence changes

Features:
- AI-powered style analysis using OpenAI API
- Confidence-based categorization of suggestions
- In PR mode: GitHub suggestions for high-confidence changes, review comments for others
- In Full mode: Automatic commits for high-confidence changes
- PR review suggestions for medium/low confidence changes
- Regex-based file exclusion
"""

import os
import sys
import re
import json
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Import required libraries
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from github import Github
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False

try:
    import git
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False

# Try to import OpenAI (optional)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class ConfidenceLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class StyleSuggestion:
    """Represents a style suggestion for a file"""
    file_path: str
    line_number: int
    original_text: str
    suggested_text: str
    explanation: str
    confidence: ConfidenceLevel
    rule_category: str


class StyleGuideChecker:
    """Main class for style guide checking functionality"""
    
    def __init__(self):
        self.setup_logging()
        self.load_environment()
        self.setup_github()
        self.setup_openai()
        self.load_style_guide()
        
    def setup_logging(self):
        """Configure logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def load_environment(self):
        """Load environment variables and inputs"""
        self.style_guide_path = os.getenv('INPUT_STYLE_GUIDE', '.github/copilot-qe-style-guide.md')
        self.docs_path = os.getenv('INPUT_DOCS', 'lectures')
        self.exclude_files = os.getenv('INPUT_EXCLUDE_FILES', '')
        self.mode = os.getenv('INPUT_MODE', 'pr')
        self.confidence_threshold = ConfidenceLevel(os.getenv('INPUT_CONFIDENCE_THRESHOLD', 'high'))
        self.max_suggestions = int(os.getenv('INPUT_MAX_SUGGESTIONS', '10'))
        self.create_pr = os.getenv('INPUT_CREATE_PR', 'true').lower() == 'true'
        
        # GitHub environment
        self.github_token = os.getenv('INPUT_GITHUB_TOKEN')
        self.openai_api_key = os.getenv('INPUT_OPENAI_API_KEY')
        self.github_repository = os.getenv('GITHUB_REPOSITORY')
        self.github_event_name = os.getenv('GITHUB_EVENT_NAME')
        self.github_head_ref = os.getenv('GITHUB_HEAD_REF')
        self.github_base_ref = os.getenv('GITHUB_BASE_REF')
        self.github_sha = os.getenv('GITHUB_SHA')
        self.github_ref = os.getenv('GITHUB_REF')
        self.github_actor = os.getenv('GITHUB_ACTOR')
        
        if not self.github_token:
            raise ValueError("GitHub token is required")
            
    def setup_github(self):
        """Setup GitHub API client"""
        if not GITHUB_AVAILABLE:
            self.logger.warning("GitHub library not available - some features will be limited")
            self.github_client = None
            self.repo = None
            return
            
        try:
            self.github_client = Github(self.github_token)
            self.repo = self.github_client.get_repo(self.github_repository)
            self.logger.info(f"Connected to GitHub repository: {self.github_repository}")
        except Exception as e:
            self.logger.error(f"Failed to setup GitHub client: {e}")
            self.github_client = None
            self.repo = None
            
    def setup_openai(self):
        """Setup OpenAI API client if available"""
        if self.openai_api_key and OPENAI_AVAILABLE:
            openai.api_key = self.openai_api_key
            self.openai_enabled = True
            self.logger.info("OpenAI API configured")
        else:
            self.openai_enabled = False
            self.logger.warning("OpenAI API not available - using rule-based checking only")
            
    def load_style_guide(self):
        """Load the style guide content"""
        try:
            # Check if it's a URL or local path
            if self.style_guide_path.startswith('http'):
                if not REQUESTS_AVAILABLE:
                    raise ImportError("requests library not available for URL loading")
                response = requests.get(self.style_guide_path)
                response.raise_for_status()
                self.style_guide_content = response.text
            else:
                # Local path
                style_guide_file = Path(self.style_guide_path)
                if not style_guide_file.exists():
                    raise FileNotFoundError(f"Style guide not found: {self.style_guide_path}")
                self.style_guide_content = style_guide_file.read_text()
                
            self.logger.info(f"Loaded style guide from: {self.style_guide_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to load style guide: {e}")
            # Use a minimal default style guide for testing
            self.style_guide_content = "Use Unicode Greek letters (α, β, γ) instead of spelled out names."
            self.logger.warning("Using minimal default style guide")
            
    def get_files_to_review(self) -> List[str]:
        """Get list of files to review based on mode"""
        if self.mode == 'pr':
            return self.get_changed_files()
        else:
            return self.get_all_markdown_files()
            
    def get_changed_files(self) -> List[str]:
        """Get files changed in the current PR"""
        try:
            if self.github_event_name != 'pull_request' or not self.repo:
                self.logger.warning("Not in PR context or GitHub not available, falling back to all files")
                return self.get_all_markdown_files()
                
            # Get PR number from context
            pr_number = self.get_pr_number()
            if not pr_number:
                return self.get_all_markdown_files()
                
            pr = self.repo.get_pull(pr_number)
            changed_files = []
            
            for file in pr.get_files():
                if file.filename.endswith('.md') and self.should_include_file(file.filename):
                    changed_files.append(file.filename)
                    
            self.logger.info(f"Found {len(changed_files)} changed markdown files")
            return changed_files
            
        except Exception as e:
            self.logger.error(f"Failed to get changed files: {e}")
            return self.get_all_markdown_files()
            
    def get_pr_number(self) -> Optional[int]:
        """Extract PR number from GitHub context"""
        try:
            # Try to get from GITHUB_REF
            if self.github_ref and 'pull' in self.github_ref:
                match = re.search(r'refs/pull/(\d+)/merge', self.github_ref)
                if match:
                    return int(match.group(1))
                    
            # Try to get from event file
            event_path = os.getenv('GITHUB_EVENT_PATH')
            if event_path and os.path.exists(event_path):
                with open(event_path) as f:
                    event_data = json.load(f)
                    if 'pull_request' in event_data:
                        return event_data['pull_request']['number']
                        
        except Exception as e:
            self.logger.warning(f"Could not determine PR number: {e}")
            
        return None
        
    def get_all_markdown_files(self) -> List[str]:
        """Get all markdown files in the docs directory"""
        docs_path = Path(self.docs_path)
        if not docs_path.exists():
            self.logger.warning(f"Docs path does not exist: {self.docs_path}")
            return []
            
        markdown_files = []
        for md_file in docs_path.rglob('*.md'):
            rel_path = str(md_file.relative_to('.'))
            if self.should_include_file(rel_path):
                markdown_files.append(rel_path)
                
        self.logger.info(f"Found {len(markdown_files)} markdown files")
        return markdown_files
        
    def should_include_file(self, file_path: str) -> bool:
        """Check if file should be included based on exclusion patterns"""
        if not self.exclude_files:
            return True
            
        exclude_patterns = [p.strip() for p in self.exclude_files.split(',')]
        for pattern in exclude_patterns:
            if pattern and re.search(pattern, file_path):
                self.logger.debug(f"Excluding file: {file_path} (matches pattern: {pattern})")
                return False
                
        return True
        
    def analyze_file_with_ai(self, file_path: str, content: str) -> List[StyleSuggestion]:
        """Analyze file content using AI for style compliance"""
        if not hasattr(self, 'openai_enabled') or not self.openai_enabled:
            return self.analyze_file_with_rules(file_path, content)
            
        try:
            prompt = self.build_ai_prompt(content)
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert technical writer and educator specializing in QuantEcon style guidelines. Analyze the provided MyST Markdown content for compliance with the style guide and provide specific, actionable suggestions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            return self.parse_ai_response(file_path, response.choices[0].message.content)
            
        except Exception as e:
            self.logger.error(f"AI analysis failed for {file_path}: {e}")
            return self.analyze_file_with_rules(file_path, content)
            
    def build_ai_prompt(self, content: str) -> str:
        """Build prompt for AI analysis"""
        return f"""
Please analyze the following MyST Markdown content for compliance with the QuantEcon style guide.

STYLE GUIDE:
{self.style_guide_content}

CONTENT TO ANALYZE:
{content}

Please provide suggestions in the following JSON format:
{{
    "suggestions": [
        {{
            "line_number": <number>,
            "original_text": "<exact text that needs changing>",
            "suggested_text": "<suggested replacement>",
            "explanation": "<why this change is needed>",
            "confidence": "<high|medium|low>",
            "rule_category": "<which style rule category this relates to>"
        }}
    ]
}}

Focus on:
1. Writing conventions (clarity, conciseness, paragraph structure)
2. Code style (PEP8, variable naming, Unicode symbols)
3. Math notation (LaTeX formatting, equation numbering)
4. Figure formatting (captions, references, matplotlib settings)
5. Document structure (headings, linking, citations)

Only suggest changes that clearly violate the style guide. Be conservative with suggestions.
Limit to {self.max_suggestions} suggestions maximum.
"""

    def parse_ai_response(self, file_path: str, response: str) -> List[StyleSuggestion]:
        """Parse AI response into StyleSuggestion objects"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                self.logger.warning(f"No JSON found in AI response for {file_path}")
                return []
                
            data = json.loads(json_match.group())
            suggestions = []
            
            for suggestion_data in data.get('suggestions', []):
                suggestion = StyleSuggestion(
                    file_path=file_path,
                    line_number=suggestion_data.get('line_number', 1),
                    original_text=suggestion_data.get('original_text', ''),
                    suggested_text=suggestion_data.get('suggested_text', ''),
                    explanation=suggestion_data.get('explanation', ''),
                    confidence=ConfidenceLevel(suggestion_data.get('confidence', 'low')),
                    rule_category=suggestion_data.get('rule_category', 'general')
                )
                suggestions.append(suggestion)
                
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Failed to parse AI response for {file_path}: {e}")
            return []
            
    def analyze_file_with_rules(self, file_path: str, content: str) -> List[StyleSuggestion]:
        """Analyze file using rule-based approach as fallback"""
        suggestions = []
        lines = content.split('\n')
        
        # Rule 1: Check for Greek letter usage in code contexts
        greek_replacements = {
            'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ',
            'epsilon': 'ε', 'sigma': 'σ', 'theta': 'θ', 'rho': 'ρ'
        }
        
        for i, line in enumerate(lines):
            # Only check lines that contain code (function definitions, equations)
            if ('def ' in line or '=' in line) and any(f'{english}' in line for english in greek_replacements.keys()):
                for english, unicode_char in greek_replacements.items():
                    # Look for the English word as a standalone parameter/variable
                    import re
                    pattern = r'\b' + english + r'\b'
                    if re.search(pattern, line):
                        new_line = re.sub(pattern, unicode_char, line)
                        if new_line != line:
                            suggestion = StyleSuggestion(
                                file_path=file_path,
                                line_number=i + 1,
                                original_text=line.strip(),
                                suggested_text=new_line.strip(),
                                explanation=f"Use Unicode {unicode_char} instead of '{english}' for better mathematical notation",
                                confidence=ConfidenceLevel.HIGH,
                                rule_category="variable_naming"
                            )
                            suggestions.append(suggestion)
                    
        # Rule 2: Check for capitalization in headings
        for i, line in enumerate(lines):
            if line.startswith('#') and not line.startswith('# '):
                continue
            if line.startswith('#'):
                heading_text = line.lstrip('#').strip()
                # Check if it's a lecture title (main heading)
                if line.startswith('# '):
                    # Should be title case
                    words = heading_text.split()
                    title_case = ' '.join(word.capitalize() for word in words)
                    if heading_text != title_case:
                        suggestion = StyleSuggestion(
                            file_path=file_path,
                            line_number=i + 1,
                            original_text=line,
                            suggested_text=f"# {title_case}",
                            explanation="Lecture titles should use title case (capitalize all words)",
                            confidence=ConfidenceLevel.MEDIUM,
                            rule_category="titles_headings"
                        )
                        suggestions.append(suggestion)
                        
        # Rule 3: Check for manual timing patterns
        for i, line in enumerate(lines):
            if 'time.time()' in line and i < len(lines) - 3:
                # Look for manual timing pattern in next few lines
                following_lines = '\n'.join(lines[i:i+5])
                if 'start_time' in following_lines and 'end_time' in following_lines:
                    suggestion = StyleSuggestion(
                        file_path=file_path,
                        line_number=i + 1,
                        original_text=line,
                        suggested_text="with qe.Timer():",
                        explanation="Use modern qe.Timer() context manager instead of manual timing",
                        confidence=ConfidenceLevel.HIGH,
                        rule_category="performance_timing"
                    )
                    suggestions.append(suggestion)
                    
        return suggestions[:self.max_suggestions]
        
    def apply_high_confidence_changes(self, suggestions: List[StyleSuggestion]) -> int:
        """Apply high confidence changes directly to files"""
        changes_made = 0
        
        # Group suggestions by file
        file_suggestions = {}
        for suggestion in suggestions:
            if suggestion.confidence == ConfidenceLevel.HIGH:
                if suggestion.file_path not in file_suggestions:
                    file_suggestions[suggestion.file_path] = []
                file_suggestions[suggestion.file_path].append(suggestion)
                
        for file_path, suggestions_list in file_suggestions.items():
            try:
                # Read file content
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                # Apply changes (in reverse line order to maintain line numbers)
                lines = content.split('\n')
                suggestions_list.sort(key=lambda x: x.line_number, reverse=True)
                
                for suggestion in suggestions_list:
                    if suggestion.line_number <= len(lines):
                        line_idx = suggestion.line_number - 1
                        current_line = lines[line_idx]
                        # Only apply if the original text matches (trimmed for safety)
                        if current_line.strip() == suggestion.original_text or suggestion.original_text in current_line:
                            lines[line_idx] = suggestion.suggested_text
                            changes_made += 1
                            self.logger.info(f"Applied change to {file_path}:{suggestion.line_number}")
                        else:
                            self.logger.warning(f"Skipping change to {file_path}:{suggestion.line_number} - line content doesn't match")
                # Write back to file
                with open(file_path, 'w') as f:
                    f.write('\n'.join(lines))
                    
            except Exception as e:
                self.logger.error(f"Failed to apply changes to {file_path}: {e}")
                
        return changes_made
        
    def create_pr_review_suggestions(self, suggestions: List[StyleSuggestion]):
        """Create PR review suggestions for all confidence levels using GitHub suggestions"""
        if self.github_event_name != 'pull_request' or not self.repo:
            self.logger.info("Not in PR context or GitHub not available, skipping review suggestions")
            return
            
        try:
            pr_number = self.get_pr_number()
            if not pr_number:
                return
                
            pr = self.repo.get_pull(pr_number)
            
            # Group suggestions by file
            file_suggestions = {}
            for suggestion in suggestions:
                if suggestion.file_path not in file_suggestions:
                    file_suggestions[suggestion.file_path] = []
                file_suggestions[suggestion.file_path].append(suggestion)
                    
            # Create review comments
            review_comments = []
            for file_path, suggestions_list in file_suggestions.items():
                for suggestion in suggestions_list:
                    if suggestion.confidence == ConfidenceLevel.HIGH:
                        # Use GitHub suggestion format for high-confidence changes
                        comment_body = f"""
**Style Guide Suggestion ({suggestion.confidence.value} confidence)**

{suggestion.explanation}

**Rule category:** {suggestion.rule_category}

```suggestion
{suggestion.suggested_text}
```
"""
                    else:
                        # Use regular comment format for medium/low confidence
                        comment_body = f"""
**Style Guide Suggestion ({suggestion.confidence.value} confidence)**

{suggestion.explanation}

**Suggested change:**
```markdown
{suggestion.suggested_text}
```

**Rule category:** {suggestion.rule_category}
"""
                    review_comments.append({
                        'path': suggestion.file_path,
                        'line': suggestion.line_number,
                        'body': comment_body
                    })
                    
            if review_comments:
                pr.create_review(
                    body="Style guide review completed. High-confidence suggestions are provided as GitHub suggestions that you can apply with one click. Please review all suggestions below.",
                    event="COMMENT",
                    comments=review_comments
                )
                self.logger.info(f"Created {len(review_comments)} review suggestions")
                
        except Exception as e:
            self.logger.error(f"Failed to create PR review suggestions: {e}")
            
    def create_pr_comment_summary(self, suggestions: List[StyleSuggestion], files_reviewed: int, changes_made: int = 0):
        """Create a summary comment on the PR"""
        if self.github_event_name != 'pull_request' or not self.repo:
            self.logger.info("Not in PR context or GitHub not available, skipping PR comment")
            return
            
        try:
            pr_number = self.get_pr_number()
            if not pr_number:
                return
                
            pr = self.repo.get_pull(pr_number)
            
            high_conf = len([s for s in suggestions if s.confidence == ConfidenceLevel.HIGH])
            medium_conf = len([s for s in suggestions if s.confidence == ConfidenceLevel.MEDIUM])
            low_conf = len([s for s in suggestions if s.confidence == ConfidenceLevel.LOW])
            
            summary = f"""
## 📝 Style Guide Review Summary

**Files reviewed:** {files_reviewed}
**Total suggestions:** {len(suggestions)}

**Suggestions provided:**
- 🔥 **{high_conf}** high-confidence suggestions (GitHub suggestions - click to apply)
- ⚠️ **{medium_conf}** medium-confidence suggestions  
- 💡 **{low_conf}** low-confidence suggestions

**Suggestion breakdown:**
- **High confidence**: Ready-to-apply suggestions using GitHub's suggestion feature
- **Medium confidence**: Recommended changes that may need minor adjustments
- **Low confidence**: Optional improvements for consideration

All suggestions are based on the [QuantEcon Style Guide]({self.style_guide_path}). High-confidence suggestions can be applied with a single click using GitHub's suggestion feature for transparency and reviewer control.

---
*Generated by [Style Guide Checker Action](https://github.com/QuantEcon/meta/.github/actions/style-guide-checker)*
"""
            
            pr.create_issue_comment(summary)
            self.logger.info("Created PR summary comment")
            
        except Exception as e:
            self.logger.error(f"Failed to create PR summary comment: {e}")
            
    def set_outputs(self, files_reviewed: int, suggestions_made: int, changes_made: int, pr_url: str = ""):
        """Set GitHub Action outputs"""
        github_output = os.getenv('GITHUB_OUTPUT')
        if github_output:
            with open(github_output, 'a') as f:
                f.write(f"files-reviewed={files_reviewed}\n")
                f.write(f"suggestions-made={suggestions_made}\n")
                f.write(f"high-confidence-changes={changes_made}\n")
                f.write(f"pr-url={pr_url}\n")
                f.write(f"review-summary=Reviewed {files_reviewed} files, made {suggestions_made} suggestions, auto-applied {changes_made} high-confidence changes\n")
                
    def run(self):
        """Main execution method"""
        try:
            self.logger.info(f"Starting style guide checker in {self.mode} mode")
            
            # Get files to review
            files_to_review = self.get_files_to_review()
            if not files_to_review:
                self.logger.info("No files to review")
                self.set_outputs(0, 0, 0)
                return
                
            all_suggestions = []
            
            # Analyze each file
            for file_path in files_to_review:
                try:
                    self.logger.info(f"Analyzing file: {file_path}")
                    
                    with open(file_path, 'r') as f:
                        content = f.read()
                        
                    suggestions = self.analyze_file_with_ai(file_path, content)
                    all_suggestions.extend(suggestions)
                    
                    self.logger.info(f"Found {len(suggestions)} suggestions for {file_path}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to analyze {file_path}: {e}")
                    
            changes_made = 0
            
            # Handle suggestions based on mode
            if self.mode == 'pr':
                # In PR mode, create review suggestions for all confidence levels
                # High-confidence suggestions will use GitHub's suggestion feature
                self.create_pr_review_suggestions(all_suggestions)
                self.create_pr_comment_summary(all_suggestions, len(files_to_review))
                self.logger.info("PR mode: All suggestions provided as review comments with GitHub suggestions for high-confidence changes")
                
            else:
                # In full mode, still apply high confidence changes and commit them
                if self.confidence_threshold in [ConfidenceLevel.HIGH]:
                    changes_made = self.apply_high_confidence_changes(all_suggestions)
                    
                    # Commit changes if any were made
                    if changes_made > 0:
                        self.commit_changes(changes_made)
                        
                self.logger.info(f"Full mode: Applied {changes_made} high-confidence changes")
                
            # Set outputs
            self.set_outputs(len(files_to_review), len(all_suggestions), changes_made)
            
            self.logger.info(f"Style guide check completed: {len(files_to_review)} files, {len(all_suggestions)} suggestions, {changes_made} changes")
            
        except Exception as e:
            self.logger.error(f"Style guide checker failed: {e}")
            sys.exit(1)
            
    def commit_changes(self, changes_made: int):
        """Commit any changes made by the style checker"""
        try:
            # Configure git
            subprocess.run(['git', 'config', 'user.name', 'Style Guide Checker'], check=True)
            subprocess.run(['git', 'config', 'user.email', 'style-checker@quantecon.org'], check=True)
            
            # Add and commit changes
            subprocess.run(['git', 'add', '.'], check=True)
            
            commit_message = f"Apply {changes_made} high-confidence style guide suggestions\n\nAuto-applied by Style Guide Checker action"
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            self.logger.info(f"Committed {changes_made} style guide changes")
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to commit changes: {e}")


def main():
    """Main entry point"""
    checker = StyleGuideChecker()
    checker.run()


if __name__ == '__main__':
    main()