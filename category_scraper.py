import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
import os
from book_scraper import extract_book_data

BASE_URL = "http://books.toscrape.com/"
CATEGORY_URL = "http://books.toscrape.com/catalogue/category/books/science_22/index.html"

def get_soup(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.content, 'html.parser')
    else:
        print(f"Failed to fetch page: {url}")
        return None

def get_category_book_urls(category_url):
    book_urls = []
    while category_url:
        print(f"Scraping category: {category_url}")
        soup = get_soup(category_url)
        if not soup:
            break

        for article in soup.select('article.product_pod h3 a'):
            relative_url = article.get('href')
            # Ensure full, correct book URL includes /catalogue/
            book_url = urljoin(category_url, relative_url)
            if "catalogue/" not in book_url:
                book_url = urljoin(BASE_URL, "catalogue/" + relative_url)
            book_urls.append(book_url)

        # Pagination: find next page link
        next_button = soup.select_one('li.next > a')
        if next_button:
            next_url = next_button['href']
            category_url = urljoin(category_url, next_url)
        else:
            category_url = None

    return book_urls

def scrape_category(category_url, output_csv='category_books.csv'):
    # Always save in the "data" folder
    output_path = os.path.join("data", output_csv)

    book_urls = get_category_book_urls(category_url)
    print(f"Found {len(book_urls)} books")

    all_books_data = []
    for url in book_urls:
        print(f"Extracting: {url}")
        book_data = extract_book_data(url)
        if book_data:
            all_books_data.append(book_data)

    if all_books_data:
        keys = all_books_data[0].keys()
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_books_data)
        print(f"Data written to {output_path}")
    else:
        print("No data to write.")

if __name__ == '__main__':
    scrape_category(CATEGORY_URL)
