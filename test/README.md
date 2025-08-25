# Tests

This directory contains tests for the GitHub Actions in this repository.

## Structure

Each GitHub Action has its own test subdirectory:

- `check-warnings/` - Tests for the `.github/actions/check-warnings` action
  - `clean.html` - HTML file without warnings (negative test case)
  - `with-warnings.html` - HTML file with warnings (positive test case)

- `weekly-report/` - Tests for the `.github/actions/weekly-report` action
  - `test-basic.sh` - Basic functionality test for the weekly report action

- `style-guide-checker/` - Tests for the `.github/actions/style-guide-checker` action
  - `clean-lecture.md` - Clean lecture file following style guide (negative test case)
  - `bad-style-lecture.md` - Lecture with style issues (positive test case)
  - `exclude-me.md` - File for testing exclusion patterns
  - `test-basic.sh` - Basic functionality test for the style guide checker action

## Running Tests

Tests are automatically run by the GitHub Actions workflows in `.github/workflows/`.

- For the `check-warnings` action, tests are run by the `test-warning-check.yml` workflow.
- For the `weekly-report` action, tests are run by the `test-weekly-report.yml` workflow.
- For the `style-guide-checker` action, tests are run by the `test-style-guide-checker.yml` workflow.