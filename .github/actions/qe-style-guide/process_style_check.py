#!/usr/bin/env python3
"""
QuantEcon Style Guide Checker
AI-powered style guide checking and suggestions for QuantEcon content
"""

import json
import os
import re
import sys
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
try:
    import openai
except ImportError:
    openai = None

try:
    import git
except ImportError:
    git = None

class StyleGuideChecker:
    def __init__(self):
        self.github_token = os.environ.get('INPUT_GITHUB_TOKEN')
        self.style_guide_path = os.environ.get('INPUT_STYLE_GUIDE', '.github/copilot-qe-style-guide.md')
        self.docs_dir = os.environ.get('INPUT_DOCS', 'lectures/')
        self.extensions = [ext.strip() for ext in os.environ.get('INPUT_EXTENSIONS', 'md').split(',')]
        self.openai_api_key = os.environ.get('INPUT_OPENAI_API_KEY', '')
        self.model = os.environ.get('INPUT_MODEL', 'gpt-4')
        self.max_suggestions = int(os.environ.get('INPUT_MAX_SUGGESTIONS', '20'))
        self.confidence_threshold = float(os.environ.get('INPUT_CONFIDENCE_THRESHOLD', '0.8'))
        
        # Parse GitHub context
        github_context_str = os.environ.get('GITHUB_CONTEXT', '{}')
        self.github_context = json.loads(github_context_str)
        
        # Set up OpenAI if API key is provided
        if self.openai_api_key and openai:
            openai.api_key = self.openai_api_key
        
        # Initialize outputs
        self.files_processed = 0
        self.suggestions_count = 0
        self.changes_made = False
        self.mode = None  # 'issue' or 'pr'
        self.target_file = None
        self.file_changes = []
        
    def load_style_guide(self) -> str:
        """Load the style guide content from file or URL"""
        try:
            if self.style_guide_path.startswith('http'):
                # Load from URL
                response = requests.get(self.style_guide_path)
                response.raise_for_status()
                return response.text
            else:
                # Load from local file
                with open(self.style_guide_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            print(f"Error loading style guide: {e}")
            sys.exit(1)
    
    def parse_trigger_comment(self) -> Tuple[Optional[str], Optional[str]]:
        """Parse the trigger comment to determine mode and target file"""
        event_name = self.github_context.get('event_name')
        
        if event_name == 'issue_comment':
            comment_body = self.github_context.get('event', {}).get('comment', {}).get('body', '')
            
            # Check if this is an issue or PR comment
            if 'pull_request' in self.github_context.get('event', {}).get('issue', {}):
                # This is a PR comment
                if '@qe-style-check' in comment_body and comment_body.strip() == '@qe-style-check':
                    return 'pr', None
            else:
                # This is an issue comment
                match = re.search(r'@qe-style-check\s+(\S+)', comment_body)
                if match:
                    return 'issue', match.group(1)
        
        return None, None
    
    def get_changed_files_in_pr(self) -> List[str]:
        """Get list of changed markdown files in the current PR"""
        try:
            repo_name = self.github_context['repository']
            pr_number = self.github_context['event']['issue']['number']
            
            url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}/files"
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            files = response.json()
            changed_md_files = []
            
            for file in files:
                filename = file['filename']
                # Check if file is in docs directory and has correct extension
                if filename.startswith(self.docs_dir):
                    for ext in self.extensions:
                        if filename.endswith(f'.{ext}'):
                            changed_md_files.append(filename)
                            break
            
            return changed_md_files
        except Exception as e:
            print(f"Error getting changed files: {e}")
            return []
    
    def get_file_content(self, file_path: str) -> str:
        """Get file content from GitHub repository"""
        try:
            repo_name = self.github_context['repository']
            url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}"
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            content_data = response.json()
            if content_data['encoding'] == 'base64':
                import base64
                return base64.b64decode(content_data['content']).decode('utf-8')
            else:
                return content_data['content']
        except Exception as e:
            print(f"Error getting file content for {file_path}: {e}")
            return ""
    
    def analyze_with_ai(self, content: str, style_guide: str, file_path: str) -> Dict[str, Any]:
        """Use AI to analyze content against style guide"""
        if not self.openai_api_key or not openai:
            return self.analyze_with_rules(content, style_guide, file_path)
        
        try:
            prompt = f"""
You are a QuantEcon style guide checker. Please analyze the following markdown content against the QuantEcon style guide and provide specific, actionable suggestions.

STYLE GUIDE:
{style_guide}

CONTENT TO ANALYZE:
{content}

Please provide your response in the following JSON format:
{{
    "suggestions": [
        {{
            "line_number": <line_number_or_null>,
            "rule_id": "<rule_identifier>",
            "severity": "high|medium|low",
            "confidence": <float_0_to_1>,
            "description": "<what_is_wrong>",
            "suggestion": "<specific_fix>",
            "original_text": "<text_to_replace>",
            "suggested_text": "<replacement_text>"
        }}
    ],
    "summary": "<brief_summary_of_main_issues>"
}}

Focus on:
1. Code style rules (especially Unicode Greek letters in code)
2. Writing conventions (bold for definitions, italics for emphasis)
3. Math notation standards
4. Figure and heading conventions
5. Only suggest changes that clearly violate the style guide
"""

            # Use the newer client interface
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise technical writing editor focused on QuantEcon style guidelines."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            result_text = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                result = json.loads(result_text)
                return result
            except json.JSONDecodeError:
                # Fallback if AI doesn't return valid JSON
                return {
                    "suggestions": [],
                    "summary": "AI analysis completed but could not parse structured response"
                }
        except Exception as e:
            print(f"Error with AI analysis: {e}")
            return self.analyze_with_rules(content, style_guide, file_path)
    
    def analyze_with_rules(self, content: str, style_guide: str, file_path: str) -> Dict[str, Any]:
        """Fallback rule-based analysis when AI is not available"""
        suggestions = []
        lines = content.split('\n')
        
        # Rule 1: Check for Greek letters in code blocks
        in_code_block = False
        for i, line in enumerate(lines):
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            
            if in_code_block and 'python' in lines[max(0, i-1)]:
                # Check for spelled-out Greek letters
                greek_replacements = {
                    'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ',
                    'epsilon': 'ε', 'sigma': 'σ', 'theta': 'θ', 'rho': 'ρ'
                }
                
                for spelled, unicode_char in greek_replacements.items():
                    if re.search(rf'\b{spelled}\b', line):
                        suggestions.append({
                            "line_number": i + 1,
                            "rule_id": "CODE_RULE_4",
                            "severity": "medium",
                            "confidence": 0.9,
                            "description": f"Use Unicode Greek letter instead of '{spelled}'",
                            "suggestion": f"Replace '{spelled}' with '{unicode_char}'",
                            "original_text": spelled,
                            "suggested_text": unicode_char
                        })
        
        # Rule 2: Check heading capitalization
        for i, line in enumerate(lines):
            if line.startswith('#'):
                # Skip lecture titles (single #)
                if line.startswith('# '):
                    continue
                
                # Check other headings for proper capitalization
                heading_text = line.lstrip('# ').strip()
                words = heading_text.split()
                if len(words) > 1:
                    # Check if more than first word is capitalized
                    capitalized_count = sum(1 for word in words[1:] if word[0].isupper() and word.lower() not in ['and', 'or', 'the', 'of', 'in', 'on', 'at', 'to', 'for'])
                    if capitalized_count > 0:
                        suggestions.append({
                            "line_number": i + 1,
                            "rule_id": "HEADING_RULE",
                            "severity": "low",
                            "confidence": 0.7,
                            "description": "Heading should only capitalize first word and proper nouns",
                            "suggestion": "Use sentence case for headings",
                            "original_text": heading_text,
                            "suggested_text": heading_text.capitalize()
                        })
        
        summary = f"Found {len(suggestions)} potential style issues using rule-based analysis"
        return {"suggestions": suggestions, "summary": summary}
    
    def apply_suggestions(self, content: str, suggestions: List[Dict], file_path: str) -> str:
        """Apply high-confidence suggestions to content"""
        modified_content = content
        lines = content.split('\n')
        
        # Sort suggestions by line number in reverse order to avoid offset issues
        high_confidence_suggestions = [
            s for s in suggestions 
            if s.get('confidence', 0) >= self.confidence_threshold
        ]
        
        applied_count = 0
        for suggestion in sorted(high_confidence_suggestions, key=lambda x: x.get('line_number', 0), reverse=True):
            if suggestion.get('original_text') and suggestion.get('suggested_text'):
                original = suggestion['original_text']
                replacement = suggestion['suggested_text']
                
                # Apply replacement
                modified_content = modified_content.replace(original, replacement)
                applied_count += 1
                
                if applied_count >= self.max_suggestions:
                    break
        
        return modified_content
    
    def generate_summary(self, suggestions: List[Dict], file_path: str, mode: str) -> str:
        """Generate a summary of changes made"""
        high_conf = [s for s in suggestions if s.get('confidence', 0) >= self.confidence_threshold]
        low_conf = [s for s in suggestions if s.get('confidence', 0) < self.confidence_threshold]
        
        if mode == 'pr':
            summary = f"## 🎨 QuantEcon Style Guide Review\n\n"
            summary += f"Automatically applied **{len(high_conf)}** high-confidence style improvements to `{file_path}`.\n\n"
            
            if high_conf:
                summary += "### Changes Applied:\n"
                for suggestion in high_conf[:5]:  # Show first 5
                    summary += f"- **{suggestion.get('rule_id', 'STYLE')}**: {suggestion.get('description', 'Style improvement')}\n"
                
                if len(high_conf) > 5:
                    summary += f"- ... and {len(high_conf) - 5} more improvements\n"
            
            if low_conf:
                summary += f"\n### Additional Suggestions (manual review needed):\n"
                for suggestion in low_conf[:3]:  # Show first 3
                    summary += f"- {suggestion.get('description', 'Style suggestion')}\n"
        
        else:  # issue mode
            summary = f"## 📝 QuantEcon Style Guide Review for `{file_path}`\n\n"
            summary += f"Found **{len(suggestions)}** style suggestions.\n\n"
            
            if suggestions:
                summary += "### Suggestions:\n"
                for suggestion in suggestions[:10]:  # Show first 10
                    conf_emoji = "🔴" if suggestion.get('confidence', 0) < 0.5 else "🟡" if suggestion.get('confidence', 0) < 0.8 else "🟢"
                    summary += f"{conf_emoji} **{suggestion.get('rule_id', 'STYLE')}** (Line {suggestion.get('line_number', '?')}): {suggestion.get('description', 'Style suggestion')}\n"
                
                if len(suggestions) > 10:
                    summary += f"\n*... and {len(suggestions) - 10} more suggestions in the full review.*\n"
        
        summary += f"\n\n*Generated by [QuantEcon Style Guide Action](https://github.com/QuantEcon/meta/.github/actions/qe-style-guide)*"
        return summary
    
    def process_file(self, file_path: str, style_guide: str) -> Dict[str, Any]:
        """Process a single file for style checking"""
        print(f"Processing file: {file_path}")
        
        content = self.get_file_content(file_path)
        if not content:
            return {"suggestions": [], "summary": f"Could not load content for {file_path}"}
        
        analysis = self.analyze_with_ai(content, style_guide, file_path)
        suggestions = analysis.get('suggestions', [])
        
        self.files_processed += 1
        self.suggestions_count += len(suggestions)
        
        result = {
            "file_path": file_path,
            "suggestions": suggestions,
            "original_content": content
        }
        
        # Apply changes if in PR mode and have high-confidence suggestions
        if self.mode == 'pr':
            modified_content = self.apply_suggestions(content, suggestions, file_path)
            if modified_content != content:
                result["modified_content"] = modified_content
                self.changes_made = True
                self.file_changes.append({
                    "path": file_path,
                    "content": modified_content
                })
        elif self.mode == 'issue':
            # For issue mode, apply all suggestions to create comprehensive PR
            modified_content = self.apply_suggestions(content, suggestions, file_path)
            if modified_content != content:
                result["modified_content"] = modified_content
                self.changes_made = True
                self.file_changes.append({
                    "path": file_path,
                    "content": modified_content
                })
        
        return result
    
    def run(self):
        """Main execution method"""
        print("QuantEcon Style Guide Checker starting...")
        
        # Parse the trigger comment
        mode, target_file = self.parse_trigger_comment()
        if not mode:
            print("No valid trigger comment found")
            sys.exit(0)
        
        self.mode = mode
        self.target_file = target_file
        
        print(f"Mode: {mode}, Target file: {target_file}")
        
        # Load style guide
        style_guide = self.load_style_guide()
        print(f"Loaded style guide from: {self.style_guide_path}")
        
        # Determine files to process
        files_to_process = []
        
        if mode == 'issue' and target_file:
            # Process specific file mentioned in issue
            file_path = target_file
            if not file_path.startswith(self.docs_dir):
                file_path = os.path.join(self.docs_dir, file_path)
            files_to_process = [file_path]
        elif mode == 'pr':
            # Process changed files in PR
            files_to_process = self.get_changed_files_in_pr()
        
        if not files_to_process:
            print("No files to process")
            self.output_results()
            return
        
        print(f"Processing {len(files_to_process)} files...")
        
        # Process each file
        all_results = []
        for file_path in files_to_process:
            result = self.process_file(file_path, style_guide)
            all_results.append(result)
        
        # Generate summary
        all_suggestions = []
        for result in all_results:
            all_suggestions.extend(result.get('suggestions', []))
        
        summary = self.generate_summary(all_suggestions, target_file or "changed files", mode)
        
        # Save results for GitHub Actions
        changes_data = {
            "mode": mode,
            "targetFile": target_file,
            "fileChanges": self.file_changes,
            "summary": summary,
            "allResults": all_results
        }
        
        with open('/tmp/style_check_changes.json', 'w') as f:
            json.dump(changes_data, f, indent=2)
        
        self.output_results()
    
    def output_results(self):
        """Output results for GitHub Actions"""
        github_output = os.environ.get('GITHUB_OUTPUT', '/dev/stdout')
        
        with open(github_output, 'a') as f:
            f.write(f"files-processed={self.files_processed}\n")
            f.write(f"suggestions-count={self.suggestions_count}\n")
            f.write(f"changes-made={'true' if self.changes_made else 'false'}\n")
            f.write(f"mode={self.mode or ''}\n")
            f.write(f"changes-file=/tmp/style_check_changes.json\n")
            
            if self.mode and self.target_file:
                f.write(f"target-file={self.target_file}\n")

if __name__ == "__main__":
    checker = StyleGuideChecker()
    checker.run()