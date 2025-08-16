# Check for Python Warnings Action

This GitHub Action scans HTML files for Python warnings and optionally fails the workflow if any are found. It's designed to be used after building documentation or running code that generates HTML output, to ensure that no warnings are present in the final output.

**Important:** This action specifically targets warnings found within code cell outputs (elements with `cell_output` class) to avoid false positives from warnings mentioned in text content.

## Features

- Scans HTML files for configurable Python warnings **within code cell outputs only**
- Prevents false positives by only checking warnings in `cell_output` HTML elements
- Supports multiple warning types (all Python warning types by default: UserWarning, DeprecationWarning, PendingDeprecationWarning, SyntaxWarning, RuntimeWarning, FutureWarning, ImportWarning, UnicodeWarning, BytesWarning, ResourceWarning, EncodingWarning)
- Provides detailed output about warnings found
- Optionally fails the workflow when warnings are detected
- **Creates GitHub issues** with detailed warning reports
- **Generates workflow artifacts** containing warning reports
- **Posts PR comments** with warning reports when failing on warnings
- Configurable search path and warning types

## Usage

### Basic Usage

```yaml
- name: Check for Python warnings
  uses: QuantEcon/meta/.github/actions/check-warnings@main
```

### Advanced Usage with PR Comments

```yaml
- name: Check for Python warnings with PR feedback
  uses: QuantEcon/meta/.github/actions/check-warnings@main
  with:
    html-path: './_build/html'
    # Uses comprehensive default warnings (all Python warning types)
    fail-on-warning: 'true'  # This will post a comment to the PR if warnings are found
```

### Advanced Usage with Issue Creation

```yaml
- name: Check for Python warnings with issue creation
  uses: QuantEcon/meta/.github/actions/check-warnings@main
  with:
    html-path: './_build/html'
    # Uses comprehensive default warnings (all Python warning types)
    fail-on-warning: 'false'
    create-issue: 'true'
    issue-title: 'Python Warnings Found in Documentation Build'
```

### Advanced Usage with Issue Creation and User Assignment

```yaml
- name: Check for Python warnings with assigned issue
  uses: QuantEcon/meta/.github/actions/check-warnings@main
  with:
    html-path: './_build/html'
    # Uses comprehensive default warnings (all Python warning types)
    fail-on-warning: 'false'
    create-issue: 'true'
    issue-title: 'Python Warnings Found in Documentation Build'
    notify: 'username1,username2'  # Assign issue to multiple users
```

### Advanced Usage with Artifact Creation

```yaml
- name: Check for Python warnings with artifact
  uses: QuantEcon/meta/.github/actions/check-warnings@main
  with:
    html-path: './_build/html'
    # Uses comprehensive default warnings (all Python warning types)
    fail-on-warning: 'true'
    create-artifact: 'true'
    artifact-name: 'python-warning-report'
```

### Complete Advanced Usage

```yaml
- name: Check for Python warnings in build output
  uses: QuantEcon/meta/.github/actions/check-warnings@main
  with:
    html-path: './_build/html'
    # Uses comprehensive default warnings (all Python warning types)
    fail-on-warning: 'false'
    create-issue: 'true'
    issue-title: 'Python Warnings Detected in Build'
    notify: 'maintainer1,reviewer2'  # Assign to specific team members
    create-artifact: 'true'
    artifact-name: 'detailed-warning-report'
```

### Excluding Specific Warning Types

Sometimes you may want to temporarily exclude certain warning types (e.g., when dealing with upstream warnings that take time to fix):

```yaml
- name: Check for Python warnings excluding upstream warnings
  uses: QuantEcon/meta/.github/actions/check-warnings@main
  with:
    html-path: './_build/html'
    exclude-warning: 'UserWarning'  # Exclude single warning type
    fail-on-warning: 'true'
```

```yaml
- name: Check for Python warnings excluding multiple warning types
  uses: QuantEcon/meta/.github/actions/check-warnings@main
  with:
    html-path: './_build/html'
    exclude-warning: 'UserWarning,RuntimeWarning,ResourceWarning'  # Exclude multiple warnings
    fail-on-warning: 'true'
```

### Custom Warning Types with Exclusions

You can combine custom warning lists with exclusions:

