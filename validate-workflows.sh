#!/bin/bash

# Workflow Validation Script for QuantEcon Modernized CI/CD
# This script validates the workflow templates for syntax and best practices

echo "🔍 Validating QuantEcon Modernized Workflows..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if yamllint is available
check_yamllint() {
    if ! command -v yamllint &> /dev/null; then
        echo -e "${YELLOW}Warning: yamllint not found. Installing...${NC}"
        pip install yamllint || {
            echo -e "${RED}Failed to install yamllint. Skipping YAML validation.${NC}"
            return 1
        }
    fi
    return 0
}

# Function to validate YAML syntax
validate_yaml() {
    local file="$1"
    echo -n "  Checking YAML syntax for $(basename "$file")... "
    
    if check_yamllint && yamllint "$file" -d '{extends: default, rules: {line-length: {max: 120}}}' &>/dev/null; then
        echo -e "${GREEN}✓${NC}"
        return 0
    elif python3 -c "import yaml; yaml.safe_load(open('$file'))" &>/dev/null; then
        echo -e "${YELLOW}✓ (basic)${NC}"
        return 0
    else
        echo -e "${RED}✗${NC}"
        return 1
    fi
}

# Function to check for required GitHub Actions
validate_actions() {
    local file="$1"
    echo -n "  Checking GitHub Actions usage in $(basename "$file")... "
    
    # Check for pinned action versions
    if grep -q "uses:.*@v[0-9]" "$file"; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${YELLOW}⚠ (no pinned versions found)${NC}"
    fi
}

# Function to check for security best practices
validate_security() {
    local file="$1"
    echo -n "  Checking security practices in $(basename "$file")... "
    
    local issues=0
    
    # Check for hardcoded secrets (should use ${{ secrets.* }})
    if grep -qE "(password|token|key).*[:=].*['\"][^$]" "$file"; then
        echo -e "${RED}✗ (possible hardcoded secrets)${NC}"
        return 1
    fi
    
    # Check for proper permissions
    if grep -q "permissions:" "$file" || ! grep -q "GITHUB_TOKEN" "$file"; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${YELLOW}⚠ (consider explicit permissions)${NC}"
    fi
}

# Function to validate workflow triggers
validate_triggers() {
    local file="$1"
    echo -n "  Checking workflow triggers in $(basename "$file")... "
    
    if grep -q "on:" "$file"; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗ (no triggers found)${NC}"
        return 1
    fi
}

# Main validation function
validate_workflow() {
    local file="$1"
    echo "📄 Validating: $(basename "$file")"
    
    local total_checks=0
    local passed_checks=0
    
    # YAML syntax
    if validate_yaml "$file"; then
        ((passed_checks++))
    fi
    ((total_checks++))
    
    # GitHub Actions usage
    validate_actions "$file"
    ((total_checks++))
    ((passed_checks++))  # This check is informational
    
    # Security practices
    if validate_security "$file"; then
        ((passed_checks++))
    fi
    ((total_checks++))
    
    # Workflow triggers
    if validate_triggers "$file"; then
        ((passed_checks++))
    fi
    ((total_checks++))
    
    echo "  Result: ${passed_checks}/${total_checks} checks passed"
    echo ""
    
    return $((total_checks - passed_checks))
}

# Find and validate all workflow files
workflow_dir=".github/workflows"
action_dir=".github/actions"

total_errors=0

if [ -d "$workflow_dir" ]; then
    echo "🔧 Validating Workflows:"
    echo "------------------------"
    
    for workflow in "$workflow_dir"/*.yml "$workflow_dir"/*.yaml; do
        if [ -f "$workflow" ]; then
            validate_workflow "$workflow"
            total_errors=$((total_errors + $?))
        fi
    done
fi

if [ -d "$action_dir" ]; then
    echo "🎯 Validating Composite Actions:"
    echo "---------------------------------"
    
    find "$action_dir" -name "action.yml" -o -name "action.yaml" | while read -r action; do
        validate_workflow "$action"
        total_errors=$((total_errors + $?))
    done
fi

# Summary
echo "📊 Validation Summary:"
echo "======================"

if [ $total_errors -eq 0 ]; then
    echo -e "${GREEN}✅ All workflows passed validation!${NC}"
    echo ""
    echo "The modernized workflows are ready for deployment to QuantEcon repositories."
    echo ""
    echo "Next steps:"
    echo "  1. Review the MIGRATION_GUIDE.md for deployment instructions"
    echo "  2. Test in a development branch before deploying to production"
    echo "  3. Update repository settings as described in the migration guide"
else
    echo -e "${RED}❌ Found $total_errors issues that should be addressed.${NC}"
    echo ""
    echo "Please review the output above and fix any critical issues before deployment."
fi

exit $total_errors