# Branch Protection Setup

This document explains how to set up branch protection rules for the Bridge Club Management System repository.

## 🎯 Branch Strategy

- **main** - Production branch (protected, auto-deploys to live site)
- **dev/test-site** - Staging branch (protected, auto-deploys to staging)
- **develop** - Integration branch (protected)
- **feature/** - Feature branches (merge to develop via PR)

## 🛡️ Required Branch Protection Rules

### 1. Main Branch Protection

**❗ CRITICAL: Main branch hosts live production site**

Settings to configure in GitHub > Settings > Branches:

```
Branch name pattern: main
☑️ Restrict pushes that create files larger than 100MB
☑️ Require a pull request before merging
  ☑️ Require approvals: 1
  ☑️ Dismiss stale PR approvals when new commits are pushed
  ☑️ Require review from code owners
☑️ Require status checks to pass before merging
  ☑️ Require branches to be up to date before merging
  Required status checks:
    - test (Django CI)
☑️ Require conversation resolution before merging
☑️ Require signed commits (recommended)
☑️ Require linear history
☑️ Include administrators
```

### 2. Dev/Test-Site Branch Protection

**Staging environment - less strict but still protected**

```
Branch name pattern: dev/test-site
☑️ Require a pull request before merging
  ☑️ Require approvals: 1
☑️ Require status checks to pass before merging
  ☑️ Require branches to be up to date before merging
  Required status checks:
    - test (Django CI)
☑️ Require conversation resolution before merging
```

### 3. Develop Branch Protection

**Integration branch**

```
Branch name pattern: develop
☑️ Require a pull request before merging
☑️ Require status checks to pass before merging
  Required status checks:
    - test (Django CI)
```

## 🔄 Workflow Process

### Feature Development

1. **Create feature branch from develop**:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Work on feature and push**:
   ```bash
   git add .
   git commit -m "Add feature description"
   git push origin feature/your-feature-name
   ```

3. **Create PR to develop**:
   - Go to GitHub repository
   - Click "New Pull Request"
   - Base: `develop` ← Compare: `feature/your-feature-name`
   - Add description and submit

4. **After PR approval and merge to develop**:
   ```bash
   git checkout develop
   git pull origin develop
   git branch -d feature/your-feature-name  # Clean up local branch
   ```

### Staging Deployment

1. **Create PR from develop to dev/test-site**:
   - Base: `dev/test-site` ← Compare: `develop`
   - This triggers staging deployment

2. **Test on staging environment**

3. **If issues found**: Fix in new feature branch → develop → staging

### Production Deployment

1. **Only when staging is fully tested**:
   - Create PR: `main` ← `dev/test-site`
   - Get required approvals
   - Merge triggers production deployment

## 🚨 Emergency Procedures

### Hotfix Process

For critical production fixes:

1. **Create hotfix branch from main**:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/critical-fix
   ```

2. **Fix issue and test locally**

3. **Create PR directly to main**:
   - Base: `main` ← Compare: `hotfix/critical-fix`
   - Mark as urgent/hotfix
   - Get emergency approval

4. **After merge, sync back to other branches**:
   ```bash
   # Merge main changes back to dev/test-site and develop
   git checkout dev/test-site
   git pull origin main
   git push origin dev/test-site
   
   git checkout develop
   git pull origin main
   git push origin develop
   ```

### Rollback Process

If production deployment fails:

1. **Immediate rollback**:
   ```bash
   git checkout main
   git log --oneline -10  # Find last good commit
   git revert <bad-commit-hash>
   git push origin main
   ```

2. **Or reset to previous state** (if safe):
   ```bash
   git reset --hard <last-good-commit>
   git push --force-with-lease origin main
   ```

## 📋 Setup Checklist

### GitHub Repository Settings

- [ ] Go to GitHub repository Settings
- [ ] Click "Branches" in left sidebar
- [ ] Add branch protection rules for each branch
- [ ] Test by creating a test PR

### Team Access

- [ ] Add team members as collaborators
- [ ] Set appropriate permissions:
  - **Admin**: Lead developers
  - **Write**: Regular developers
  - **Read**: Stakeholders/observers

### Notifications

- [ ] Set up Slack/email notifications for:
  - Failed deployments
  - PR reviews needed
  - Production deployments

## 🔍 Monitoring

### Regular Checks

- [ ] Weekly review of branch protection compliance
- [ ] Monitor failed CI/CD runs
- [ ] Review deployment logs
- [ ] Check for security vulnerabilities

### Metrics to Track

- PR review time
- Deployment frequency
- Failed deployment rate
- Hotfix frequency

## 🛠️ Tools Integration

### VS Code Settings

Add to `.vscode/settings.json`:
```json
{
  "git.branchProtection": ["main", "dev/test-site", "develop"],
  "git.alwaysSignOff": true,
  "git.enableCommitSigning": true
}
```

### Git Hooks

Consider adding pre-commit hooks:
```bash
# Install pre-commit
pip install pre-commit

# Add .pre-commit-config.yaml
# Configure hooks for linting, testing
```

## 📞 Support

For questions about branch protection setup:
1. Check this documentation
2. Review GitHub's branch protection documentation
3. Contact repository administrator
4. Create issue in repository for clarification

---

**Remember**: These protections are in place to maintain the stability and quality of our production system. Always follow the established workflow!