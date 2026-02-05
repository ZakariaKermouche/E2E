# Contributing to E2E Big Data Pipeline

Thank you for your interest in contributing! This document provides guidelines and instructions for getting started.

## Getting Started

### Fork & Clone
```bash
git clone https://github.com/yourusername/E2E.git
cd E2E
```

### Set Up Development Environment
```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Create your feature branch
git checkout -b feature/your-feature-name
```

## Development Workflow

### Code Style
- Python: PEP 8 compliance
- SQL: UPPERCASE keywords
- YAML: 2-space indentation
- Docker: Use official base images

### Before Submitting
1. **Test your changes**
   ```bash
   docker compose down
   docker compose up -d
   # Run manual tests
   ```

2. **Check logs for errors**
   ```bash
   docker compose logs -f
   ```

3. **Update documentation**
   - Update README if changing behavior
   - Add comments for complex logic
   - Update architecture if needed

### Commit Message Format
```
type(scope): subject

body

Fixes #issue-number
```

**Types:** feat, fix, docs, style, refactor, test, chore

**Example:**
```
feat(kafka): add message compression support

Implement gzip compression for Kafka messages
to reduce network traffic and storage costs.

Fixes #42
```

## Areas for Contribution

### High Priority
- [ ] Add unit tests for DAGs
- [ ] Implement data quality checks
- [ ] Add monitoring/alerting setup
- [ ] Create example dashboards

### Medium Priority
- [ ] Performance optimization
- [ ] Documentation improvements
- [ ] Error handling enhancements
- [ ] Configuration flexibility

### Community
- [ ] Share your use cases
- [ ] Report bugs
- [ ] Suggest improvements
- [ ] Help others in discussions

## Pull Request Process

1. Update README.md with any new features
2. Follow the code style guidelines
3. Ensure all services start successfully
4. Update relevant documentation
5. Link related issues

## Reporting Issues

**Include:**
- Service logs (`docker compose logs`)
- Environment details (OS, Docker version)
- Steps to reproduce
- Expected vs actual behavior
- Error messages

## Questions?

- Check existing issues/discussions
- Review documentation
- Start a GitHub discussion

---

Happy contributing! 🎉
