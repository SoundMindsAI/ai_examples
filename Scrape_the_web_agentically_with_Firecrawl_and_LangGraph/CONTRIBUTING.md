# Contributing to FireCrawl

We love your input! We want to make contributing to FireCrawl as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Development Setup

1. Clone your fork of the repo
   ```bash
   git clone https://github.com/YOUR_USERNAME/firecrawl.git
   ```

2. Create a virtual environment and activate it
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies
   ```bash
   pip install -e ".[dev]"
   ```

4. Set up pre-commit hooks (recommended)
   ```bash
   pre-commit install
   ```

## Pull Request Process

1. Update the README.md with details of changes to the interface, if applicable.
2. Update the version numbers in:
   - `src/firecrawl/__init__.py`
   - `setup.py`
3. The PR may be merged once you have the sign-off of at least one other developer.

## Any Contributions You Make Will Be Under the MIT Software License
In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report Bugs Using GitHub's [Issue Tracker](https://github.com/your-username/firecrawl/issues)
We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/your-username/firecrawl/issues/new); it's that easy!

## Write Bug Reports With Detail, Background, and Sample Code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can.
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## License
By contributing, you agree that your contributions will be licensed under its MIT License.