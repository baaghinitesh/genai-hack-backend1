# 🔄 GitHub Collaboration Workflow

## 🎯 Recommended Workflow: Fork + Branch + PR

This is the **safest and most professional** approach for team collaboration.

### Step 1: Fork the Repository

1. Go to the main repository on GitHub
2. Click the "Fork" button in the top right
3. This creates your own copy of the repository

### Step 2: Clone Your Fork

```bash
# Clone your forked repository
git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
cd REPO_NAME

# Add the original repository as upstream
git remote add upstream https://github.com/ORIGINAL_OWNER/REPO_NAME.git
```

### Step 3: Create Feature Branch

```bash
# Make sure you're on main branch
git checkout main

# Pull latest changes from upstream
git pull upstream main

# Create and switch to feature branch
git checkout -b feature/your-feature-name

# Push your branch to your fork
git push origin feature/your-feature-name
```

### Step 4: Make Changes & Commit

```bash
# Make your changes
# ... edit files ...

# Add changes
git add .

# Commit with meaningful message
git commit -m "feat: add user authentication system"

# Push to your fork
git push origin feature/your-feature-name
```

### Step 5: Create Pull Request

1. Go to your fork on GitHub
2. You'll see a banner suggesting to create a PR for your new branch
3. Click "Compare & pull request"
4. Fill in:
   - **Title**: Clear description of your changes
   - **Description**: Detailed explanation of what you did
   - **Checklist**: Mark completed items
5. Click "Create pull request"

### Step 6: Code Review & Merge

1. Team lead reviews your PR
2. Address any feedback or requested changes
3. Once approved, PR gets merged to main branch

## 🚀 Alternative: Direct Collaboration

If you have **write access** to the main repository, you can work directly:

### Setup

```bash
# Clone the main repository
git clone https://github.com/ORIGINAL_OWNER/REPO_NAME.git
cd REPO_NAME

# Create feature branch
git checkout -b feature/your-feature-name
```

### Workflow

```bash
# Make changes
# ... edit files ...

# Commit
git add .
git commit -m "feat: add new feature"

# Push to main repo
git push origin feature/your-feature-name

# Create PR on GitHub
```

## 📋 Branch Naming Conventions

Use descriptive branch names:

```bash
# Features
git checkout -b feature/user-authentication
git checkout -b feature/improve-story-generation

# Bug fixes
git checkout -b fix/audio-sync-issue
git checkout -b fix/memory-leak

# Documentation
git checkout -b docs/update-readme
git checkout -b docs/add-api-docs

# Refactoring
git checkout -b refactor/optimize-image-processing
git checkout -b refactor/cleanup-code
```

## 📝 Commit Message Guidelines

Use conventional commit format:

```bash
# Format: type(scope): description

# Examples:
git commit -m "feat(auth): add user login functionality"
git commit -m "fix(audio): resolve panel 5 auto-advance issue"
git commit -m "docs(readme): update installation instructions"
git commit -m "refactor(story): optimize LLM prompt structure"
git commit -m "test(api): add unit tests for story generation"
```

### Commit Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

## 🔄 Keeping Your Fork Updated

```bash
# Fetch latest changes from upstream
git fetch upstream

# Switch to main branch
git checkout main

# Merge upstream changes
git merge upstream/main

# Push to your fork
git push origin main
```

## 🚨 Important Security Notes

### Never Commit Sensitive Data

```bash
# ❌ DON'T do this
git add servicekey.json
git commit -m "add credentials"

# ✅ DO this instead
# Keep servicekey.json in .gitignore
# Share credentials securely with team
```

### Environment Variables

```bash
# Use .env files for local development
echo "GOOGLE_APPLICATION_CREDENTIALS=./servicekey.json" > .env

# Add .env to .gitignore
echo ".env" >> .gitignore
```

## 🆘 Common Issues & Solutions

### 1. Merge Conflicts

```bash
# When you get merge conflicts
git status  # See conflicted files
# Edit conflicted files manually
git add .   # Mark conflicts as resolved
git commit  # Complete the merge
```

### 2. Rebase vs Merge

```bash
# Keep history clean with rebase
git rebase upstream/main

# Or use merge (creates merge commit)
git merge upstream/main
```

### 3. Undo Last Commit

```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1
```

## 📊 Best Practices

### Before Starting Work

1. ✅ Pull latest changes from main
2. ✅ Create feature branch
3. ✅ Set up environment variables
4. ✅ Test that everything works

### During Development

1. ✅ Commit frequently with clear messages
2. ✅ Test your changes
3. ✅ Keep commits focused and atomic
4. ✅ Update documentation if needed

### Before Submitting PR

1. ✅ Test all functionality
2. ✅ Update tests if needed
3. ✅ Check code style
4. ✅ Write clear PR description
5. ✅ Request review from team lead

## 🎉 Success Checklist

- [ ] Repository forked/cloned
- [ ] Environment variables set up
- [ ] Feature branch created
- [ ] Changes implemented and tested
- [ ] Code committed with clear messages
- [ ] Pull request created with description
- [ ] Code review completed
- [ ] Changes merged to main

---

**Happy collaborating! 🤝✨**
