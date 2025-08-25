# Tests

This directory contains tests for the GitHub Actions in this repository.

## Structure

Each GitHub Action has its own test subdirectory:

- `check-warnings/` - Tests for the `.github/actions/check-warnings` action
  - `clean.html` - HTML file without warnings (negative test case)
  - `with-warnings.html` - HTML file with warnings (positive test case)

- `weekly-report/` - Tests for the `.github/actions/weekly-report` action
  - `test-basic.sh` - Basic functionality test for the weekly report action

- `qe-style-check/` - Tests for the `.github/actions/qe-style-check` action
  - `test-basic.sh` - Basic functionality test for the style checker
  - `test-lecture-with-issues.md` - Test file containing style violations
  - `test-lecture-clean.md` - Test file following style guidelines

## Running Tests

Tests are automatically run by the GitHub Actions workflows in `.github/workflows/`.

- For the `check-warnings` action, tests are run by the `test-warning-check.yml` workflow.
- For the `weekly-report` action, tests are run by the `test-weekly-report.yml` workflow.
- For the `qe-style-check` action, tests are run by the `test-qe-style-check.yml` workflow.

### Local Testing

You can run tests locally:

```bash
# Test warning checker
cd test/check-warnings && ../../.github/actions/check-warnings/action.yml

# Test weekly report
cd test/weekly-report && ./test-basic.sh

# Test style checker
cd test/qe-style-check && ./test-basic.sh
```