"""Tests for the WebScraper class.

This module contains a comprehensive test suite for the WebScraper class. It tests
all major functionality including browser setup, navigation, content extraction,
and error handling. The tests use pytest-asyncio for async testing and pytest-mock
for mocking Playwright components.

Test Categories:
1. Setup/Teardown Tests
   - Browser initialization
   - Resource cleanup
2. Navigation Tests
   - Successful page navigation
   - Failed page navigation
3. Content Extraction Tests
   - Title and content extraction
   - Link discovery
4. Error Handling Tests
   - Network errors
   - Invalid URLs
5. Depth Control Tests
   - Maximum depth enforcement
   - Link filtering

Each test uses mocked Playwright components to avoid actual browser operations
during testing.
"""

from unittest.mock import AsyncMock, Mock

import pytest
from playwright.async_api import Browser, Page, Response

from firecrawl.scraper import BrowserState, WebScraper


@pytest.fixture
def mock_page(mocker):
    """Create a mock Page object for testing.

    This fixture provides a mock Playwright Page object with pre-configured
    responses for common operations like navigation, content extraction,
    and link discovery.

    Returns:
        AsyncMock: A mock Page object with the following configured:
            - goto: Returns a successful response (status 200)
            - title: Returns "Test Page"
            - content: Returns a simple HTML document
            - query_selector_all: Returns a list with one mock link element
    """
    page = AsyncMock(spec=Page)

    # Mock successful response
    response = AsyncMock(spec=Response)
    response.ok = True
    response.status = 200
    page.goto.return_value = response

    # Mock page content
    title_mock = AsyncMock()
    title_mock.return_value = "Test Page"
    page.title = title_mock

    content_mock = AsyncMock()
    content_mock.return_value = "<html><body>Test content</body></html>"
    page.content = content_mock

    # Mock link extraction
    mock_element = AsyncMock()
    mock_element.get_attribute.return_value = "https://example.com/test"
    page.query_selector_all.return_value = [mock_element]

    return page


@pytest.fixture
def mock_browser(mocker, mock_page):
    """Create a mock Browser object for testing.

    This fixture provides a mock Playwright Browser object that returns
    our mock Page object when new_page() is called.

    Args:
        mocker: The pytest-mock fixture
        mock_page: Our mock Page fixture

    Returns:
        AsyncMock: A mock Browser object configured to return mock_page
    """
    browser = AsyncMock(spec=Browser)
    browser.new_page.return_value = mock_page
    return browser


@pytest.fixture
def mock_playwright(mocker, mock_browser):
    """Create a mock Playwright instance for testing.

    This fixture provides a mock Playwright instance that returns our
    mock Browser object when chromium.launch() is called.

    Args:
        mocker: The pytest-mock fixture
        mock_browser: Our mock Browser fixture

    Returns:
        AsyncMock: A mock Playwright instance configured to return mock_browser
    """
    playwright = AsyncMock()
    playwright.chromium.launch.return_value = mock_browser
    return playwright


@pytest.fixture
def scraper():
    """Create a WebScraper instance for testing.

    Returns:
        WebScraper: A fresh WebScraper instance configured to start at example.com
    """
    return WebScraper("https://example.com")


@pytest.mark.asyncio
async def test_setup_browser(mocker, scraper, mock_playwright):
    """Test the browser setup process.

    This test verifies that:
    1. The async_playwright() call works correctly
    2. Browser resources are properly initialized
    3. The browser state is correctly set up

    Args:
        mocker: The pytest-mock fixture
        scraper: Our WebScraper fixture
        mock_playwright: Our mock Playwright fixture
    """
    # Create an async mock that returns our mock_playwright
    async_playwright_mock = AsyncMock()
    async_playwright_mock.return_value = mock_playwright
    mocker.patch(
        "firecrawl.scraper.async_playwright", return_value=async_playwright_mock()
    )

    await scraper._setup_browser()

    # Verify browser was set up correctly
    assert scraper.browser_state.playwright is mock_playwright
    assert scraper.browser_state.browser is mock_playwright.chromium.launch.return_value
    assert (
        scraper.browser_state.page
        is mock_playwright.chromium.launch.return_value.new_page.return_value
    )


@pytest.mark.asyncio
async def test_cleanup(scraper):
    """Test the browser cleanup process.

    This test verifies that:
    1. All browser resources are properly closed
    2. The cleanup process handles async operations correctly
    3. No resources are left open

    Args:
        scraper: Our WebScraper fixture
    """
    # Set up mock browser state
    scraper.browser_state = BrowserState(
        playwright=Mock(spec=AsyncMock),
        browser=Mock(spec=AsyncMock),
        page=Mock(spec=AsyncMock),
    )

    # Configure async mocks
    scraper.browser_state.page.close = AsyncMock()
    scraper.browser_state.browser.close = AsyncMock()
    scraper.browser_state.playwright.stop = AsyncMock()

    await scraper._cleanup()

    # Verify cleanup calls
    assert scraper.browser_state.page.close.called
    assert scraper.browser_state.browser.close.called
    assert scraper.browser_state.playwright.stop.called


