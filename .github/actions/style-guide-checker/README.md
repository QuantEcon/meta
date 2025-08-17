# Style Guide Checker Action

A GitHub Action that uses AI to review QuantEcon lectures for compliance with the [QuantEcon Style Guide](../../copilot-qe-style-guide.md) and automatically suggests or applies improvements.

## Features

- 🤖 **AI-Powered Analysis**: Uses OpenAI GPT-4 to understand style guide context and provide intelligent suggestions
- 📝 **Two Operating Modes**: 
  - **PR Mode**: Reviews only changed files in pull requests
  - **Full Mode**: Reviews all files in the repository (for scheduled runs)
- 🎯 **Confidence-Based Actions**:
  - **High confidence**: Auto-commits changes directly
  - **Medium/Low confidence**: Creates PR review suggestions for human review
- 🚫 **File Exclusion**: Supports regex patterns to exclude files from review
- 📊 **Detailed Reporting**: Provides comprehensive summaries and metrics

## Usage

### Basic Usage (PR Mode)

```yaml
name: Style Guide Review
on:
  pull_request:
    paths:
      - 'lectures/**/*.md'

jobs:
  style-check:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        
      - name: Run style guide checker
        uses: QuantEcon/meta/.github/actions/style-guide-checker@main
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
          docs: 'lectures'
          mode: 'pr'
```

### Scheduled Full Review

```yaml
name: Weekly Style Review
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM UTC

jobs:
  full-style-review:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        
      - name: Run full style guide review
        uses: QuantEcon/meta/.github/actions/style-guide-checker@main
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
          docs: 'lectures'
          mode: 'full'
          create-pr: 'true'
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `style-guide` | Path to the style guide document (local path or URL) | No | `.github/copilot-qe-style-guide.md` |
| `docs` | Path to the documents/lectures directory | No | `lectures` |
| `exclude-files` | Comma-separated list of file patterns to exclude (supports regex) | No | `''` |
| `mode` | Operating mode: `pr` for PR review, `full` for complete review | No | `pr` |
| `confidence-threshold` | Minimum confidence level for auto-commits (`high`, `medium`, `low`) | No | `high` |
| `github-token` | GitHub token for API access | **Yes** | |
| `openai-api-key` | OpenAI API key for AI-powered style checking | No | `''` |
| `max-suggestions` | Maximum number of suggestions to make per file | No | `10` |
| `create-pr` | Whether to create a PR for scheduled mode (`true`/`false`) | No | `true` |

## Outputs

| Output | Description |
|--------|-------------|
| `files-reviewed` | Number of files reviewed |
| `suggestions-made` | Total number of suggestions made |
| `high-confidence-changes` | Number of high confidence changes auto-committed |
| `pr-url` | URL of created PR (in scheduled mode) |
| `review-summary` | Summary of the style review |

## Configuration Examples

### Custom Style Guide Location

```yaml
- name: Style check with custom guide
  uses: QuantEcon/meta/.github/actions/style-guide-checker@main
  with:
    style-guide: 'https://raw.githubusercontent.com/MyOrg/docs/main/style-guide.md'
    github-token: ${{ secrets.GITHUB_TOKEN }}
    openai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

### Exclude Specific Files

