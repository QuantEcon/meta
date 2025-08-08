# Example: Using the Warning Check Action

This directory contains examples of how to use the `check-warnings` action in different scenarios.

## Example 1: Basic Jupyter Book Build

```yaml
name: Build and Check Jupyter Book

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-check:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install jupyter-book
        pip install -r requirements.txt
    
    - name: Build Jupyter Book
      run: |
        jupyter-book build .
    
    - name: Check for Python warnings in built HTML
      uses: QuantEcon/meta/.github/actions/check-warnings@main
      with:
        html-path: './_build/html'
        warnings: 'SyntaxWarning,DeprecationWarning,FutureWarning'
        fail-on-warning: 'true'
```

## Example 2: Non-failing Check with Reporting

```yaml
name: Build with Warning Report

on:
  push:
    branches: [ main ]

jobs:
  build-with-warning-report:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    
    - name: Build documentation
      run: |
        # Your build process here
        make html
    
    - name: Check for warnings (non-failing)
      id: warning-check
      uses: QuantEcon/meta/.github/actions/check-warnings@main
      with:
        html-path: './docs/_build/html'
        fail-on-warning: 'false'
    
    - name: Create warning report
      if: steps.warning-check.outputs.warnings-found == 'true'
      run: |
        echo "## Warning Report" >> $GITHUB_STEP_SUMMARY
        echo "Found ${{ steps.warning-check.outputs.warning-count }} warnings:" >> $GITHUB_STEP_SUMMARY
        echo '```' >> $GITHUB_STEP_SUMMARY
        echo "${{ steps.warning-check.outputs.warning-details }}" >> $GITHUB_STEP_SUMMARY
        echo '```' >> $GITHUB_STEP_SUMMARY
    
    - name: Post warning comment (for PRs)
      if: github.event_name == 'pull_request' && steps.warning-check.outputs.warnings-found == 'true'
      uses: actions/github-script@v7
      with:
        script: |
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: '⚠️ **Python Warnings Found**\n\nFound ${{ steps.warning-check.outputs.warning-count }} warnings in the built documentation:\n\n```\n${{ steps.warning-check.outputs.warning-details }}\n```'
          })
```

## Example 3: Custom Warning Types

```yaml
name: Check for Custom Warnings

on:
  workflow_dispatch:
    inputs:
      custom_warnings:
        description: 'Custom warnings to check for'
        required: false
        default: 'UserWarning,RuntimeWarning,ResourceWarning'

jobs:
  custom-warning-check:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    
    - name: Build project
      run: |
        # Your build process
        make build
    
    - name: Check for custom warnings
      uses: QuantEcon/meta/.github/actions/check-warnings@main
      with:
        html-path: './output'
        warnings: ${{ github.event.inputs.custom_warnings || 'SyntaxWarning,DeprecationWarning,FutureWarning' }}
        fail-on-warning: 'true'
```

## Example 4: Matrix Strategy

```yaml
name: Multi-version Warning Check

on:
  schedule:
    - cron: '0 2 * * 1'  # Weekly on Monday

jobs:
  warning-check-matrix:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']
        
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Build documentation
      run: |
        jupyter-book build .
    
    - name: Check for warnings
      uses: QuantEcon/meta/.github/actions/check-warnings@main
      with:
        html-path: './_build/html'
        warnings: 'SyntaxWarning,DeprecationWarning,FutureWarning'
        fail-on-warning: 'false'
      
    - name: Upload HTML artifacts if warnings found
      if: steps.warning-check.outputs.warnings-found == 'true'
      uses: actions/upload-artifact@v4
      with:
        name: html-with-warnings-py${{ matrix.python-version }}
        path: ./_build/html
```

## Tips for Usage

1. **Place the warning check after your build step**: The action needs the final HTML output to scan.

2. **Use `fail-on-warning: 'false'` for reporting**: If you want to report warnings without failing the workflow.

3. **Customize warning types**: Adjust the `warnings` input to match your project's needs.

4. **Path considerations**: Make sure the `html-path` points to where your build process outputs HTML files.

5. **Integration with existing workflows**: This action can be easily added to existing CI/CD pipelines.