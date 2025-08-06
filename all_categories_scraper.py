import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from book_scraper import extract_book_data
from category_scraper import get_category_book_urls

BASE_URL = "http://books.toscrape.com/"
INDEX_URL = BASE_URL + "index.html"

def get_soup(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.content, 'html.parser')
    else:
        print(f"Failed to fetch page: {url}")
        return None

def get_all_category_urls():
    soup = get_soup(INDEX_URL)
    category_urls = {}
    category_list = soup.select('div.side_categories ul li ul li a')
    
    for category in category_list:
        name = category.text.strip()
        relative_url = category.get('href')
        full_url = urljoin(BASE_URL, relative_url)
        category_urls[name] = full_url

    return category_urls

def sanitize_filename(name):
    return name.lower().replace(' ', '_').replace('/', '_')

def scrape_all_categories():
    category_urls = get_all_category_urls()
    print(f"Found {len(category_urls)} categories")

    for category_name, category_url in category_urls.items():
        print(f"\n--- Scraping Category: {category_name} ---")
        book_urls = get_category_book_urls(category_url)
        print(f"Found {len(book_urls)} books in {category_name}")

        books_data = []
        for book_url in book_urls:
            print(f"Extracting book: {book_url}")
            data = extract_book_data(book_url)
            if data:
                books_data.append(data)

        if books_data:
            filename = f"{sanitize_filename(category_name)}.csv"
            keys = books_data[0].keys()
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                import csv
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(books_data)
            print(f"✅ Data for '{category_name}' written to '{filename}'")
        else:
            print(f"No books found in category: {category_name}")

if __name__ == "__main__":
    scrape_all_categories()

