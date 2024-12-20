"""
A web scraper implementation using Playwright for browser automation.

This module provides a WebScraper class that can navigate through websites,
extract content, and follow links while respecting depth limits and handling
errors gracefully.

Example:
    ```python
    import asyncio
    from scraper import WebScraper

    async def main():
        scraper = WebScraper("https://example.com", max_depth=2)
        results = await scraper.run()
        print(results)

    asyncio.run(main())
    ```
"""

import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from playwright.async_api import (
    Browser,
    Page,
    Playwright,
    async_playwright,
)


@dataclass
class BrowserState:
    """Holds browser-related state that can't be serialized.

    This class maintains references to Playwright browser objects that need to be
    managed throughout the scraping session.

    Attributes:
        playwright: The Playwright instance
        browser: The browser instance (e.g., Chromium)
        page: The current browser page/tab
    """

    playwright: Optional[Playwright] = None
    browser: Optional[Browser] = None
    page: Optional[Page] = None


class WebScraper:
    """A web scraper that uses Playwright for browser automation.

    This class implements a web scraper that can navigate through websites,
    extract content, and follow links up to a specified depth. It handles
    browser automation using Playwright and manages resources efficiently.

    Attributes:
        start_url: The URL to start scraping from
        max_depth: Maximum depth of links to follow
        browser_state: State object holding browser-related resources
        visited_urls: Set of URLs that have been processed
        urls_to_visit: List of URLs to process
        extracted_data: Dictionary storing scraped data for each URL
        current_depth: Current depth in the link hierarchy
    """

    def __init__(self, start_url: str, max_depth: int = 2) -> None:
        """Initialize the web scraper.

        Args:
            start_url: The URL to start scraping from
            max_depth: Maximum depth to crawl (default: 2)
        """
        self.start_url = start_url
        self.max_depth = max_depth
        self.browser_state = BrowserState()
        self.visited_urls: Set[str] = set()
        self.urls_to_visit: List[str] = [start_url]
        self.extracted_data: Dict[str, Dict[str, str | List[str]]] = {}
        self.current_depth = 0

    async def _setup_browser(self) -> None:
        """Set up the browser instance.

        Initializes Playwright, launches a browser, and creates a new page.
        This should be called before starting the scraping process.
        """
        self.browser_state.playwright = await async_playwright().start()
        browser_config = {"headless": True}  # Configure browser options
        chromium = self.browser_state.playwright.chromium
        self.browser_state.browser = await chromium.launch(**browser_config)
        self.browser_state.page = await self.browser_state.browser.new_page()

    async def _cleanup(self) -> None:
        """Clean up browser resources.

        Closes the page, browser, and stops Playwright.
        This should be called after scraping is complete.
        """
        if self.browser_state.page:
            await self.browser_state.page.close()
        if self.browser_state.browser:
            await self.browser_state.browser.close()
        if self.browser_state.playwright:
            await self.browser_state.playwright.stop()

    async def _extract_links(self, depth: int) -> List[str]:
        """Extract links from the current page.

        Args:
            depth: Current depth in the crawl

        Returns:
            List[str]: List of extracted links
        """
        if depth >= self.max_depth - 1:
            return []

        links = []
        try:
            elements = await self.browser_state.page.query_selector_all("a[href]")
            for element in elements:
                try:
                    href = await element.get_attribute("href")
                    if href and href.startswith("http"):
                        links.append(href)
                except Exception as e:
                    print(f"Error extracting link: {str(e)}")
        except Exception as e:
            print(f"Error during link extraction: {str(e)}")

        return links

    async def _navigate_and_extract(self, url: str) -> bool:
        """Navigate to a URL and extract its content.

        This method handles both navigation to the URL and content extraction.
        It includes error handling for navigation failures and content extraction issues.

        Args:
            url: The URL to navigate to and extract content from

        Returns:
            bool: True if the page was successfully processed, False otherwise

        Note:
            The extracted data is stored in self.extracted_data and includes:
            - title: Page title
            - content: Page HTML content
            - links: List of links found on the page
            - error: Error message (if any error occurred)
        """
        if url in self.visited_urls:
            return False

        try:
            # Configure navigation options
            nav_options = {"wait_until": "domcontentloaded", "timeout": 10000}
            page = self.browser_state.page
            response = await page.goto(url, **nav_options)

            if not response or not response.ok:
                status = response.status if response else "No response"
                print(f"Failed to load {url}: {status}")
                return False

            # Extract content
            title = await page.title()
            content = await page.content()
            links = await self._extract_links(self.current_depth)

            # Store the data
            self.extracted_data[url] = {
                "title": title,
                "content": content,
                "links": links,
            }

            # Add new links to visit
            if links:
                new_links = [
                    link
                    for link in links
                    if link not in self.visited_urls and link not in self.urls_to_visit
                ]
                # Limit the number of new links to avoid recursion issues
                self.urls_to_visit.extend(new_links[:5])

            self.visited_urls.add(url)
            return True

        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
            self.extracted_data[url] = {
                "title": "",
                "content": "",
                "links": [],
                "error": str(e),
            }
            return False

    async def run(self) -> Dict[str, Dict[str, str | List[str]]]:
        """Run the web scraper.

        This method orchestrates the entire scraping process:
        1. Sets up the browser
        2. Processes URLs up to the specified depth
        3. Cleans up resources
        4. Returns the extracted data

        Returns:
            Dict[str, Dict[str, Any]]: A dictionary mapping URLs to their extracted data.
            Each URL's data includes:
            - title: Page title
            - content: Page HTML content
            - links: List of links found on the page
            - error: Error message (if any error occurred)

        Raises:
            Exception: If an error occurs during the scraping process
        """
        try:
            await self._setup_browser()

            while self.urls_to_visit and self.current_depth < self.max_depth:
                current_batch = self.urls_to_visit.copy()
                self.urls_to_visit = []

                for url in current_batch:
                    success = await self._navigate_and_extract(url)
                    if success:
                        print(f"Successfully processed {url}")

                self.current_depth += 1

        except Exception as e:
            print(f"Error during workflow execution: {str(e)}")

        finally:
            await self._cleanup()

        return self.extracted_data


async def main():
    # Example usage
    scraper = WebScraper("https://example.com", max_depth=2)
    results = await scraper.run()
    print("Scraped data:", results)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
