# Style Guide Checker Examples

This document provides comprehensive examples of how to use the Style Guide Checker action in various scenarios.

## Basic Examples

### 1. Simple PR Review

The most basic usage for reviewing pull requests:

```yaml
name: Style Review
on:
  pull_request:
    paths:
      - '**/*.md'

jobs:
  style-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: QuantEcon/meta/.github/actions/style-guide-checker@main
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

### 2. Weekly Full Repository Review

Scheduled review of all files with PR creation:

```yaml
name: Weekly Style Audit
on:
  schedule:
    - cron: '0 9 * * 1'  # Monday 9 AM UTC

jobs:
  full-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: QuantEcon/meta/.github/actions/style-guide-checker@main
        with:
          mode: 'full'
          github-token: ${{ secrets.GITHUB_TOKEN }}
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
          create-pr: 'true'
```

## Advanced Configuration Examples

### 3. Custom Documentation Structure

For repositories with non-standard directory structures:

```yaml
- name: Style check custom structure
  uses: QuantEcon/meta/.github/actions/style-guide-checker@main
  with:
    docs: 'content/lectures'
    style-guide: 'docs/style/quantecon-guide.md'
    github-token: ${{ secrets.GITHUB_TOKEN }}
    openai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

### 4. File Exclusion Patterns

Excluding specific files and directories using regex patterns:

```yaml
- name: Style check with exclusions
  uses: QuantEcon/meta/.github/actions/style-guide-checker@main
  with:
    exclude-files: |
      lectures/archive/.*,
      .*_backup\.md,
      lectures/tmp/.*,
      lectures/old_version/.*,
      README\.md
    github-token: ${{ secrets.GITHUB_TOKEN }}
    openai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

### 5. Conservative Mode (Medium Confidence Threshold)

Only auto-commit very high confidence changes:

```yaml
- name: Conservative style check
  uses: QuantEcon/meta/.github/actions/style-guide-checker@main
  with:
    confidence-threshold: 'high'
    max-suggestions: 5
    github-token: ${{ secrets.GITHUB_TOKEN }}
    openai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

### 6. Aggressive Mode (Lower Confidence Threshold)

Auto-commit more changes (use with caution):

```yaml
- name: Aggressive style check
  uses: QuantEcon/meta/.github/actions/style-guide-checker@main
  with:
    confidence-threshold: 'medium'
    max-suggestions: 20
    github-token: ${{ secrets.GITHUB_TOKEN }}
    openai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

## Organization-Wide Examples

### 7. Shared Workflow Template

Create a reusable workflow template in `.github/workflows/style-check.yml`:

```yaml
name: Style Guide Compliance

on:
  pull_request:
    paths:
      - 'lectures/**/*.md'
      - 'content/**/*.md'
  workflow_dispatch:
    inputs:
      mode:
        description: 'Review mode'
        required: true
        default: 'pr'
        type: choice
        options:
          - pr
          - full

jobs:
  style-review:
    runs-on: ubuntu-latest
    name: Style Guide Review
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - name: Run style guide checker
        uses: QuantEcon/meta/.github/actions/style-guide-checker@main
        with:
          mode: ${{ github.event.inputs.mode || 'pr' }}
          docs: ${{ vars.DOCS_PATH || 'lectures' }}
          style-guide: ${{ vars.STYLE_GUIDE_PATH || '.github/copilot-qe-style-guide.md' }}
          exclude-files: ${{ vars.EXCLUDE_PATTERNS || '' }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
          max-suggestions: ${{ vars.MAX_SUGGESTIONS || '10' }}
```

### 8. Multi-Repository Style Enforcement

For organization-wide style enforcement using repository variables:

```yaml
name: Organization Style Standards

on:
  pull_request:
  schedule:
    - cron: '0 2 * * 0'  # Weekly at 2 AM Sunday

jobs:
  determine-mode:
    runs-on: ubuntu-latest
    outputs:
      mode: ${{ steps.mode.outputs.mode }}
    steps:
      - id: mode
        run: |
          if [ "${{ github.event_name }}" = "pull_request" ]; then
            echo "mode=pr" >> $GITHUB_OUTPUT
          else
            echo "mode=full" >> $GITHUB_OUTPUT
          fi

  style-check:
    needs: determine-mode
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.ORGANIZATION_TOKEN }}
          
      - uses: QuantEcon/meta/.github/actions/style-guide-checker@main
        with:
          mode: ${{ needs.determine-mode.outputs.mode }}
          style-guide: 'https://raw.githubusercontent.com/QuantEcon/meta/main/.github/copilot-qe-style-guide.md'
          docs: ${{ vars.LECTURES_PATH }}
          exclude-files: ${{ vars.STYLE_EXCLUDE_PATTERNS }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

## Integration Examples

### 9. Integration with Quality Checks

Combine with other quality assurance actions:

```yaml
name: Quality Assurance Pipeline

on:
  pull_request:
    paths:
      - 'lectures/**/*.md'

jobs:
  quality-checks:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        check: [style, warnings, spelling]
    steps:
      - uses: actions/checkout@v4
      
      - name: Style Guide Check
        if: matrix.check == 'style'
        uses: QuantEcon/meta/.github/actions/style-guide-checker@main
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
          
      - name: Warning Check
        if: matrix.check == 'warnings'
        uses: QuantEcon/meta/.github/actions/check-warnings@main
        with:
          html-path: '_build/html'
          
      - name: Spelling Check
        if: matrix.check == 'spelling'
        uses: crate-ci/typos@master
```

### 10. Conditional Execution

Run style checks only when certain conditions are met:

```yaml
name: Conditional Style Check

on:
  pull_request:
    types: [opened, synchronize, ready_for_review]

jobs:
  style-check:
    if: |
      !github.event.pull_request.draft &&
      contains(github.event.pull_request.labels.*.name, 'needs-style-review')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: QuantEcon/meta/.github/actions/style-guide-checker@main
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

## Fallback and Error Handling Examples

### 11. Graceful Fallback

Handle cases where OpenAI is unavailable:

```yaml
- name: Style check with fallback
  uses: QuantEcon/meta/.github/actions/style-guide-checker@main
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    openai-api-key: ${{ secrets.OPENAI_API_KEY }}
  continue-on-error: true
  
- name: Notify on failure
  if: failure()
  uses: actions/github-script@v7
  with:
    script: |
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: '⚠️ Style guide check failed. Please review manually against the [style guide](/.github/copilot-qe-style-guide.md).'
      })
