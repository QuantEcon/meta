# Code Style Formatter Action Examples

This document provides practical examples of using the Code Style Formatter Action in different scenarios.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Trigger on PR Comments](#trigger-on-pr-comments)
- [Selective Processing](#selective-processing)
- [Custom Black Configuration](#custom-black-configuration)
- [Integration with Existing Workflows](#integration-with-existing-workflows)
- [Multi-Repository Setup](#multi-repository-setup)

## Basic Usage

### Format Specific Files

```yaml
name: Format Python Code
on:
  push:
    paths:
      - 'lectures/**/*.md'

jobs:
  format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Format Python code
        uses: QuantEcon/meta/.github/actions/code-style-checker@main
        with:
          files: 'lectures/dynamic_programming.md,lectures/optimization.md'
          
      - name: Push changes
        run: git push
```

### Format All Markdown Files Using Glob Patterns

```yaml
- name: Format all lecture files
  uses: QuantEcon/meta/.github/actions/code-style-checker@main
  with:
    files: 'lectures/**/*.md'

- name: Format multiple directories
  uses: QuantEcon/meta/.github/actions/code-style-checker@main
  with:
    files: 'lectures/**/*.md,examples/**/*.md,notebooks/**/*.md'
```

### Format All Markdown Files

```yaml
- name: Get all markdown files using glob pattern
  uses: QuantEcon/meta/.github/actions/code-style-checker@main
  with:
    files: '**/*.md'

- name: Format specific directories
  uses: QuantEcon/meta/.github/actions/code-style-checker@main
  with:
    files: 'lectures/**/*.md,examples/**/*.md'
```

## Trigger on PR Comments

### Complete PR Comment Workflow

Copy this complete workflow to your repository as `.github/workflows/code-style-formatter.yml`:

```yaml
name: Code Style Formatter
on:
  issue_comment:
    types: [created]

jobs:
  format-code:
    if: github.event.issue.pull_request && contains(github.event.comment.body, '@quantecon-code-style')
    runs-on: ubuntu-latest
    
    steps:
    - name: Get PR information
      id: pr
      uses: actions/github-script@v7
      with:
        script: |
          const { data: pullRequest } = await github.rest.pulls.get({
            owner: context.repo.owner,
            repo: context.repo.repo,
            pull_number: context.issue.number,
          });
          
          core.setOutput('head-sha', pullRequest.head.sha);
          core.setOutput('head-ref', pullRequest.head.ref);
          core.setOutput('base-sha', pullRequest.base.sha);
          
          return pullRequest;
    
    - name: Checkout PR branch
      uses: actions/checkout@v4
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
        ref: ${{ steps.pr.outputs.head-ref }}
        fetch-depth: 0
    
    - name: Get changed files
      id: changed-files
      uses: tj-actions/changed-files@v40
      with:
        files: '**/*.md'
        base_sha: ${{ steps.pr.outputs.base-sha }}
        sha: ${{ steps.pr.outputs.head-sha }}
    
    - name: Check if any markdown files changed
      id: check-files
      run: |
        if [ -z "${{ steps.changed-files.outputs.all_changed_files }}" ]; then
          echo "no-files=true" >> $GITHUB_OUTPUT
          echo "No markdown files were changed in this PR"
        else
          echo "no-files=false" >> $GITHUB_OUTPUT
          echo "Changed markdown files:"
          echo "${{ steps.changed-files.outputs.all_changed_files }}"
        fi
    
    - name: Format MyST markdown files
      if: steps.check-files.outputs.no-files == 'false'
      id: format
      uses: QuantEcon/meta/.github/actions/code-style-checker@main
      with:
        files: ${{ steps.changed-files.outputs.all_changed_files }}
        check-myst-code-cells: 'true'
        check-markdown-blocks: 'true'
        python-languages: 'python,python3,ipython,ipython3'
        black-args: '--line-length=88'
        commit-files: 'true'
        git-user-name: 'GitHub Action'
        git-user-email: 'action@github.com'
    
    - name: Push changes
      if: steps.check-files.outputs.no-files == 'false' && steps.format.outputs.changes-made == 'true'
      run: |
        git push
        echo "Successfully pushed formatting changes"
    
    - name: Post comment with results
      uses: actions/github-script@v7
      with:
        script: |
          const noFiles = '${{ steps.check-files.outputs.no-files }}';
          const changesMade = '${{ steps.format.outputs.changes-made }}';
          const filesProcessed = '${{ steps.format.outputs.files-processed }}';
          const filesChanged = '${{ steps.format.outputs.files-changed }}';
          const blocksFormatted = '${{ steps.format.outputs.total-blocks-formatted }}';
          
          let body;
          
          if (noFiles === 'true') {
            body = [
              '## 🔍 Code Style Check Results',
              '',
              '✅ **No markdown files were changed in this PR.**',
              '',
              'The code style checker found no markdown files to process.',
              '',
              '---',
              '',
              '🤖 *This comment was automatically generated by the [Code Style Formatter](https://github.com/QuantEcon/meta/.github/actions/code-style-checker).*'
            ].join('\n');
          } else if (changesMade === 'true') {
            body = [
              '## ✅ Code Style Formatting Applied',
              '',
              `🎉 **Successfully applied black formatting to ${blocksFormatted} code block(s) across ${filesChanged} file(s).**`,
              '',
              '**Summary:**',
              `- **Files processed:** ${filesProcessed}`,
              `- **Files modified:** ${filesChanged}`,
              `- **Code blocks formatted:** ${blocksFormatted}`,
              '',
              '**Changes committed:**',
              '- Each modified file has been committed separately with a descriptive commit message',
              '- The formatting follows PEP8 standards using black',
              '',
              '**Languages processed:**',
              '- \`python\`, \`python3\`, \`ipython\`, \`ipython3\` code blocks',
              '- Both MyST \`{code-cell}\` directives and standard markdown fenced code blocks',
              '',
              '---',
              '',
              '🤖 *This comment was automatically generated by the [Code Style Formatter](https://github.com/QuantEcon/meta/.github/actions/code-style-checker).*'
            ].join('\n');
          } else {
            body = [
              '## ✅ Code Style Check Completed',
              '',
              `📝 **Processed ${filesProcessed} markdown file(s) - no formatting changes needed.**`,
              '',
              'All Python code blocks in the changed markdown files are already properly formatted according to PEP8 standards.',
              '',
              '**Summary:**',
              `- **Files processed:** ${filesProcessed}`,
              '- **Files modified:** 0',
              '- **Code blocks formatted:** 0',
              '',
              '**Languages checked:**',
              '- \`python\`, \`python3\`, \`ipython\`, \`ipython3\` code blocks',
              '- Both MyST \`{code-cell}\` directives and standard markdown fenced code blocks',
              '',
              '---',
              '',
              '🤖 *This comment was automatically generated by the [Code Style Formatter](https://github.com/QuantEcon/meta/.github/actions/code-style-checker).*'
            ].join('\n');
          }
          
          await github.rest.issues.createComment({
            owner: context.repo.owner,
            repo: context.repo.repo,
            issue_number: context.issue.number,
            body: body
          });
```

After adding this workflow to your repository, simply comment `@quantecon-code-style` on any PR to trigger automatic formatting of Python code in changed markdown files.

### Custom Comment Triggers

You can customize the trigger phrase:

```yaml
if: github.event.issue.pull_request && contains(github.event.comment.body, '/format-python')
```

Or support multiple triggers:

```yaml
if: |
  github.event.issue.pull_request && (
    contains(github.event.comment.body, '@quantecon-code-style') ||
    contains(github.event.comment.body, '/format-code') ||
    contains(github.event.comment.body, '/black-format')
  )
```

## Selective Processing

### MyST Code-Cells Only

```yaml
- name: Format MyST code-cells only
  uses: QuantEcon/meta/.github/actions/code-style-checker@main
  with:
    files: ${{ steps.changed-files.outputs.all_changed_files }}
    check-myst-code-cells: 'true'
    check-markdown-blocks: 'false'
```

### Standard Markdown Blocks Only

```yaml
- name: Format markdown code blocks only
  uses: QuantEcon/meta/.github/actions/code-style-checker@main
  with:
    files: ${{ steps.changed-files.outputs.all_changed_files }}
    check-myst-code-cells: 'false'
    check-markdown-blocks: 'true'
```

### Specific Python Variants

```yaml
- name: Format only Python and IPython
  uses: QuantEcon/meta/.github/actions/code-style-checker@main
  with:
    files: 'notebooks/*.md'
    python-languages: 'python,ipython'
```

## Custom Black Configuration

### Line Length and Style Options

```yaml
- name: Format with custom black settings
  uses: QuantEcon/meta/.github/actions/code-style-checker@main
  with:
    files: ${{ steps.changed-files.outputs.all_changed_files }}
    black-args: '--line-length=100 --skip-string-normalization'
```

### Target Python Version

```yaml
- name: Format for Python 3.8+
  uses: QuantEcon/meta/.github/actions/code-style-checker@main
  with:
    files: ${{ steps.changed-files.outputs.all_changed_files }}
    black-args: '--line-length=88 --target-version=py38'
```

### Skip Formatting Commits

```yaml
- name: Format without committing
  uses: QuantEcon/meta/.github/actions/code-style-checker@main
  with:
    files: ${{ steps.changed-files.outputs.all_changed_files }}
    commit-files: 'false'

- name: Custom commit message
  if: steps.format.outputs.changes-made == 'true'
  run: |
    git add .
    git commit -m "Apply black formatting to Python code blocks"
    git push
```

## Integration with Existing Workflows

### Pre-commit Integration

```yaml
name: Pre-commit Checks
on: [push, pull_request]

jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Run pre-commit
      uses: pre-commit/action@v3.0.0
    
    - name: Format Python in markdown
      if: failure()  # Only run if pre-commit fails
      uses: QuantEcon/meta/.github/actions/code-style-checker@main
      with:
        files: ${{ steps.changed-files.outputs.all_changed_files }}
```

### Build Process Integration

```yaml
name: Build Documentation
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Format Python code
      uses: QuantEcon/meta/.github/actions/code-style-checker@main
      with:
        files: 'lectures/*.md'
    
    - name: Build with Jupyter Book
      run: jupyter-book build .
    
    - name: Deploy to GitHub Pages
      if: github.ref == 'refs/heads/main'
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./_build/html
```

## Multi-Repository Setup

### Reusable Workflow

Create `.github/workflows/format-python.yml`:

```yaml
name: Reusable Python Formatter

on:
  workflow_call:
    inputs:
      file-pattern:
        description: 'Pattern for files to format'
        required: false
        default: '**/*.md'
        type: string
      black-args:
        description: 'Arguments for black'
        required: false
        default: '--line-length=88'
        type: string

jobs:
  format:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Get changed files
      id: changed-files
      uses: tj-actions/changed-files@v40
      with:
        files: ${{ inputs.file-pattern }}
    
    - name: Format Python code
      if: steps.changed-files.outputs.any_changed == 'true'
      uses: QuantEcon/meta/.github/actions/code-style-checker@main
      with:
        files: ${{ steps.changed-files.outputs.all_changed_files }}
        black-args: ${{ inputs.black-args }}
    
    - name: Push changes
      if: steps.changed-files.outputs.any_changed == 'true'
      run: git push
```

Use in other repositories:

```yaml
name: Format Code
on: [push]

jobs:
  format:
    uses: QuantEcon/meta/.github/workflows/format-python.yml@main
    with:
      file-pattern: 'lectures/**/*.md'
      black-args: '--line-length=100'
```

### Organization-wide Settings

For consistent formatting across all repositories:

```yaml
- name: Format with organization standards
  uses: QuantEcon/meta/.github/actions/code-style-checker@main
  with:
    files: ${{ steps.changed-files.outputs.all_changed_files }}
    black-args: '--line-length=88 --target-version=py39'
    python-languages: 'python,python3,ipython,ipython3'
    check-myst-code-cells: 'true'
    check-markdown-blocks: 'true'
```

## Advanced Examples

### Conditional Formatting Based on File Changes

```yaml
- name: Get changed file types
  id: changes
  uses: dorny/paths-filter@v2
  with:
    filters: |
      lectures:
        - 'lectures/**/*.md'
      notebooks:
        - 'notebooks/**/*.md'
      examples:
        - 'examples/**/*.md'

- name: Format lecture files
  if: steps.changes.outputs.lectures == 'true'
  uses: QuantEcon/meta/.github/actions/code-style-checker@main
  with:
    files: ${{ steps.changed-files.outputs.all_changed_files }}
    black-args: '--line-length=88'

- name: Format notebook files
  if: steps.changes.outputs.notebooks == 'true'
  uses: QuantEcon/meta/.github/actions/code-style-checker@main
  with:
    files: ${{ steps.changed-files.outputs.all_changed_files }}
    black-args: '--line-length=100'  # Different settings for notebooks
```

### Error Handling and Notifications

```yaml
- name: Format Python code
  id: format
  continue-on-error: true
  uses: QuantEcon/meta/.github/actions/code-style-checker@main
  with:
    files: ${{ steps.changed-files.outputs.all_changed_files }}

- name: Report formatting results
  uses: actions/github-script@v7
  with:
    script: |
      const success = '${{ steps.format.outcome }}' === 'success';
      const changesMode = '${{ steps.format.outputs.changes-made }}' === 'true';
      
      let message = success ? '✅ Code formatting completed' : '❌ Code formatting failed';
      if (success && changesMode) {
        message += `\n\n📝 Formatted ${{ steps.format.outputs.total-blocks-formatted }} code blocks in ${{ steps.format.outputs.files-changed }} files.`;
      }
      
      await github.rest.issues.createComment({
        owner: context.repo.owner,
        repo: context.repo.repo,
        issue_number: context.issue.number,
        body: message
      });
```

## Troubleshooting

### Common Issues and Solutions

1. **No files processed**: Ensure the file paths are correct and files exist
2. **Black formatting errors**: Check that the Python code is syntactically valid
3. **Permission issues**: Ensure the GitHub token has write permissions
4. **Large files**: Consider processing files in batches for very large repositories

### Debug Mode

```yaml
- name: Format with debug output
  uses: QuantEcon/meta/.github/actions/code-style-checker@main
  with:
    files: ${{ steps.changed-files.outputs.all_changed_files }}
  env:
    ACTIONS_STEP_DEBUG: true
```