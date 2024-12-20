import asyncio
from firecrawl.scraper import WebScraper

async def run_example():
    try:
        # Create a scraper instance with a starting URL and max depth
        start_url = "https://quotes.toscrape.com"  # A website that allows scraping
        max_depth = 2
        print(f"\nStarting web scraping from {start_url} with max depth {max_depth}...")
        
        scraper = WebScraper(start_url, max_depth)
        results = await scraper.run()
        
        # Print results
        print("\nScraping completed! Here are the results:")
        for url, data in results.items():
            print(f"\nURL: {url}")
            print(f"Title: {data.get('title', 'N/A')}")
            print(f"Content length: {len(data.get('content', ''))} characters")
            if 'error' in data:
                print(f"Error: {data['error']}")
            print(f"Found {len(data.get('links', []))} links")
            
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(run_example())
