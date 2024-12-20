# Web Scraper with Playwright

A simple yet powerful web scraper built with Python and Playwright. This scraper can navigate through websites, extract content, and follow links while respecting depth limits and handling errors gracefully.

- See the [inspired by code](https://github.com/trancethehuman/ai-workshop-code/blob/main/Scrape_the_web_agentically_with_Firecrawl_and_LangGraph.ipynb) for this project: 

## Overview

This project implements a web scraping system that:
- Uses Playwright for browser automation
- Handles navigation and content extraction
- Follows links to a specified depth
- Manages browser resources efficiently
- Handles errors gracefully

## Features

- **Depth-Limited Crawling**: Control how deep the scraper goes into linked pages
- **Content Extraction**: Get page titles, content, and links
- **Error Handling**: Graceful handling of navigation errors and failed requests
- **Resource Management**: Proper cleanup of browser resources
- **Link Filtering**: Smart filtering of links to avoid revisiting pages
- **Progress Tracking**: Clear output of scraping progress and results

## Prerequisites

- Python 3.9+
- Playwright
- Pydantic

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
python -m playwright install
```

## Usage

Here's a simple example of how to use the scraper:

```python
import asyncio
from scraper import WebScraper

async def run_example():
    # Create a scraper instance with a starting URL and max depth
    scraper = WebScraper(
        start_url="https://example.com",
        max_depth=2
    )
    
    # Run the scraper and get results
    results = await scraper.run()
    
    # Process results
    for url, data in results.items():
        print(f"\nURL: {url}")
        print(f"Title: {data.get('title', 'N/A')}")
        print(f"Content length: {len(data.get('content', ''))} characters")
        print(f"Found {len(data.get('links', []))} links")

if __name__ == "__main__":
    asyncio.run(run_example())
```

## API Reference

### WebScraper Class

#### Constructor
```python
WebScraper(start_url: str, max_depth: int = 3)
```
- `start_url`: The URL to start scraping from
- `max_depth`: Maximum depth of links to follow (default: 3)

#### Methods
- `run()`: Starts the scraping process and returns the extracted data
- Returns: Dict[str, Dict[str, Any]] - A dictionary mapping URLs to their extracted data

#### Extracted Data Format
For each URL, the scraper returns:
- `title`: Page title
- `content`: Page HTML content
- `links`: List of links found on the page
- `error`: Error message (if any error occurred)

## Important Notes

- Always check a website's robots.txt and terms of service before scraping
- Implement appropriate rate limiting for production use
- Some websites may block automated browsers
- Large-scale scraping may require additional error handling and retry logic

## Project Structure

```
firecrawl/
├── .env                    # Environment variables (not in version control)
├── .env.example           # Example environment variables
├── .gitignore            # Git ignore file
├── MANIFEST.in           # Package manifest
├── README.md             # Project documentation
├── requirements.txt      # Direct dependencies
├── setup.py             # Package setup configuration
├── src/
│   └── firecrawl/
│       ├── __init__.py   # Package initialization
│       └── scraper.py    # Core scraper implementation
├── examples/
│   └── example.py       # Usage examples
├── tests/
│   ├── __init__.py      # Test package initialization
│   └── test_scraper.py  # Scraper tests
└── pytest.ini           # Pytest configuration
```

### Directory Structure Overview

#### Core Package (`src/firecrawl/`)
- `__init__.py`: Package initialization, exports, and version information
- `scraper.py`: Core web scraper implementation with Playwright integration

#### Examples (`examples/`)
- `example.py`: Demonstrates basic and advanced usage of the scraper
- Additional examples can be added here to showcase different features

#### Tests (`tests/`)
- `test_scraper.py`: Comprehensive test suite for the scraper
- Uses pytest and pytest-asyncio for testing
- Includes mocks for browser interactions

#### Configuration Files
- `.env`: Local environment variables (not in version control)
- `.env.example`: Template for required environment variables
- `pytest.ini`: Pytest configuration settings
- `setup.py`: Package installation and dependency configuration
- `MANIFEST.in`: Specifies additional files to include in package distribution

#### Documentation
- `README.md`: Main project documentation (you are here)
- Code comments and docstrings within source files

### Development Setup

To set up the project for development:

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```
4. Copy `.env.example` to `.env` and configure as needed
5. Run tests to verify setup:
   ```bash
   pytest
   ```

## Development Tools

The project uses several tools to maintain code quality:

#### Code Formatting and Linting
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Code linting
- **mypy**: Static type checking

#### Testing
- **pytest**: Test framework
- **pytest-asyncio**: Async test support
- **pytest-mock**: Mocking support

#### Development Workflow
- **pre-commit**: Git hooks for code quality
- **Make**: Common development tasks

To set up the development environment with all tools:

```bash
# Install all development dependencies
make install

# Run tests
make test

# Format code
make format

# Run linters
make lint

# Clean up build artifacts
make clean
```

## Testing

The project includes a comprehensive test suite using pytest and pytest-asyncio. The tests cover all major functionality of the web scraper:

### Test Categories

1. **Setup/Teardown Tests**
   - Browser initialization
   - Resource cleanup

2. **Navigation Tests**
   - Successful page navigation
   - Failed page navigation

3. **Content Extraction Tests**
   - Title and content extraction
   - Link discovery

4. **Error Handling Tests**
   - Network errors
   - Invalid URLs

5. **Depth Control Tests**
   - Maximum depth enforcement
   - Link filtering

### Running Tests

To run the tests:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run a specific test
pytest tests/test_scraper.py -k test_name
```

### Test Architecture

The test suite uses several pytest fixtures to mock Playwright components:

- `mock_page`: Simulates a Playwright Page object
- `mock_browser`: Simulates a Playwright Browser object
- `mock_playwright`: Simulates the main Playwright instance

These fixtures allow us to test the scraper's functionality without actually launching a browser or making network requests.

### Adding New Tests

When adding new tests:

1. Use the existing fixtures where possible
2. Follow the naming convention: `test_*`
3. Use descriptive docstrings explaining:
   - What the test verifies
   - Input conditions
   - Expected outcomes
4. Group related tests together
5. Mock external dependencies
6. Handle async operations correctly

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:
- Setting up your development environment
- Our coding standards
- The pull request process
- Bug reporting guidelines

## License

This project is intended for educational purposes. Please ensure you have the right permissions before scraping any website.

---
Last Updated: December 20, 2024
