import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
import os

# Target book URL
BOOK_URL = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
BASE_URL = "http://books.toscrape.com/"

def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.content, 'html.parser')

def extract_book_data(url):
    soup = get_soup(url)

    title = soup.find('h1').text
    table = soup.find('table')
    rows = table.find_all('tr')
    data = {row.find('th').text: row.find('td').text for row in rows}
    
    description_tag = soup.find('div', id='product_description')
    description = description_tag.find_next_sibling('p').text if description_tag else 'No description'

    category = soup.select('ul.breadcrumb li a')[-1].text.strip()
    rating = soup.find('p', class_='star-rating')['class'][1]
    image_relative_url = soup.find('img')['src']
    image_url = urljoin(BASE_URL, image_relative_url)

    quantity_text = soup.find('p', class_='instock availability').text
    quantity = ''.join(filter(str.isdigit, quantity_text))

    return {
        "product_page_url": url,
        "universal_product_code (upc)": data.get("UPC", ""),
        "book_title": title,
        "price_including_tax": data.get("Price (incl. tax)", ""),
        "price_excluding_tax": data.get("Price (excl. tax)", ""),
        "quantity_available": quantity,
        "product_description": description,
        "category": category,
        "review_rating": rating,
        "image_url": image_url
    }

def write_to_csv(book_data, filename='book_data.csv'):
    # Always save in the "data" folder
    filepath = os.path.join("data", filename)
    fieldnames = list(book_data.keys())
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(book_data)
    print(f"Book data written to {filepath}")

if __name__ == "__main__":
    data = extract_book_data(BOOK_URL)
    write_to_csv(data)
