#!/usr/bin/env python3
"""
Validation script for the translation workflow setup.

This script validates that all requirements are met and provides setup guidance.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_file_permissions():
    """Check that script files have execute permissions."""
    script_files = [
        'scripts/check_translation_status.py',
        'scripts/create_translation_pr.py',
        'scripts/create_fallback_issue.py',
        'scripts/test_workflow.py',
        'scripts/demo_workflow.py'
    ]
    
    issues = []
    for script in script_files:
        path = Path(script)
        if path.exists():
            if not os.access(path, os.X_OK):
                issues.append(f"{script} is not executable")
        else:
            issues.append(f"{script} does not exist")
    
    if issues:
        print("❌ File permission issues:")
        for issue in issues:
            print(f"  - {issue}")
        print("\nFix with: chmod +x scripts/*.py")
        return False
    else:
        print("✅ All script files have correct permissions")
        return True


def check_python_dependencies():
    """Check if required Python packages are available."""
    required_packages = [
        'requests',
        'PyYAML',
        'openai',
        'gitpython'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.lower().replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("⚠️  Missing Python packages (will be installed in workflow):")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nThese will be automatically installed in the GitHub Actions workflow.")
        return True  # Not a failure for our validation
    else:
        print("✅ All required Python packages are available")
        return True


def check_secrets_guidance():
    """Provide guidance on required secrets."""
    print("🔐 Required Secrets Setup:")
    print("  1. GITHUB_TOKEN:")
    print("     - Go to GitHub Settings > Developer settings > Personal access tokens")
    print("     - Create token with 'repo' scope")
    print("     - Add as repository secret")
    print("")
    print("  2. OPENAI_API_KEY:")
    print("     - Get API key from https://platform.openai.com/api-keys")
    print("     - Add as repository secret")
    print("")
    print("  3. Repository permissions:")
    print("     - Token needs read access to source repository")
    print("     - Token needs write access to target repository")
    print("")
    return True


def check_workflow_syntax():
    """Validate workflow YAML syntax."""
    try:
        import yaml
        workflow_file = '.github/workflows/lecture-translation-migration.yml'
        with open(workflow_file, 'r') as f:
            yaml.safe_load(f)
        print("✅ GitHub Actions workflow syntax is valid")
        return True
    except Exception as e:
        print(f"❌ Workflow syntax error: {e}")
        return False


def check_integration_setup():
    """Provide integration setup guidance."""
    print("🔗 Integration Setup:")
    print("  1. In the source repository (lecture-python.myst):")
    print("     - Add the workflow from INTEGRATION_EXAMPLE.md")
    print("     - Configure META_REPO_TOKEN secret")
    print("")
    print("  2. Alternative: Set up webhook")
    print("     - Repository Settings > Webhooks")
    print("     - Point to GitHub API dispatch endpoint")
    print("")
    return True


def main():
    """Run all validation checks."""
    print("🔧 Translation Workflow Validation")
    print("=" * 50)
    
    checks = [
        ("File Permissions", check_file_permissions),
        ("Python Dependencies", check_python_dependencies),
        ("Workflow Syntax", check_workflow_syntax),
        ("Secrets Guidance", check_secrets_guidance),
        ("Integration Guidance", check_integration_setup)
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n{name}:")
        print("-" * len(name))
        try:
            result = check_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ Error in {name}: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 Validation complete! Workflow is ready for deployment.")
        print("\n📋 Next steps:")
        print("1. Configure required secrets in repository settings")
        print("2. Set up integration in source repository")
        print("3. Test with a real PR")
        print("4. Monitor workflow execution in Actions tab")
    else:
        print("❌ Some issues need to be resolved before deployment.")
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())