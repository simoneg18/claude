# CLAUDE.md - AI Assistant Guide

> This file provides guidance for AI assistants (like Claude) working on this repository.

## Repository Overview

**Repository:** `simoneg18/claude`
**Status:** Newly initialized repository
**Primary Branch:** `main` (to be established)

This repository is in its initial state. Update this section as the project develops to include:
- Project purpose and goals
- Target users/audience
- Core functionality description

## Project Structure

```
/home/user/claude/
├── CLAUDE.md           # This file - AI assistant guidance
└── .git/               # Git configuration
```

As the project grows, document the directory structure here:

```
# Example structure (update as project develops):
├── src/                # Source code
│   ├── components/     # UI components (if applicable)
│   ├── utils/          # Utility functions
│   └── index.ts        # Entry point
├── tests/              # Test files
├── docs/               # Documentation
├── package.json        # Dependencies (Node.js projects)
└── README.md           # Project documentation
```

## Development Workflow

### Getting Started

```bash
# Clone the repository
git clone <repository-url>
cd claude

# Install dependencies (update based on project type)
# npm install        # Node.js
# pip install -r requirements.txt  # Python
# cargo build        # Rust
```

### Common Commands

Document frequently used commands here as the project develops:

```bash
# Build (example)
# npm run build

# Test (example)
# npm test

# Lint (example)
# npm run lint

# Development server (example)
# npm run dev
```

## Code Conventions

### General Guidelines

1. **Code Style**: Follow established patterns in existing code
2. **Naming Conventions**: Use descriptive, meaningful names
3. **Comments**: Add comments for complex logic, not obvious code
4. **Error Handling**: Handle errors gracefully with appropriate messages
5. **Security**: Never commit secrets, API keys, or sensitive data

### Git Workflow

1. **Branch Naming**: Use descriptive branch names
   - Features: `feature/description`
   - Bugfixes: `fix/description`
   - AI sessions: `claude/session-id`

2. **Commit Messages**: Write clear, descriptive commit messages
   - Use present tense ("Add feature" not "Added feature")
   - First line: brief summary (50 chars or less)
   - Body: detailed explanation if needed

3. **Pull Requests**: Include description of changes and testing performed

## AI Assistant Guidelines

### When Working on This Repository

1. **Read First**: Always read relevant files before making changes
2. **Understand Context**: Explore the codebase to understand patterns
3. **Minimal Changes**: Make only necessary changes, avoid over-engineering
4. **Test Changes**: Run tests after making modifications
5. **Security Aware**: Never introduce security vulnerabilities

### File Operations

- Prefer editing existing files over creating new ones
- Keep changes focused and minimal
- Preserve existing code style and formatting

### Before Committing

1. Verify changes work as expected
2. Run linting/formatting tools if available
3. Run tests if available
4. Review changes for unintended modifications

## Testing

Document testing approach as the project develops:

- **Unit Tests**: Location and running instructions
- **Integration Tests**: How to run and what they cover
- **E2E Tests**: End-to-end testing approach

## Configuration

List important configuration files and their purposes:

| File | Purpose |
|------|---------|
| `.gitignore` | Files to exclude from git |
| `package.json` | Node.js dependencies and scripts |
| `tsconfig.json` | TypeScript configuration |
| `.env.example` | Environment variable template |

## Dependencies

Document key dependencies and their purposes as they are added.

## Troubleshooting

Common issues and solutions:

### Issue: [Description]
**Solution:** [Steps to resolve]

---

## Maintenance Notes

- **Created:** 2026-01-30
- **Last Updated:** 2026-01-30

Update this file as the project evolves to keep AI assistants informed of:
- New directories and their purposes
- Changed workflows or conventions
- Important architectural decisions
- Known issues or gotchas
