# Import dependencies: requests, csv, BeautifulSoup
import requests
import csv
from bs4 import BeautifulSoup


# URL of the webpage to scrape
url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"



def scrape_book_data(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    soup = BeautifulSoup(response.content, 'html.parser')
    # Extracting data from the soup object
    
    # Extracting UPC and prices
    table = soup.find('table', class_='table table-striped')
    table_data = {row.th.text: row.td.text for row in table.find_all('tr')}
    upc = table_data.get('UPC')
    price_incl_tax = table_data.get('Price (incl. tax)')
    price_excl_tax = table_data.get('Price (excl. tax)')
    quantity_available = table_data.get('Availability')
    
    # Book title
    book_title = soup.find('div', class_='product_main').h1.text

    # Book description
    desc = soup.find('div', id='product_description')
    product_description = desc.find_next_sibling('p').text if desc else ''

    # Category (breadcrumb nav)
    category = soup.find('ul', class_='breadcrumb').find_all('li')[2].a.text.strip()
    
    # Review rating
    rating_elem = soup.find('p', class_='star-rating')
    rating = rating_elem.get('class', [])
    review_rating = next((r for r in rating if r != 'star-rating'), '')

    # Image URL
    img_relative = soup.find('img')['src']
    image_url = 'https://books.toscrape.com/' + img_relative.lstrip('../')
    
    book_data = {
        "product_page_url": url,
        "universal_product_code (upc)": upc,
        "book_title": book_title,
        "price_including_tax": price_incl_tax,
        "price_excluding_tax": price_excl_tax,
        "quantity_available": quantity_available,
        "product_description": product_description,
        "category": category,
        "review_rating": review_rating,
        "image_url": image_url,
    }
    return book_data

def write_to_csv(data, filename='book_data.csv'):
    fieldnames = [
        "product_page_url", "universal_product_code (upc)", "book_title",
        "price_including_tax", "price_excluding_tax", "quantity_available",
        "product_description", "category", "review_rating", "image_url"
    ]
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(data)

if __name__ == "__main__":
    url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"  # sample product
    data = scrape_book_data(url)
    write_to_csv(data)
    print("Book data scraped and saved to book_data.csv")
    
    

