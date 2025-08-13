# QuantEcon Meta Repository

This repository contains shared resources, templates, and documentation for the QuantEcon organization.

## 🚀 Modernized CI/CD Workflows

This repository provides modernized GitHub Actions workflows that replace third-party dependencies with GitHub-native features for improved security, reliability, and maintainability.

### Quick Start

For QuantEcon lecture repositories, use these modernized workflows:

- **[`modernized-ci.yml`](.github/workflows/modernized-ci.yml)** - PR previews with artifact downloads (replaces Netlify)
- **[`modernized-cache.yml`](.github/workflows/modernized-cache.yml)** - Intelligent build caching (replaces artifact downloads)
- **[`modernized-publish.yml`](.github/workflows/modernized-publish.yml)** - Production deployment with native caching

### Key Improvements

✅ **Eliminates third-party dependencies:**
- `dawidd6/action-download-artifact@v11` → `actions/cache@v4`
- `nwtgck/actions-netlify@v3` → GitHub artifacts + PR comments

✅ **Enhanced security and reliability**
✅ **Faster builds with intelligent caching**
✅ **Zero external service costs**

## 📖 Documentation

- **[Modernized Workflows README](MODERNIZED_WORKFLOWS_README.md)** - Comprehensive guide to the new workflows
- **[Migration Guide](MIGRATION_GUIDE.md)** - Step-by-step migration instructions
- **[Composite Action](/.github/actions/setup-quantecon/)** - Reusable setup action

## 🔧 Available Templates

1. **Standard CI with native caching** - [`modernized-ci.yml`](.github/workflows/modernized-ci.yml)
2. **Simplified CI with composite action** - [`simplified-ci.yml`](.github/workflows/simplified-ci.yml)
3. **Advanced PR previews** - [`advanced-pr-preview.yml`](.github/workflows/advanced-pr-preview.yml)
4. **Build caching** - [`modernized-cache.yml`](.github/workflows/modernized-cache.yml)
5. **Production deployment** - [`modernized-publish.yml`](.github/workflows/modernized-publish.yml)

## 🏗️ For Repository Maintainers

To adopt the modernized workflows in your QuantEcon repository:

```bash
# Copy workflow templates
curl -O https://raw.githubusercontent.com/quantecon/meta/main/.github/workflows/modernized-ci.yml
curl -O https://raw.githubusercontent.com/quantecon/meta/main/.github/workflows/modernized-cache.yml
curl -O https://raw.githubusercontent.com/quantecon/meta/main/.github/workflows/modernized-publish.yml

# Replace existing workflows
mv modernized-*.yml .github/workflows/
```

See the [Migration Guide](MIGRATION_GUIDE.md) for detailed instructions.

## 📋 Meta Repository Purpose

This repository serves as:
- **Issue tracking** for cross-repository concerns
- **Template storage** for shared workflows and actions
- **Documentation hub** for QuantEcon development practices
- **Discussion space** for organization-wide decisions

## 🤝 Contributing

For issues and discussion covering more than one QuantEcon repository, please open an issue here. For repository-specific issues, use the respective repository's issue tracker.
