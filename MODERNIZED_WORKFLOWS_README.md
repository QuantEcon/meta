# QuantEcon Modernized CI/CD Workflows

This repository contains modernized GitHub Actions workflows for QuantEcon lecture repositories. These workflows replace third-party dependencies with GitHub-native features for improved reliability, security, and maintainability.

## Overview

The modernized workflows eliminate the following third-party dependencies:
- `dawidd6/action-download-artifact@v11` → Replaced with GitHub's native `actions/cache@v4`
- `nwtgck/actions-netlify@v3` → Replaced with GitHub-native artifact-based PR previews

## Workflow Templates

### 1. `modernized-ci.yml` - Pull Request Preview Workflow

**Replaces:** Original `ci.yml` with Netlify integration

**Key Improvements:**
- Uses `actions/cache@v4` for build caching instead of artifact downloads
- Provides PR previews via GitHub artifacts with automatic PR comments
- More efficient caching based on content hashes
- Eliminates external Netlify dependency

**Features:**
- Builds jupyter-book project on every pull request
- Caches build artifacts for faster subsequent builds
- Generates PDF and notebook downloads
- Uploads preview as GitHub artifact
- Automatically comments on PR with download instructions

### 2. `modernized-cache.yml` - Build Cache Workflow

**Replaces:** Original `cache.yml` with artifact uploads

**Key Improvements:**
- Uses GitHub's native caching mechanism
- Automatic cache invalidation based on content changes
- More efficient storage and retrieval
- Integrated with CI workflow for seamless operation

**Features:**
- Runs weekly to warm the cache
- Can be triggered manually
- Uses content-aware cache keys
- Automatic cache management

### 3. `modernized-publish.yml` - Production Deployment

**Replaces:** Original `publish.yml` with artifact downloads

**Key Improvements:**
- Uses GitHub's native caching for build optimization
- Maintains all existing functionality
- Improved reliability without external dependencies

**Features:**
- Deploys to GitHub Pages on tag push
- Syncs notebooks to separate repository
- Uses native caching for faster builds

## Migration Guide

### For Existing QuantEcon Repositories

1. **Replace workflows:**
   ```bash
   # Copy the modernized workflows to your repository
   cp modernized-ci.yml .github/workflows/ci.yml
   cp modernized-cache.yml .github/workflows/cache.yml
   cp modernized-publish.yml .github/workflows/publish.yml
   ```

2. **Remove Netlify secrets:** (if using Netlify)
   - `NETLIFY_AUTH_TOKEN`
   - `NETLIFY_SITE_ID`

3. **Update repository settings:**
   - Ensure Actions have read/write permissions for pull requests
   - No additional setup required for caching (automatic)

### Cache Key Strategy

The modernized workflows use intelligent cache keys:
```yaml
key: jupyter-book-${{ runner.os }}-${{ hashFiles('lectures/**', 'environment.yml') }}
```

This ensures:
- Cache invalidation when lecture content changes
- Cache invalidation when dependencies change
- Platform-specific caching
- Automatic cleanup of old caches

## PR Preview Workflow

Since GitHub Pages doesn't natively support PR previews, the modernized approach:

1. **Builds the site** on every PR
2. **Uploads as artifact** with PR-specific naming
3. **Comments on PR** with download instructions
4. **Provides direct link** to workflow run and artifact

### Alternative Advanced Preview Solutions

For repositories requiring live URL previews, consider these GitHub-native alternatives:

#### Option A: GitHub Codespaces Integration
```yaml
- name: Setup Codespace Preview
  run: |
    echo "Preview available in Codespace at: https://github.com/codespaces"
    echo "Run: python -m http.server 8000 --directory _build/html"
```

#### Option B: GitHub Container Registry
```yaml
- name: Build and push preview container
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: ghcr.io/${{ github.repository }}/preview:pr-${{ github.event.number }}
```

## Benefits of Modernization

### Security
- Eliminates third-party action dependencies
- Reduces attack surface
- Uses GitHub's trusted infrastructure

### Reliability
- No external service dependencies
- Built-in redundancy with GitHub's infrastructure
- Automatic failover and retry mechanisms

### Performance
- Intelligent content-based caching
- Faster cache hits with GitHub's global CDN
- Reduced build times for unchanged content

### Maintainability
- Fewer external integrations to maintain
- Standardized GitHub Actions ecosystem
- Better integration with GitHub's security features

### Cost
- Eliminates external service costs (Netlify)
- Uses included GitHub Actions minutes
- Efficient caching reduces compute usage

## Troubleshooting

### Cache Issues
```bash
# To clear cache (run in repository with GitHub CLI)
gh cache list
gh cache delete <cache-key>
```

### Artifact Access
- Artifacts are available for 30 days
- Only users with repository access can download
- Artifacts auto-expire to save storage

### Build Failures
- Check execution reports artifact for detailed logs
- Verify environment.yml dependencies
- Ensure LaTeX packages are available

## Support and Contributing

For issues specific to these workflows:
1. Check the Actions logs for detailed error messages
2. Verify cache keys are generating correctly
3. Ensure required permissions are set

For general QuantEcon lecture build issues:
- Refer to the jupyter-book documentation
- Check QuantEcon community forums
- Review lecture-specific troubleshooting guides