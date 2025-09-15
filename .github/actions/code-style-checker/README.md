# Code Style Formatter Action

A GitHub Action that automatically formats Python code in MyST markdown files and standard markdown code blocks using [black](https://black.readthedocs.io/).

## Features

- **MyST Code-Cell Support**: Formats Python code in MyST `{code-cell}` directives
- **Standard Markdown Support**: Formats Python code in standard markdown fenced code blocks  
- **Language Detection**: Automatically detects Python code by language identifiers (`python`, `python3`, `ipython`, `ipython3`)
- **Selective Processing**: Configure which types of code blocks to process
- **Individual Commits**: Creates separate commits for each modified file
- **Configurable Formatting**: Customize black formatting options
- **Comprehensive Outputs**: Detailed information about files processed and changes made

## Usage

### As a Standalone Action

```yaml
- name: Format Python code in markdown files
  uses: QuantEcon/meta/.github/actions/code-style-checker@main
  with:
    files: 'lecture/aiyagari.md,lecture/mccall.md'
    check-myst-code-cells: 'true'
    check-markdown-blocks: 'true'
    python-languages: 'python,python3,ipython,ipython3'
    black-args: '--line-length=88'
    commit-files: 'true'
```

### With PR Comment Trigger

The action automatically runs when a PR comment contains `@quantecon-code-style`:

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
    - name: Checkout PR branch
      uses: actions/checkout@v4
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
        ref: ${{ github.event.pull_request.head.ref }}
    
    - name: Get changed files
      id: changed-files
      uses: tj-actions/changed-files@v40
      with:
        files: '**/*.md'
    
    - name: Format markdown files
      uses: QuantEcon/meta/.github/actions/code-style-checker@main
      with:
        files: ${{ steps.changed-files.outputs.all_changed_files }}
    
    - name: Push changes
      run: git push
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `files` | Comma-separated list of markdown files to process | ✅ | |
| `check-myst-code-cells` | Enable processing of MyST `{code-cell}` directives | ❌ | `true` |
| `check-markdown-blocks` | Enable processing of standard markdown fenced code blocks | ❌ | `true` |
| `python-languages` | Comma-separated list of language identifiers to treat as Python | ❌ | `python,python3,ipython,ipython3` |
| `black-args` | Additional arguments to pass to black | ❌ | `--line-length=88` |
| `commit-files` | Whether to commit changes to individual files | ❌ | `true` |
| `git-user-name` | Git user name for commits | ❌ | `GitHub Action` |
| `git-user-email` | Git user email for commits | ❌ | `action@github.com` |

## Outputs

| Output | Description |
|--------|-------------|
| `files-processed` | Number of files that were processed |
| `files-changed` | Number of files that had changes made |
| `total-blocks-formatted` | Total number of code blocks that were formatted |
| `changes-made` | Whether any changes were made to files (`true`/`false`) |

## Code Block Types Supported

### MyST Code-Cell Directives

```markdown
```{code-cell} python
import numpy as np
def badly_formatted(x,y):
    return x+y
```
```

### Standard Markdown Fenced Blocks

```markdown
```python
import numpy as np
def badly_formatted(x,y):
    return x+y
```
```

### Supported Language Identifiers

By default, the action recognizes these language identifiers as Python code:
- `python`
- `python3` 
- `ipython`
- `ipython3`

You can customize this list using the `python-languages` input.

## Example Workflow Trigger

To trigger the formatter on a PR, simply comment:

```
@quantecon-code-style
```

The action will:
1. Find all changed markdown files in the PR
2. Extract Python code from MyST code-cells and markdown blocks
3. Apply black formatting to the code
4. Commit changes to individual files with descriptive messages
5. Post a summary comment with results

## How It Works

1. **File Detection**: Processes only `.md` files from the provided file list
2. **Code Extraction**: Uses regex patterns to find MyST `{code-cell}` directives and standard markdown fenced code blocks
3. **Language Filtering**: Only processes blocks with Python language identifiers
4. **Black Formatting**: Creates temporary Python files and runs black with specified arguments
5. **File Updates**: Replaces original code blocks with formatted versions
6. **Git Operations**: Commits each modified file individually with descriptive commit messages

## Configuration Examples

### Only Process MyST Code-Cells

```yaml
- uses: QuantEcon/meta/.github/actions/code-style-checker@main
  with:
    files: 'lecture/*.md'
    check-myst-code-cells: 'true'
    check-markdown-blocks: 'false'
```

### Custom Black Configuration

```yaml
- uses: QuantEcon/meta/.github/actions/code-style-checker@main
  with:
    files: 'docs/*.md'
    black-args: '--line-length=100 --skip-string-normalization'
```

### Process Only Specific Python Variants

```yaml
- uses: QuantEcon/meta/.github/actions/code-style-checker@main
  with:
    files: 'examples/*.md'
    python-languages: 'python,ipython'
```

## Error Handling

The action handles common issues gracefully:

- **Invalid Python Code**: If black cannot format the code, the original code is preserved
- **Missing Files**: Non-existent files are skipped with a warning
- **Non-Python Languages**: Code blocks with other languages are skipped and logged
- **Empty Code Blocks**: Empty or whitespace-only blocks are ignored

## Commit Messages

When `commit-files` is enabled, each file gets its own commit with the format:

```
[filename.md] applying black changes to code
```

For example:
- `[aiyagari.md] applying black changes to code`
- `[mccall.md] applying black changes to code`

## See Also

- [Black Documentation](https://black.readthedocs.io/)
- [MyST Markdown](https://myst-parser.readthedocs.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)