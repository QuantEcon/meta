# Tests

This directory contains tests for the GitHub Actions in this repository.

## Structure

Each GitHub Action has its own test subdirectory:

- `check-warnings/` - Tests for the `.github/actions/check-warnings` action
  - `clean.html` - HTML file without warnings (negative test case)
  - `with-warnings.html` - HTML file with warnings (positive test case)

- `code-style-checker/` - Tests for the `.github/actions/code-style-checker` action
  - `unformatted-code.md` - Markdown file with poorly formatted Python code (positive test case)
  - `formatted-code.md` - Markdown file with well-formatted Python code (negative test case)
  - `no-python-code.md` - Markdown file with non-Python code blocks (negative test case)

- `link-checker/` - Tests for the `.github/actions/link-checker` action
  - `good-links.html` - HTML file with working external links (negative test case)
  - `broken-links.html` - HTML file with broken and problematic links (positive test case)
  - `redirect-links.html` - HTML file with redirected links for AI suggestion testing
- `weekly-report/` - Tests for the `.github/actions/weekly-report` action
  - `test-basic.sh` - Basic functionality test for the weekly report action

## Running Tests

Tests are automatically run by the GitHub Actions workflows in `.github/workflows/`.

- For the `check-warnings` action, tests are run by the `test-warning-check.yml` workflow.
- For the `code-style-checker` action, tests are run by the `test-code-style-checker.yml` workflow.
- For the `link-checker` action, tests are run by the `test-link-checker.yml` workflow.
- For the `weekly-report` action, tests are run by the `test-weekly-report.yml` workflow.
