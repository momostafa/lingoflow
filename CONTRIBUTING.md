# Contributing to LingoFlow

Thank you for your interest in contributing to LingoFlow! This document provides guidelines for contributing to the project.

## 🤝 How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates.

When creating a bug report, include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, LLM backend)
- Screenshots or logs if applicable

### Suggesting Enhancements

1. Check existing issues and pull requests
1. Open an issue describing the enhancement
1. Discuss the implementation approach with maintainers
1. Submit a pull request if approved

## 🛠️ Development Setup

### Fork and Clone

1. Fork the repository on GitHub
1. Clone your fork locally:

```bash
git clone https://github.com/yourusername/lingoflow.git
cd lingoflow
```

### Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Install Development Tools

```bash
pip install black isort flake8 pytest
```

## 📝 Coding Standards

### Python Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Limit line length to 88 characters
- Use type hints where appropriate

### Code Formatting

Before committing, run:

```bash
black src/
isort src/
```

### Linting

```bash
flake8 src/
```

### JavaScript/HTML/CSS

- Follow existing code style in the project
- Use descriptive class and ID names
- Keep functions focused and modular
- Add comments for complex logic

## 🧪 Testing

### Running Tests

```bash
pytest
```

### Writing Tests

- Write tests for new features
- Ensure all tests pass before submitting a PR
- Aim for good test coverage

## 📦 Pull Request Process

1. Create a new branch from `main`:

```bash
git checkout -b feature/your-feature-name
```

1. Make your changes and commit them:

```bash
git add .
git commit -m "Brief description of your changes"
```

1. Push to your fork:

```bash
git push origin feature/your-feature-name
```

1. Create a pull request on GitHub with:

- A clear title describing the change
- A detailed description of what the PR does
- Reference any related issues

1. Respond to code review feedback

## 📋 Project-Specific Guidelines

### Database Changes

- Always use migrations for schema changes
- Test migrations both up and down
- Include SQL scripts in PR description if needed

### API Changes

- Update API documentation
- Maintain backward compatibility when possible
- Add tests for new endpoints

### UI Changes

- Ensure responsive design
- Test on different screen sizes
- Maintain accessibility standards

## 🎯 Areas Needing Help

We welcome contributions in these areas:

- Additional language support
- Translation accuracy improvements
- UI/UX enhancements
- Performance optimizations
- Documentation improvements
- Test coverage expansion

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to LingoFlow! 🌊
