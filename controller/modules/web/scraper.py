import concurrent.futures
import cloudscraper
from bs4 import BeautifulSoup
from googlesearch import search
import json

# Function to scrape a single website using cloudscraper
def scrape_website(url):
    try:
        # Use cloudscraper to bypass security
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract title
        title = soup.title.string if soup.title else "No title found"
        
        # Extract meta keywords
        meta_keywords = soup.find("meta", attrs={"name": "keywords"})
        keywords = meta_keywords["content"] if meta_keywords else "No keywords found"
        
        # Extract paragraphs (limit to 5 paragraphs for brevity)
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")][:5]
        
        return {
            "parts": paragraphs,
            "inline_data": title,
            "text": keywords,
            "mime_type": "text/html",
            "data": url,
            "error": ""
        }
    except Exception as e:
        return {
            "parts": [],
            "inline_data": "No title found",
            "text": "",
            "mime_type": "text/html",
            "data": url,
            "error": str(e)
        }

# Function to search Google for URLs
def get_search_results(query, num_results=5):
    return [url for url in search(query, num_results=num_results)]

width = 15

# Main function to manage scraping process
import concurrent.futures

# Main function to manage scraping process
async def web_scrapper(query):
    # User input for query and settings
    search_query = query.strip()
    num_results = width
    num_threads = width
    
    print("\nSearching for websites... Please wait.")
    urls = get_search_results(search_query, num_results)
    print(f"Found {len(urls)} URLs to scrape.")
    
    print("\nScraping websites... Please wait.")
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(scrape_website, url) for url in urls]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    
    # Instead of saving to a file, return the results as a JSON-like Python object
    print(results)
    return results
