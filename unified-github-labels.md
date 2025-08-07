# Unified GitHub Labels for QuantEcon Lecture Projects

This document specifies a unified set of GitHub labels to be applied at the organization level across all QuantEcon lecture repositories for consistent issue and pull request categorization.

## Target Repositories

- **lecture-python-programming** - Python programming fundamentals
- **lecture-python-intro** - Introduction to Python lectures  
- **lecture-python.myst** - Intermediate Python lectures (MyST format)
- **lecture-python-advanced.myst** - Advanced Python lectures (MyST format)
- **lecture-jax** - JAX-based computational lectures
- **continuous_time_mcs** - Continuous Time Markov Chain lectures

## Unified Label System

### 1. Issue Types
**Purpose:** Categorize the nature of issues and pull requests

| Label | Color | Description |
|-------|-------|-------------|
| `bug` | `#d73a4a` | Something isn't working correctly |
| `enhancement` | `#a2eeef` | New feature or improvement request |
| `documentation` | `#0075ca` | Improvements or additions to documentation |
| `question` | `#d876e3` | Further information is requested |
| `maintenance` | `#fef2c0` | Repository maintenance tasks |

### 2. Priority/Severity  
**Purpose:** Indicate urgency and impact level

| Label | Color | Description |
|-------|-------|-------------|
| `priority: critical` | `#b60205` | Critical issues that break functionality |
| `priority: high` | `#d93f0b` | High priority issues |
| `priority: medium` | `#fbca04` | Medium priority issues |
| `priority: low` | `#0e8a16` | Low priority issues |

### 3. Status & Workflow
**Purpose:** Track progress and workflow states

| Label | Color | Description |
|-------|-------|-------------|
| `status: ready` | `#23B685` | Ready for implementation/review |
| `status: in-progress` | `#fbca04` | Currently being worked on |
| `status: blocked` | `#e11d21` | Blocked by external dependencies |
| `status: needs-review` | `#0052cc` | Awaiting code/content review |
| `status: testing` | `#10947B` | Under testing or quality assurance |

### 4. Content Areas
**Purpose:** Categorize by lecture series or content type

| Label | Color | Description |
|-------|-------|-------------|
| `content: intro` | `#c5def5` | Python intro lecture series |
| `content: intermediate` | `#bfd4f2` | Intermediate Python lectures |
| `content: advanced` | `#b8d4ff` | Advanced Python lectures |
| `content: jax` | `#5319e7` | JAX-based lectures |
| `content: programming` | `#c7def8` | Programming fundamentals |

### 5. Technical Components
**Purpose:** Identify technical areas affected

| Label | Color | Description |
|-------|-------|-------------|
| `component: build` | `#1d76db` | Build system and compilation |
| `component: infrastructure` | `#0052cc` | CI/CD, workflows, deployment |
| `component: content` | `#006b75` | Lecture content and materials |
| `component: exercises` | `#0e8a16` | Exercises and solutions |
| `component: dependencies` | `#0366d6` | Package and dependency management |

### 6. Automation & Tooling
**Purpose:** Automated processes and tooling

| Label | Color | Description |
|-------|-------|-------------|
| `automated issue` | `#ededed` | Created by automated processes |
| `dependencies` | `#0366d6` | Dependency updates (Dependabot) |
| `github_actions` | `#000000` | GitHub Actions workflows |
| `linkchecker` | `#ededed` | Link validation reports |
| `report` | `#ededed` | Automated reports |

### 7. Special Categories
**Purpose:** Special handling and community engagement

| Label | Color | Description |
|-------|-------|-------------|
| `good first issue` | `#7057ff` | Good for newcomers |
| `help wanted` | `#008672` | Extra attention is needed |
| `duplicate` | `#cfd3d7` | Duplicate of another issue |
| `invalid` | `#e4e669` | Invalid issue or request |
| `wontfix` | `#ffffff` | Will not be fixed/implemented |

### 8. Format & Migration
**Purpose:** Content format and migration tracking

| Label | Color | Description |
|-------|-------|-------------|
| `format: myst` | `#79e0dc` | MyST markdown format |
| `format: rst` | `#c7def8` | reStructuredText format |
| `migration` | `#79e0dc` | Content migration tasks |

## Implementation Guidelines

### Organization-Level Setup

1. **GitHub Organization Settings:**
   - Navigate to QuantEcon organization settings
   - Go to "Repository defaults" > "Labels"
   - Add all unified labels with specified colors and descriptions

2. **Repository Synchronization:**
   - Apply labels to all target repositories
   - Migrate existing issues to use unified labels
   - Update repository templates and documentation

### Label Usage Best Practices

1. **Required Labels:**
   - Every issue should have at least one **issue type** label
   - Use **priority** labels for issues requiring triage
   - Apply **status** labels to track workflow progress

2. **Content Organization:**
   - Use **content area** labels to categorize by lecture series
   - Apply **component** labels for technical categorization
   - Tag automated issues with appropriate **automation** labels

3. **Special Handling:**
   - Use `good first issue` for contributor onboarding
   - Apply `help wanted` when external assistance is needed
   - Mark duplicates and invalid issues appropriately

### Migration Strategy

1. **Phase 1: Infrastructure Setup**
   - Create unified labels at organization level
   - Apply to all target repositories
   - Document usage guidelines

2. **Phase 2: Content Migration**
   - Review existing issues and PRs
   - Apply appropriate unified labels
   - Update issue templates

3. **Phase 3: Team Training**
   - Train maintainers on new label system
   - Update contribution guidelines
   - Monitor usage and adjust as needed

## Benefits

- **Consistency:** Uniform labeling across all lecture repositories
- **Discoverability:** Easier to find related issues across projects
- **Automation:** Better support for automated workflows and reporting
- **Contributor Experience:** Clear categorization for new contributors
- **Project Management:** Improved tracking and organization of work

## Maintenance

- Review label usage quarterly
- Adjust colors and descriptions based on feedback
- Add new labels as project needs evolve
- Maintain synchronization across repositories

---

*This unified labeling system ensures consistent issue and PR categorization across all QuantEcon lecture projects, improving project management and contributor experience.*