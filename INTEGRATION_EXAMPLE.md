# Integration with Source Repository

To fully integrate this translation workflow, add the following workflow to the source repository (`QuantEcon/lecture-python.myst`):

## `.github/workflows/trigger-translation.yml`

```yaml
name: Trigger Translation Check

on:
  pull_request:
    types: [opened, synchronize, reopened]
    paths:
      - 'lectures/*.md'

jobs:
  trigger-translation:
    runs-on: ubuntu-latest
    if: github.event.pull_request.draft == false
    steps:
    - name: Trigger translation workflow
      run: |
        curl -X POST \
          -H "Authorization: token ${{ secrets.META_REPO_TOKEN }}" \
          -H "Accept: application/vnd.github.v3+json" \
          -H "Content-Type: application/json" \
          https://api.github.com/repos/QuantEcon/meta/dispatches \
          -d '{
            "event_type": "pr-opened",
            "client_payload": {
              "repository": "${{ github.repository }}",
              "pr_number": ${{ github.event.number }},
              "target_repo": "QuantEcon/lecture-python.zh-cn"
            }
          }'
    
    - name: Comment on PR
      uses: actions/github-script@v6
      with:
        script: |
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: '🔄 Translation workflow triggered! If any of the modified lectures have been translated to Chinese, a translation PR will be automatically created.'
          })
```

## Required Secrets

Add the following secret to the source repository:

- `META_REPO_TOKEN`: A GitHub personal access token with the following permissions:
  - `repo` scope for the meta repository
  - Permission to trigger workflow dispatches

## Alternative: Webhook Integration

Instead of using repository dispatch, you can set up a webhook:

1. Go to repository Settings → Webhooks
2. Add webhook with URL: `https://api.github.com/repos/QuantEcon/meta/dispatches`
3. Set content type to `application/json`
4. Select "Pull requests" events
5. Add webhook secret if needed

## Testing the Integration

1. Create a test PR in the source repository that modifies a lecture file
2. Check that the workflow is triggered in the meta repository
3. Verify that the correct files are identified for translation
4. Check that PRs or issues are created as expected

## Monitoring

Monitor the workflow execution in:
- Actions tab of the meta repository
- Check logs for debugging information
- Review created PRs and issues in target repository