```yaml
- name: Style check with exclusions
  uses: QuantEcon/meta/.github/actions/style-guide-checker@main
  with:
    exclude-files: 'lectures/tmp/.*,.*_old\.md,lectures/archive/.*'
    github-token: ${{ secrets.GITHUB_TOKEN }}
    openai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

### Rule-Based Mode (No OpenAI)

```yaml
- name: Rule-based style check
  uses: QuantEcon/meta/.github/actions/style-guide-checker@main
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    # No openai-api-key provided - uses rule-based fallback
```

## How It Works

### 1. File Discovery
- **PR Mode**: Analyzes only files changed in the current pull request
- **Full Mode**: Analyzes all `.md` files in the specified `docs` directory
- Applies exclusion patterns to filter out unwanted files

### 2. Style Analysis
- **AI-Powered (Recommended)**: Uses OpenAI GPT-4 with the style guide as context to provide intelligent, contextual suggestions
- **Rule-Based Fallback**: Uses predefined rules for common style issues when OpenAI is not available

### 3. Confidence-Based Actions
- **High Confidence**: Changes that clearly violate style rules are auto-committed
- **Medium Confidence**: Likely style improvements suggested as PR review comments
- **Low Confidence**: Potential improvements suggested as PR review comments

### 4. Reporting
- Creates detailed PR comments with summaries and metrics
- Provides GitHub Action outputs for integration with other workflows

## Style Rules Checked

The action checks for compliance with the [QuantEcon Style Guide](../../copilot-qe-style-guide.md), including:

### Writing Conventions
- Clarity and conciseness
- One sentence paragraphs
- Proper logical flow
- Appropriate capitalization

### Code Style
- PEP8 compliance
- Unicode symbols for Greek letters (α, β, γ, etc.)
- Modern timing patterns (`qe.Timer()`)
- Proper package installation practices

### Math Notation
- LaTeX formatting standards
- Equation numbering and referencing
- Matrix and vector notation

### Figure Formatting
- Caption formatting and placement
- Figure referencing
- Matplotlib styling guidelines

### Document Structure
- Heading capitalization rules
- Proper linking syntax
- Citation formatting

## Examples

### Example PR Comment

When the action runs on a pull request, it creates a summary comment like:

```markdown
## 📝 Style Guide Review Summary

**Files reviewed:** 3
**Total suggestions:** 8

**Changes made:**
- ✅ **2** high-confidence changes auto-committed
- 💭 **6** suggestions added as review comments

**Suggestion breakdown:**
- 🔥 High confidence: 2
- ⚠️ Medium confidence: 4
- 💡 Low confidence: 2

The high-confidence changes have been automatically applied to maintain consistency with the QuantEcon Style Guide. Please review the other suggestions in the file comments.
```

### Example Review Suggestion

Individual suggestions appear as PR review comments:

```markdown
**Style Guide Suggestion (medium confidence)**

Use Unicode α instead of 'alpha' for better mathematical notation

**Suggested change:**
```markdown
def utility_function(c, α=0.5, β=0.95):
```

**Rule category:** variable_naming
```

## Setup Requirements

### 1. GitHub Token
The action requires a GitHub token with appropriate permissions:
- For public repositories: `${{ secrets.GITHUB_TOKEN }}` (automatic)
- For private repositories: Personal access token with `repo` scope

### 2. OpenAI API Key (Recommended)
For AI-powered analysis, add your OpenAI API key as a repository secret:
1. Go to repository Settings → Secrets and variables → Actions
2. Add a new secret named `OPENAI_API_KEY`
3. Paste your OpenAI API key as the value

Without OpenAI, the action falls back to rule-based checking with limited capabilities.

## Troubleshooting

### Common Issues

**"No files to review"**
- Check that the `docs` path exists and contains `.md` files
- Verify exclusion patterns aren't too broad
- In PR mode, ensure there are actual changes to markdown files

**"OpenAI API not available"**
- Verify the `OPENAI_API_KEY` secret is correctly set
- Check API key has sufficient credits/quota
- Action will fall back to rule-based checking

**"Failed to create PR review suggestions"**
- Ensure the GitHub token has appropriate permissions
- Check that the action is running in a PR context for PR mode

### Debug Mode

Add debug logging by setting the `ACTIONS_STEP_DEBUG` secret to `true` in your repository settings.

## Contributing

To contribute to this action:

1. Modify the Python script in `check-style.py`
2. Update tests in the `/test/style-guide-checker/` directory
3. Run tests locally before submitting PR
4. Update documentation as needed

## License

This action is part of the QuantEcon meta repository and follows the same license terms.