```yaml
- name: Check for specific warnings but exclude problematic ones
  uses: QuantEcon/meta/.github/actions/check-warnings@main
  with:
    html-path: './_build/html'
    warnings: 'UserWarning,DeprecationWarning,RuntimeWarning,ResourceWarning'
    exclude-warning: 'ResourceWarning'  # Check all above except ResourceWarning
    fail-on-warning: 'true'
```

### Using Outputs

```yaml
- name: Check for Python warnings
  id: warning-check
  uses: QuantEcon/meta/.github/actions/check-warnings@main
  with:
    fail-on-warning: 'false'

- name: Report warnings
  if: steps.warning-check.outputs.warnings-found == 'true'
  run: |
    echo "Found ${{ steps.warning-check.outputs.warning-count }} warnings:"
    echo "${{ steps.warning-check.outputs.warning-details }}"
```

## New Features

### GitHub Issue Creation

When `create-issue` is set to `true`, the action will automatically create a GitHub issue when warnings are detected. The issue includes:

- Detailed warning information with file paths and line numbers
- Repository and workflow context
- Direct links to the failing workflow run
- Suggested next steps for resolution
- Automatic labeling (`bug`, `documentation`, `python-warnings`)

#### Automatic User Assignment

When the `notify` parameter is provided, the created issue will be automatically assigned to the specified GitHub users. This feature supports:

- Single user assignment: `notify: 'username'`
- Multiple user assignment: `notify: 'user1,user2,user3'`
- Robust error handling: If assignment fails, the issue is still created successfully

This ensures that the right team members are immediately notified about warnings and can take action to resolve them.

Additionally, when issues are created in pull request contexts, a simple notification comment is posted to the PR thread containing:

- List of files with warnings
- Direct link to the created issue for detailed information

This provides immediate awareness to PR authors without cluttering the conversation with full warning details.

### Workflow Artifacts

When `create-artifact` is set to `true`, the action generates a detailed Markdown report as a workflow artifact. This report includes:

- Complete warning details in a readable format
- Repository and workflow metadata
- Timestamp and commit information
- Downloadable for offline review

### Pull Request Comments

When `fail-on-warning` is set to `true` and warnings are found in a pull request, the action automatically posts a detailed comment to the PR containing:

- Complete warning information formatted for easy reading
- Direct links to the failing workflow run
- Suggested next steps for fixing the warnings
- Repository and commit context

This feature helps developers quickly identify and fix warnings without digging through workflow logs.

### Using Both Features Together

You can enable both issue creation and artifact generation simultaneously:

```yaml
- name: Comprehensive warning check
  uses: QuantEcon/meta/.github/actions/check-warnings@main
  with:
    html-path: './_build/html'
    fail-on-warning: 'false'  # Don't fail, just report
    create-issue: 'true'      # Create issue for tracking
    create-artifact: 'true'   # Create artifact for detailed review
```

## How It Works

This action specifically searches for Python warnings within HTML elements that have `cell_output` in their class attribute. This approach prevents false positives that would occur if warnings like "FutureWarning" or "DeprecationWarning" are mentioned in the text content of documentation pages.

### Example HTML Structure

The action will detect warnings in this structure:
```html
<div class="cell_output">
    <pre>
    /path/to/file.py:10: FutureWarning: This feature will be deprecated
      result = old_function()
    </pre>
</div>
```

But will **ignore** warnings mentioned in regular content:
```html
<div class="content">
    <p>In this tutorial, we'll discuss FutureWarning messages.</p>
</div>
```

This ensures that educational content about warnings doesn't trigger false positives in the check.

## Permissions

For the action to work correctly with all features, ensure your workflow has the appropriate permissions:

```yaml
permissions:
  contents: read          # For checking out the repository
  issues: write          # For creating GitHub issues (if create-issue is enabled)
  actions: read          # For creating workflow artifacts (if create-artifact is enabled)
  pull-requests: write   # For posting PR comments (when fail-on-warning is true OR create-issue is true in PRs)
```

