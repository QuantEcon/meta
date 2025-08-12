# Translation Migration Workflow

This repository contains a GitHub Actions workflow that automatically detects when lectures are modified in the English repository (`lecture-python.myst`) and migrates those changes to the Chinese repository (`lecture-python.zh-cn`) if the lectures have already been translated.

## How It Works

### Workflow Overview

1. **Trigger**: The workflow is triggered when a PR is opened or updated in the `lecture-python.myst` repository
2. **Detection**: It identifies which lecture files have been modified
3. **Translation Check**: It checks the Chinese repository's `_toc.yml` to see which lectures have been translated
4. **Translation**: For translated lectures, it automatically translates the changes using OpenAI's API
5. **PR Creation**: It creates a new PR in the Chinese repository with the translated changes
6. **Review**: It tags @nisha617 for review of the translation
7. **Fallback**: If translation fails, it creates an issue for manual review

### Files

- `.github/workflows/lecture-translation-migration.yml`: Main workflow file
- `scripts/check_translation_status.py`: Checks which modified files have been translated
- `scripts/create_translation_pr.py`: Creates a PR with translated changes
- `scripts/create_fallback_issue.py`: Creates an issue when automatic translation fails

## Setup Requirements

### Secrets

The workflow requires the following secrets to be configured in the repository:

1. **`GITHUB_TOKEN`**: GitHub personal access token with appropriate permissions
   - Needs access to read from source repository
   - Needs access to create PRs and issues in target repository

2. **`OPENAI_API_KEY`**: OpenAI API key for translation services
   - Used to translate content from English to Chinese
   - Requires a valid OpenAI account with API access

### Permissions

The `GITHUB_TOKEN` needs the following permissions:
- `contents: read` - To read files from repositories
- `pull-requests: read` - To read PR details and files
- `contents: write` - To create branches and update files
- `pull-requests: write` - To create PRs
- `issues: write` - To create fallback issues

## Triggering the Workflow

### Automatic Triggering

The workflow can be triggered automatically from the source repository by sending a repository dispatch event:

```bash
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/QuantEcon/meta/dispatches \
  -d '{
    "event_type": "pr-opened",
    "client_payload": {
      "repository": "QuantEcon/lecture-python.myst",
      "pr_number": 123,
      "target_repo": "QuantEcon/lecture-python.zh-cn"
    }
  }'
```

### Manual Triggering

The workflow can also be triggered manually through the GitHub Actions interface:

1. Go to the Actions tab in the meta repository
2. Select "Lecture Translation Migration" workflow
3. Click "Run workflow"
4. Fill in the required parameters:
   - Source repository (e.g., `QuantEcon/lecture-python.myst`)
   - PR number
   - Target repository (e.g., `QuantEcon/lecture-python.zh-cn`)

## Integration with Source Repository

To fully automate the process, add a webhook or workflow to the source repository that triggers this workflow when PRs are opened:

```yaml
# In QuantEcon/lecture-python.myst/.github/workflows/trigger-translation.yml
name: Trigger Translation Check

on:
  pull_request:
    types: [opened, synchronize]
    paths:
      - 'lectures/*.md'

jobs:
  trigger-translation:
    runs-on: ubuntu-latest
    steps:
    - name: Trigger translation workflow
      run: |
        curl -X POST \
          -H "Authorization: token ${{ secrets.META_REPO_TOKEN }}" \
          -H "Accept: application/vnd.github.v3+json" \
          https://api.github.com/repos/QuantEcon/meta/dispatches \
          -d '{
            "event_type": "pr-opened",
            "client_payload": {
              "repository": "${{ github.repository }}",
              "pr_number": ${{ github.event.number }},
              "target_repo": "QuantEcon/lecture-python.zh-cn"
            }
          }'
```

## Translation Quality

The workflow uses OpenAI's GPT-4 model for translation with specific instructions to:

- Preserve markdown formatting
- Keep code snippets untranslated
- Maintain mathematical formulas
- Use appropriate academic Chinese terminology
- Preserve technical terms commonly used in English

## Review Process

When a translation PR is created:

1. @nisha617 is automatically tagged for review
2. The PR includes links to the original PR
3. A checklist is provided for reviewers
4. The PR description includes context about the changes

## Troubleshooting

### Common Issues

1. **Translation fails**: Check OpenAI API key and quota
2. **Permission denied**: Verify GitHub token permissions
3. **No translated files found**: Check that files are listed in target repository's `_toc.yml`

### Logs

Check the workflow logs in the Actions tab for detailed error messages and debugging information.

## Configuration

### Environment Variables

- `TRANSLATION_REVIEWER`: GitHub username for the translation reviewer (default: `nisha617`)

### Customization

The scripts can be customized for different language pairs or repositories by modifying the parameters and translation prompts.