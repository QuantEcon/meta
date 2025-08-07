# Implementation Guide: Unified GitHub Labels

This guide provides step-by-step instructions for implementing the unified GitHub label system across QuantEcon lecture repositories.

## Quick Reference: Label Set

### Core Labels (Required for all repositories)

```yaml
# Issue Types
bug: "#d73a4a"
enhancement: "#a2eeef" 
documentation: "#0075ca"
question: "#d876e3"
maintenance: "#fef2c0"

# Priority
"priority: critical": "#b60205"
"priority: high": "#d93f0b"
"priority: medium": "#fbca04"
"priority: low": "#0e8a16"

# Status
"status: ready": "#23B685"
"status: in-progress": "#fbca04"
"status: blocked": "#e11d21"
"status: needs-review": "#0052cc"
"status: testing": "#10947B"

# Automation
"automated issue": "#ededed"
dependencies: "#0366d6"
github_actions: "#000000"
linkchecker: "#ededed"
report: "#ededed"

# Special
"good first issue": "#7057ff"
"help wanted": "#008672"
duplicate: "#cfd3d7"
invalid: "#e4e669"
wontfix: "#ffffff"
```

### Repository-Specific Labels

Add these based on repository content:

```yaml
# Content Areas (choose relevant ones)
"content: intro": "#c5def5"
"content: intermediate": "#bfd4f2" 
"content: advanced": "#b8d4ff"
"content: jax": "#5319e7"
"content: programming": "#c7def8"

# Components
"component: build": "#1d76db"
"component: infrastructure": "#0052cc"
"component: content": "#006b75"
"component: exercises": "#0e8a16"
"component: dependencies": "#0366d6"

# Format
"format: myst": "#79e0dc"
"format: rst": "#c7def8"
migration: "#79e0dc"
```

## Implementation Steps

### Step 1: Organization-Level Setup

1. **Access Organization Settings:**
   ```
   Navigate to: https://github.com/orgs/QuantEcon/settings
   → Repository defaults → Labels
   ```

2. **Create Default Labels:**
   - Click "New label" for each unified label
   - Enter name, color (hex code), and description
   - Save each label

### Step 2: Repository Application

For each target repository:

1. **Access Repository Labels:**
   ```
   Repository → Issues → Labels
   ```

2. **Clean Up Existing Labels:**
   - Review current labels
   - Delete or rename conflicting labels
   - Preserve any repository-specific labels that don't conflict

3. **Apply Unified Labels:**
   - Use GitHub's "Labels" API or manual creation
   - Apply all core labels plus relevant repository-specific labels

### Step 3: Bulk Label Management

**Using GitHub CLI:**

```bash
# Install GitHub CLI if not already installed
# List current labels
gh label list --repo QuantEcon/[repository-name]

# Create new labels (example)
gh label create "priority: critical" --description "Critical issues that break functionality" --color "b60205" --repo QuantEcon/[repository-name]

# Delete old labels
gh label delete "old-label-name" --repo QuantEcon/[repository-name]
```

**Using GitHub API:**

```bash
# Create label via API
curl -X POST \
  https://api.github.com/repos/QuantEcon/[repository-name]/labels \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "priority: critical",
    "description": "Critical issues that break functionality",
    "color": "b60205"
  }'
```

### Step 4: Issue and PR Migration

1. **Review Existing Issues:**
   - Identify issues with old/non-standard labels
   - Apply appropriate unified labels
   - Remove deprecated labels

2. **Update Issue Templates:**
   ```yaml
   # .github/ISSUE_TEMPLATE/bug_report.yml
   labels: ["bug", "status: needs-review"]
   
   # .github/ISSUE_TEMPLATE/feature_request.yml  
   labels: ["enhancement", "status: needs-review"]
   ```

3. **Update Pull Request Templates:**
   ```markdown
   ## Type of Change
   - [ ] Bug fix (add `bug` label)
   - [ ] New feature (add `enhancement` label)
   - [ ] Documentation update (add `documentation` label)
   - [ ] Maintenance (add `maintenance` label)
   ```

### Step 5: Automation Updates

1. **Update Dependabot Configuration:**
   ```yaml
   # .github/dependabot.yml
   updates:
     - package-ecosystem: "pip"
       directory: "/"
       schedule:
         interval: "weekly"
       labels:
         - "dependencies"
         - "maintenance"
   ```

2. **Update GitHub Actions:**
   ```yaml
   # Example workflow for auto-labeling
   - name: Label PRs
     uses: actions/labeler@v4
     with:
       repo-token: "${{ secrets.GITHUB_TOKEN }}"
       configuration-path: .github/labeler.yml
   ```

## Repository-Specific Configurations

### lecture-python-programming
```yaml
Content labels: ["content: programming"]
Special: ["format: rst"] (if still using RST)
Focus: Programming fundamentals and introductory content
```

### lecture-python-intro  
```yaml
Content labels: ["content: intro"]
Special: ["format: myst"]
Focus: Introduction level Python lectures
```

### lecture-python.myst
```yaml
Content labels: ["content: intermediate"] 
Special: ["format: myst"]
Focus: Intermediate economics and Python
```

### lecture-python-advanced.myst
```yaml
Content labels: ["content: advanced"]
Special: ["format: myst"] 
Focus: Advanced economics and computational methods
```

### lecture-jax
```yaml
Content labels: ["content: jax"]
Special: ["format: myst"]
Focus: JAX-based computational economics
```

### continuous_time_mcs
```yaml
Content labels: ["content: intermediate"] # or create "content: continuous-time"
Special: ["format: myst"]
Focus: Continuous time Markov chains
```

## Validation and Testing

### Label Coverage Check
```bash
# Verify all required labels exist
gh label list --repo QuantEcon/[repository] | grep -E "(bug|enhancement|documentation|question|maintenance)"
```

### Usage Monitoring
1. **Weekly Review:**
   - Check label usage across repositories
   - Identify inconsistencies
   - Gather team feedback

2. **Monthly Analysis:**
   - Generate usage reports
   - Update documentation
   - Adjust label set if needed

## Troubleshooting

### Common Issues

1. **Label Name Conflicts:**
   - Delete conflicting labels first
   - Migrate issues to new labels
   - Create unified labels

2. **Color Inconsistencies:**
   - Use exact hex codes provided
   - Verify color accessibility
   - Maintain visual grouping

3. **Missing Labels:**
   - Check organization defaults
   - Verify repository permissions
   - Re-apply missing labels

### Support

- **GitHub Documentation:** [Managing labels](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels)
- **GitHub CLI:** [gh label reference](https://cli.github.com/manual/gh_label)
- **API Reference:** [Labels API](https://docs.github.com/en/rest/issues/labels)

## Success Metrics

- **Consistency:** All repositories use unified label set
- **Coverage:** 100% of issues have appropriate type labels  
- **Usage:** Regular application of status and priority labels
- **Automation:** Dependabot and workflows use correct labels
- **Community:** Contributors can easily find and categorize issues

---

*This implementation guide ensures smooth rollout of the unified labeling system across all QuantEcon lecture repositories.*