If you're only using the basic warning check functionality, only `contents: read` is required. Add `pull-requests: write` when you want PR comments on warnings or when using issue creation in PR contexts.

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `html-path` | Path to directory containing HTML files to scan | No | `.` |
| `warnings` | Comma-separated list of warnings to check for | No | `UserWarning,DeprecationWarning,PendingDeprecationWarning,SyntaxWarning,RuntimeWarning,FutureWarning,ImportWarning,UnicodeWarning,BytesWarning,ResourceWarning,EncodingWarning` |
| `exclude-warning` | Comma-separated list of warnings to exclude from checking (can be a single warning or multiple warnings) | No | `` |
| `fail-on-warning` | Whether to fail the workflow if warnings are found | No | `true` |
| `create-issue` | Whether to create a GitHub issue when warnings are found | No | `false` |
| `issue-title` | Title for the GitHub issue when warnings are found | No | `Python Warnings Found in Documentation Build` |
| `create-artifact` | Whether to create a workflow artifact with the warning report | No | `false` |
| `artifact-name` | Name for the workflow artifact containing the warning report | No | `warning-report` |
| `notify` | GitHub username(s) to assign to the created issue (comma-separated for multiple users) | No | `` |

## Outputs

| Output | Description |
|--------|-------------|
| `warnings-found` | Whether warnings were found (`true`/`false`) |
| `warning-count` | Number of warnings found |
| `warning-details` | Details of warnings found |
| `issue-url` | URL of the created GitHub issue (if `create-issue` is enabled) |
| `artifact-path` | Path to the created artifact file (if `create-artifact` is enabled) |

## Example Workflow

Here's a complete example of how to use this action in a workflow:

```yaml
name: Build and Check Documentation

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

permissions:
  contents: read
  issues: write
  actions: read
  pull-requests: write

jobs:
  build-and-check:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Build documentation
      run: |
        jupyter-book build .
    
    - name: Check for Python warnings
      uses: QuantEcon/meta/.github/actions/check-warnings@main
      with:
        html-path: './_build/html'
        # Uses comprehensive default warnings (all Python warning types)
        fail-on-warning: ${{ github.event_name == 'push' }}  # Fail on push, warn on PR
        create-issue: ${{ github.event_name == 'push' }}     # Create issues for main branch
        notify: 'maintainer1,reviewer2'                      # Assign issues to team members
        create-artifact: 'true'                              # Always create artifacts
        artifact-name: 'warning-report'
```

## Use Case

This action is particularly useful for:

1. **Documentation builds**: After building Jupyter Books or Sphinx documentation, check that no Python warnings appear in the generated HTML
2. **Code execution**: When running notebooks or Python scripts that generate HTML output, ensure no warnings are present
3. **Continuous Integration**: Maintain code quality by preventing warnings from being introduced

## How It Works

1. The action searches for all `.html` files in the specified directory
2. For each HTML file, it searches for the specified warning strings
3. If warnings are found, it reports the details and optionally fails the workflow
4. The action provides outputs that can be used by subsequent steps

## Error Handling

- If the specified HTML path doesn't exist, the action will fail with an error
- The action will report the exact location (file and line number) where warnings are found
- When `fail-on-warning` is `true`, the workflow will fail if any warnings are detected

## Tips for Usage

1. **Place the warning check after your build step**: The action needs the final HTML output to scan.

2. **Use `fail-on-warning: 'false'` for reporting**: If you want to report warnings without failing the workflow.

3. **Customize warning types**: Adjust the `warnings` input to match your project's needs.

4. **Exclude problematic warnings temporarily**: Use `exclude-warning` to temporarily exclude warnings from upstream dependencies or issues that take time to fix:
   ```yaml
   exclude-warning: 'UserWarning,RuntimeWarning'  # Exclude multiple warnings
   ```

5. **Path considerations**: Make sure the `html-path` points to where your build process outputs HTML files.

5. **Integration with existing workflows**: This action can be easily added to existing CI/CD pipelines.

6. **Issue management**: When using `create-issue: 'true'`, consider:
   - Setting up issue templates for consistency
   - Using branch-specific conditions to avoid duplicate issues
   - Implementing automatic issue closing when warnings are resolved

7. **Artifact usage**: Artifacts are perfect for:
   - Detailed offline review of warnings
   - Sharing warning reports with team members
   - Historical tracking of warning trends

8. **Performance considerations**: For large HTML output directories, consider:
   - Using specific paths rather than scanning entire directories
   - Limiting warning types to only those relevant to your project
   - Setting appropriate artifact retention periods

9. **Pull Request feedback**: 
   - When `fail-on-warning` is `true`: The action posts detailed warning reports as PR comments
   - When `create-issue` is `true`: The action posts simple notification comments linking to created issues
   - Both features provide immediate feedback to developers without requiring log diving
   - Requires `pull-requests: write` permission in your workflow