# Migration Guide: From Third-Party Actions to GitHub-Native CI/CD

This guide walks through migrating existing QuantEcon repositories from third-party GitHub Actions to the modernized GitHub-native workflows.

## Quick Migration Steps

### 1. Backup Current Workflows
```bash
# In your repository
mkdir backup-workflows
cp .github/workflows/*.yml backup-workflows/
```

### 2. Copy Modernized Workflows

**Option A: Use templates from this repository**
```bash
# Download templates
curl -O https://raw.githubusercontent.com/quantecon/meta/main/.github/workflows/modernized-ci.yml
curl -O https://raw.githubusercontent.com/quantecon/meta/main/.github/workflows/modernized-cache.yml
curl -O https://raw.githubusercontent.com/quantecon/meta/main/.github/workflows/modernized-publish.yml

# Replace existing workflows
mv modernized-ci.yml .github/workflows/ci.yml
mv modernized-cache.yml .github/workflows/cache.yml
mv modernized-publish.yml .github/workflows/publish.yml
```

**Option B: Use composite action approach**
```bash
# Copy the composite action
mkdir -p .github/actions
cp -r quantecon/meta/.github/actions/setup-quantecon .github/actions/

# Use the simplified workflow
curl -O https://raw.githubusercontent.com/quantecon/meta/main/.github/workflows/simplified-ci.yml
mv simplified-ci.yml .github/workflows/ci.yml
```

### 3. Update Repository Settings

1. **Remove Netlify secrets** (if using Netlify):
   - Go to Settings → Secrets and variables → Actions
   - Delete `NETLIFY_AUTH_TOKEN`
   - Delete `NETLIFY_SITE_ID`

2. **Verify GitHub Actions permissions**:
   - Go to Settings → Actions → General
   - Under "Workflow permissions", ensure "Read and write permissions" is selected
   - Enable "Allow GitHub Actions to create and approve pull requests"

### 4. Clean Up Old Cache/Artifacts

**If using the old artifact-based caching:**
```bash
# Using GitHub CLI
gh run list --workflow=cache.yml --limit=50
gh run list --workflow=cache.yml --limit=50 | grep completed | awk '{print $NF}' | xargs -I {} gh run delete {}
```

## Detailed Changes Explained

### Before: Third-Party Dependencies
```yaml
# OLD: Download artifacts from separate workflow
- name: Download "build" folder (cache)
  uses: dawidd6/action-download-artifact@v11
  with:
    workflow: cache.yml
    branch: main
    name: build-cache
    path: _build

# OLD: Deploy to Netlify
- name: Preview Deploy to Netlify
  uses: nwtgck/actions-netlify@v3
  with:
    publish-dir: '_build/html/'
    production-branch: main
    github-token: ${{ secrets.GITHUB_TOKEN }}
    deploy-message: "Preview Deploy from GitHub Actions"
  env:
    NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
    NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

### After: GitHub-Native Solutions
```yaml
# NEW: Use GitHub's native caching
- name: Cache jupyter-book build
  uses: actions/cache@v4
  with:
    path: _build
    key: jupyter-book-${{ runner.os }}-${{ hashFiles('lectures/**', 'environment.yml') }}
    restore-keys: |
      jupyter-book-${{ runner.os }}-

# NEW: Upload as artifact with PR comment
- name: Upload PR Preview Artifact
  uses: actions/upload-artifact@v4
  if: github.event_name == 'pull_request'
  with:
    name: pr-preview-${{ github.event.number }}
    path: '_build/html/'
    retention-days: 30
```

## Benefits After Migration

| Aspect | Before | After |
|--------|--------|-------|
| **Security** | Third-party dependencies | GitHub-native only |
| **Reliability** | External service dependencies | GitHub infrastructure |
| **Cost** | Netlify costs | GitHub Actions included |
| **Maintenance** | Multiple external integrations | Single GitHub ecosystem |
| **Caching** | Artifact up/download | Smart content-based caching |
| **Speed** | Slower artifact transfers | Faster cache hits |

## Testing the Migration

### 1. Test Build Cache
```bash
# Create a test PR and verify:
git checkout -b test-modernized-ci
git commit --allow-empty -m "Test modernized CI"
git push origin test-modernized-ci

# Check that cache is created and used in subsequent runs
```

### 2. Test PR Preview
1. Open a PR with the new workflow
2. Verify that:
   - Build completes successfully
   - Artifact is uploaded with correct name
   - PR comment is posted with download link
   - Artifact contains the built site

### 3. Test Production Deployment
```bash
# Test with a tag (be careful - this deploys to production!)
git tag publish-test-v1.0.0
git push origin publish-test-v1.0.0
```

## Troubleshooting Common Issues

### Cache Not Working
```yaml
# Verify cache key is generating correctly
- name: Debug cache key
  run: |
    echo "Cache key would be: jupyter-book-${{ runner.os }}-${{ hashFiles('lectures/**', 'environment.yml') }}"
    find lectures -name "*.md" -o -name "*.ipynb" | head -10
```

### Permissions Issues
```yaml
# Add explicit permissions if needed
permissions:
  contents: read
  pull-requests: write
  actions: read
```

### Build Failures
1. Check that all dependencies are in `environment.yml`
2. Verify LaTeX packages are installed correctly
3. Check execution reports artifact for detailed logs

### Large Repository Concerns
For large repositories, consider:
```yaml
# Increase cache size limit and add more specific paths
- name: Cache jupyter-book build
  uses: actions/cache@v4
  with:
    path: |
      _build
      ~/.cache/pip
    key: jupyter-book-${{ runner.os }}-${{ hashFiles('lectures/**', 'environment.yml', 'requirements.txt') }}
```

## Rollback Plan

If issues arise, you can quickly rollback:
```bash
# Restore original workflows
cp backup-workflows/*.yml .github/workflows/
git add .github/workflows/
git commit -m "Rollback to original workflows"
git push
```

## Repository-Specific Considerations

### For `lecture-python-programming.myst`
- Verify notebook sync still works in publish workflow
- Test PDF generation with new caching
- Confirm CNAME setting in publish workflow

### For Other Lecture Repositories
- Update repository-specific URLs in publish workflow
- Verify environment.yml compatibility
- Test with repository-specific build commands

## Support

For migration issues:
1. Check the workflow run logs in GitHub Actions
2. Compare with working examples in this meta repository
3. Open an issue in the quantecon/meta repository
4. Refer to GitHub Actions documentation for native features