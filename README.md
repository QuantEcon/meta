# meta
For issues and discussion covering more than one repository

## Translation Automation Workflow

This repository now includes an automated workflow for translating lecture changes from English to Chinese. When lectures are modified in `QuantEcon/lecture-python.myst`, the system automatically:

1. **Detects** which lectures have been changed
2. **Checks** if those lectures have been translated to Chinese  
3. **Translates** the changes using AI
4. **Creates** a pull request in `QuantEcon/lecture-python.zh-cn`
5. **Tags** reviewers for verification

### Quick Start

1. **Setup Secrets**: Configure `GITHUB_TOKEN` and `OPENAI_API_KEY` in repository settings
2. **Integration**: Add trigger workflow to source repository (see `INTEGRATION_EXAMPLE.md`)
3. **Test**: Create a PR in the English repository to test the workflow

### Files

- 📋 **`.github/workflows/lecture-translation-migration.yml`** - Main workflow
- 🐍 **`scripts/`** - Python automation scripts  
- 📚 **`TRANSLATION_WORKFLOW.md`** - Detailed documentation
- 🔗 **`INTEGRATION_EXAMPLE.md`** - Source repository integration
- ✅ **`scripts/validate_setup.py`** - Setup validation
- 🎬 **`scripts/demo_workflow.py`** - Workflow demonstration

### Quick Validation

```bash
python scripts/validate_setup.py  # Check setup
python scripts/demo_workflow.py   # See workflow demo
```

See `TRANSLATION_WORKFLOW.md` for complete documentation.
