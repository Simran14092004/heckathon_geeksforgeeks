# web_scrapper/scrape_data.py
import requests
from bs4 import BeautifulSoup
import logging

def scrape_latest_data():
    url = "https://example.com/latest-prices"  # Replace with the actual URL
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for HTTP issues
        soup = BeautifulSoup(response.text, 'html.parser')

        print(f"Soup object: {soup}") # print the soup object.

        # Example scraping logic (customize based on the actual HTML structure)
        prices = []
        for price_tag in soup.select('.price-class'):  # Adjust the selector as needed
            prices.append(price_tag.text.strip())
        print(f"Scraped prices: {prices}") # print the prices that were scraped.

        # Return scraped data
        return {"prices": prices}

    except Exception as e:
        logging.error(f"Error in scraper: {e}")
        return {"error": "Failed to scrape data"}