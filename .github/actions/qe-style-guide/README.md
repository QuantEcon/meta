# QuantEcon Style Guide Action

A GitHub Action that provides AI-powered style guide checking and suggestions for QuantEcon content. This action can be triggered via comments on issues and pull requests to automatically review and improve content according to the QuantEcon style guidelines.

## Features

- **Comment-triggered reviews**: Simply comment `@qe-style-check` to trigger style analysis
- **AI-powered analysis**: Uses OpenAI GPT models to analyze content against the QuantEcon style guide
- **Two modes of operation**:
  - **Issue mode**: Creates a new PR with comprehensive style suggestions
  - **PR mode**: Applies high-confidence changes directly to the existing PR
- **Rule-based fallback**: Works even without AI API keys using built-in style rules
- **Configurable**: Customizable style guide source, file extensions, and confidence thresholds

## Usage

### Triggering Style Checks

#### For Issues
Comment on any issue with:
```
@qe-style-check filename.md
```

This will:
1. Analyze the specified file against the QuantEcon style guide
2. Create a new pull request with all suggested improvements
3. Comment on the original issue with a link to the PR

#### For Pull Requests
Comment on any pull request with:
```
@qe-style-check
```

This will:
1. Analyze all changed markdown files in the PR
2. Apply high-confidence style improvements directly to the PR
3. Post a summary comment with details of changes made

### Direct Usage in Workflows

You can also use this action directly in your GitHub workflows:

```yaml
- name: Check style guide compliance
  uses: QuantEcon/meta/.github/actions/qe-style-guide@main
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    style-guide: '.github/copilot-qe-style-guide.md'
    docs: 'lectures/'
    extensions: 'md'
    openai-api-key: ${{ secrets.OPENAI_API_KEY }}  # Optional
    model: 'gpt-4'
    max-suggestions: '20'
    confidence-threshold: '0.8'
```

## Configuration

### Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `github-token` | GitHub token with repository access | Yes | |
| `style-guide` | Path or URL to the style guide document | No | `.github/copilot-qe-style-guide.md` |
| `docs` | Directory containing documents to check | No | `lectures/` |
| `extensions` | File extensions to check (comma-separated) | No | `md` |
| `openai-api-key` | OpenAI API key for AI-powered analysis | No | (uses rule-based fallback) |
| `model` | AI model to use for style checking | No | `gpt-4` |
| `max-suggestions` | Maximum number of suggestions per file | No | `20` |
| `confidence-threshold` | Confidence threshold for auto-applying changes (0.0-1.0) | No | `0.8` |

### Outputs

| Output | Description |
|--------|-------------|
| `files-processed` | Number of files processed |
| `suggestions-count` | Total number of style suggestions made |
| `pr-url` | URL of the created pull request (issue mode only) |
| `commit-sha` | SHA of the commit with style changes (PR mode only) |
| `summary` | Summary of changes made |

## Style Guide Rules

The action enforces the QuantEcon style guide rules including:

### Code Style
- **Unicode Greek Letters**: Prefer `α, β, γ, δ, ε, σ, θ, ρ` over `alpha, beta, gamma, delta, epsilon, sigma, theta, rho` in Python code
- **PEP8 Compliance**: Follow Python style guidelines
- **Operator Spacing**: Use spaces around operators (`a * b`, `a + b`) but not for exponentiation (`a**b`)

### Writing Conventions
- **Bold for Definitions**: Use `**bold**` for new term definitions
- **Italics for Emphasis**: Use `*italics*` for emphasis
- **Heading Capitalization**: Only capitalize first word and proper nouns in headings (except main titles)

### Math Notation
- Use `\\top` for transpose: $A^\\top$
- Use `\\mathbb{1}` for vectors/matrices of ones
- Use square brackets for matrices: `\\begin{bmatrix} ... \\end{bmatrix}`
- Use curly brackets for sequences: `\\{ x_t \\}_{t=0}^{\\infty}`

### Figure Guidelines
- No embedded titles in matplotlib plots
- Use lowercase captions except first letter and proper nouns
- Set descriptive `name` attributes for cross-references
- Use `lw=2` for matplotlib line charts

## Setup

### Prerequisites

1. **Repository Access**: The action requires a GitHub token with repository access
2. **OpenAI API Key** (Optional): For AI-powered analysis, set up an OpenAI API key as a repository secret

### Installation

1. **Copy the action files** to your repository:
   ```
   .github/actions/qe-style-guide/
   ├── action.yml
   ├── process-style-check.py
   └── README.md
   ```

2. **Add the workflow file**:
   ```
   .github/workflows/qe-style-guide.yml
   ```

3. **Set up secrets** (optional):
   - `OPENAI_API_KEY`: Your OpenAI API key for enhanced AI analysis

4. **Customize the style guide**:
   - Place your style guide document at `.github/copilot-qe-style-guide.md`
   - Or specify a different path/URL in the action configuration

## Permissions

Only users with write access to the repository can trigger style guide checks. The action will automatically check permissions and reject requests from unauthorized users.

## Examples

### Basic Issue Usage
```
I'd like to review the style of the Aiyagari model lecture.

@qe-style-check aiyagari.md
```

### PR Usage
```
Please check the style of the files I've modified in this PR.

@qe-style-check
```

### Custom Workflow Integration
```yaml
name: Weekly Style Review
on:
  schedule:
    - cron: '0 10 * * 1'  # Every Monday at 10 AM

jobs:
  style-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Review recent changes
        uses: QuantEcon/meta/.github/actions/qe-style-guide@main
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          docs: 'lectures/'
          extensions: 'md,rst'
          confidence-threshold: '0.9'
```

## AI vs Rule-Based Analysis

### AI-Powered Analysis (with OpenAI API key)
- Comprehensive understanding of context and style nuances
- Natural language explanations of issues
- Confidence scoring for each suggestion
- Advanced pattern recognition

### Rule-Based Analysis (fallback)
- Fast, deterministic checking
- Focuses on clear, codifiable rules:
  - Greek letter usage in code blocks
  - Heading capitalization patterns
  - Basic formatting conventions
- No external API dependencies

## Troubleshooting

### Common Issues

1. **"User does not have sufficient permissions"**
   - Only repository collaborators with write access can trigger style checks
   - Contact a repository maintainer for access

2. **"No files to process"**
   - Ensure the specified file exists in the `docs` directory
   - Check that file extensions match the configured `extensions` input

3. **"AI analysis failed"**
   - Check that `OPENAI_API_KEY` is correctly set
   - Verify API key has sufficient credits
   - The action will fall back to rule-based analysis

4. **"Could not load style guide"**
   - Verify the style guide path is correct
   - For URL-based style guides, ensure the URL is accessible
   - Check repository permissions for local files

### Getting Help

- Check the [workflow logs](../../actions) for detailed error messages
- Review the [QuantEcon style guide](../../blob/main/.github/copilot-qe-style-guide.md)
- Open an issue in the [meta repository](https://github.com/QuantEcon/meta/issues)

## Contributing

This action is part of the QuantEcon meta repository. Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This action is released under the same license as the QuantEcon meta repository.