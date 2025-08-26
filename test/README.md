# Tests

This directory contains tests for the GitHub Actions in this repository.

## Structure

Each GitHub Action has its own test subdirectory:

- `check-warnings/` - Tests for the `.github/actions/check-warnings` action
  - `clean.html` - HTML file without warnings (negative test case)
  - `with-warnings.html` - HTML file with warnings (positive test case)

- `weekly-report/` - Tests for the `.github/actions/weekly-report` action
  - `test-basic.sh` - Basic functionality test for the weekly report action

- `qe-style-guide/` - Tests for the `.github/actions/qe-style-guide` action
  - `test-basic.sh` - Basic functionality test for the style guide action
  - `test-document-with-issues.md` - Test document with various style issues
  - `clean-document.md` - Test document following style guidelines

## Running Tests

Tests are automatically run by the GitHub Actions workflows in `.github/workflows/`:

- For the `check-warnings` action, tests are run by the `test-warning-check.yml` workflow.
- For the `weekly-report` action, tests are run by the `test-weekly-report.yml` workflow.
- For the `qe-style-guide` action, tests are run by the `test-qe-style-guide.yml` workflow.

### Manual Test Execution

You can also run tests manually:

```bash
# Test check-warnings action
cd .github/actions/check-warnings && # follow test instructions in README

# Test weekly-report action
./test/weekly-report/test-basic.sh

# Test qe-style-guide action
./test/qe-style-guide/test-basic.sh
```