```

### 12. Rate Limiting Handling

For large repositories, add delays to avoid API rate limits:

```yaml
- name: Style check large repo
  uses: QuantEcon/meta/.github/actions/style-guide-checker@main
  with:
    mode: 'full'
    max-suggestions: 5  # Limit suggestions per file
    github-token: ${{ secrets.GITHUB_TOKEN }}
    openai-api-key: ${{ secrets.OPENAI_API_KEY }}
  timeout-minutes: 30
```

## Testing and Development Examples

### 13. Development Testing

For testing the action during development:

```yaml
name: Test Style Checker

on:
  push:
    paths:
      - '.github/actions/style-guide-checker/**'
  workflow_dispatch:
    inputs:
      test-file:
        description: 'Specific file to test'
        required: false

jobs:
  test-action:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Create test file
        if: github.event.inputs.test-file
        run: |
          mkdir -p test-lectures
          echo "${{ github.event.inputs.test-file }}" > test-lectures/test.md
          
      - name: Test style checker
        uses: .//.github/actions/style-guide-checker
        with:
          docs: 'test-lectures'
          mode: 'full'
          github-token: ${{ secrets.GITHUB_TOKEN }}
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

### 14. Style Guide Development

Test with custom style guides during development:

```yaml
- name: Test with custom style guide
  uses: QuantEcon/meta/.github/actions/style-guide-checker@main
  with:
    style-guide: '.github/test-style-guide.md'
    docs: 'test-content'
    mode: 'full'
    github-token: ${{ secrets.GITHUB_TOKEN }}
    openai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

## Output Usage Examples

### 15. Using Action Outputs

Use outputs from the style checker in subsequent steps:

```yaml
- name: Run style check
  id: style
  uses: QuantEcon/meta/.github/actions/style-guide-checker@main
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    openai-api-key: ${{ secrets.OPENAI_API_KEY }}
    
- name: Report results
  run: |
    echo "Files reviewed: ${{ steps.style.outputs.files-reviewed }}"
    echo "Suggestions made: ${{ steps.style.outputs.suggestions-made }}"
    echo "Auto-applied changes: ${{ steps.style.outputs.high-confidence-changes }}"
    
- name: Fail if too many issues
  if: steps.style.outputs.suggestions-made > 50
  run: |
    echo "Too many style issues found (${{ steps.style.outputs.suggestions-made }})"
    exit 1
```

### 16. Metrics Collection

Collect style check metrics for analysis:

```yaml
- name: Style check with metrics
  id: style
  uses: QuantEcon/meta/.github/actions/style-guide-checker@main
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    openai-api-key: ${{ secrets.OPENAI_API_KEY }}
    
- name: Upload metrics
  uses: actions/upload-artifact@v4
  with:
    name: style-metrics
    path: |
      echo "date=$(date -u +%Y-%m-%d)" >> style-metrics.txt
      echo "repository=${{ github.repository }}" >> style-metrics.txt
      echo "files_reviewed=${{ steps.style.outputs.files-reviewed }}" >> style-metrics.txt
      echo "suggestions_made=${{ steps.style.outputs.suggestions-made }}" >> style-metrics.txt
      echo "auto_applied=${{ steps.style.outputs.high-confidence-changes }}" >> style-metrics.txt
```

## Security Examples

### 17. Secure Token Handling

Proper token management for organization use:

```yaml
name: Secure Style Check

jobs:
  style-check:
    runs-on: ubuntu-latest
    environment: production  # Use environment protection rules
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.STYLE_CHECK_TOKEN }}  # Limited scope token
          
      - uses: QuantEcon/meta/.github/actions/style-guide-checker@main
        with:
          github-token: ${{ secrets.STYLE_CHECK_TOKEN }}
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

### 18. Fork Safety

Safe execution for external contributions:

```yaml
name: Safe Style Check

on:
  pull_request_target:  # Use with caution
    types: [labeled]

jobs:
  style-check:
    if: contains(github.event.label.name, 'safe-to-test')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}
          
      - uses: QuantEcon/meta/.github/actions/style-guide-checker@main
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          # Note: No OpenAI key for external PRs - uses rule-based fallback
```

These examples cover most common use cases and can be adapted for specific repository needs. Remember to always test new configurations in a development environment before deploying to production workflows.