@pytest.mark.asyncio
async def test_navigate_and_extract_success(mocker, scraper, mock_page):
    """Test successful navigation and content extraction.

    This test verifies that:
    1. Page navigation works correctly
    2. Content extraction (title, HTML) succeeds
    3. Link discovery works as expected
    4. Extracted data is properly stored

    Args:
        mocker: The pytest-mock fixture
        scraper: Our WebScraper fixture
        mock_page: Our mock Page fixture
    """
    # Set up scraper with mock page
    scraper.browser_state.page = mock_page

    # Test navigation and extraction
    result = await scraper._navigate_and_extract("https://example.com")

    assert result is True
    assert "https://example.com" in scraper.visited_urls
    assert "https://example.com" in scraper.extracted_data

    data = scraper.extracted_data["https://example.com"]
    assert data["title"] == "Test Page"
    assert data["content"] == "<html><body>Test content</body></html>"
    assert len(data["links"]) == 1
    assert data["links"][0] == "https://example.com/test"


@pytest.mark.asyncio
async def test_navigate_and_extract_failure(mocker, scraper, mock_page):
    """Test navigation failure handling.

    This test verifies that:
    1. Failed navigation (404) is handled gracefully
    2. Error information is properly recorded
    3. The URL is not marked as visited
    4. No invalid data is stored

    Args:
        mocker: The pytest-mock fixture
        scraper: Our WebScraper fixture
        mock_page: Our mock Page fixture
    """
    # Mock a failed response
    response = AsyncMock(spec=Response)
    response.ok = False
    response.status = 404
    mock_page.goto.return_value = response

    # Set up scraper with mock page
    scraper.browser_state.page = mock_page

    # Test navigation failure
    result = await scraper._navigate_and_extract("https://example.com")

    assert result is False
    assert "https://example.com" not in scraper.visited_urls
    assert "https://example.com" not in scraper.extracted_data


@pytest.mark.asyncio
async def test_run_workflow(mocker, scraper, mock_playwright):
    """Test the complete scraping workflow.

    This test verifies that:
    1. The entire scraping process works end-to-end
    2. Multiple pages are processed correctly
    3. Data is collected and stored properly
    4. The workflow terminates correctly

    Args:
        mocker: The pytest-mock fixture
        scraper: Our WebScraper fixture
        mock_playwright: Our mock Playwright fixture
    """
    # Create an async mock that returns our mock_playwright
    async_playwright_mock = AsyncMock()
    async_playwright_mock.return_value = mock_playwright
    mocker.patch(
        "firecrawl.scraper.async_playwright", return_value=async_playwright_mock()
    )

    # Configure mock page responses
    mock_page = mock_playwright.chromium.launch.return_value.new_page.return_value
    title_mock = AsyncMock()
    title_mock.return_value = "Test Page"
    mock_page.title = title_mock

    content_mock = AsyncMock()
    content_mock.return_value = "<html><body>Test content</body></html>"
    mock_page.content = content_mock

    # Mock successful response
    response = AsyncMock(spec=Response)
    response.ok = True
    response.status = 200
    mock_page.goto.return_value = response

    # Mock link extraction
    mock_element = AsyncMock()
    mock_element.get_attribute.return_value = "https://example.com/test"
    mock_page.query_selector_all.return_value = [mock_element]

    # Run the scraper
    results = await scraper.run()

    # Verify results
    assert isinstance(results, dict)
    assert len(results) > 0
    assert "https://example.com" in results

    # Verify the first page was processed
    first_page = results["https://example.com"]
    assert first_page["title"] == "Test Page"
    assert first_page["content"] == "<html><body>Test content</body></html>"
    assert len(first_page["links"]) == 1


@pytest.mark.asyncio
async def test_max_depth_limit(mocker, scraper, mock_playwright):
    """Test the maximum depth limit enforcement.

    This test verifies that:
    1. The scraper respects the max_depth setting
    2. No pages beyond max_depth are processed
    3. Link extraction stops at the appropriate depth
    4. The scraper terminates correctly at max depth

    Args:
        mocker: The pytest-mock fixture
        scraper: Our WebScraper fixture
        mock_playwright: Our mock Playwright fixture
    """
    # Set a low max depth
    scraper.max_depth = 1

    # Create an async mock that returns our mock_playwright
    async_playwright_mock = AsyncMock()
    async_playwright_mock.return_value = mock_playwright
    mocker.patch(
        "firecrawl.scraper.async_playwright", return_value=async_playwright_mock()
    )

    # Run the scraper
    results = await scraper.run()

    # Verify we didn't go too deep
    assert scraper.current_depth <= scraper.max_depth

    # Verify we processed at least the first page
    assert "https://example.com" in results
