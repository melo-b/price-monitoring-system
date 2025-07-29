import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin

BASE_URL = "http://books.toscrape.com/"
CATEGORY_URL = "http://books.toscrape.com/catalogue/category/books/science_22/index.html"

def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.content, 'html.parser')

def get_book_urls(category_url):
    book_urls = []
    while category_url:
        soup = get_soup(category_url)
        articles = soup.select('article.product_pod h3 a')
        for a in articles:
            relative_url = a['href']
            book_url = urljoin(category_url, relative_url)
            book_url = book_url.replace('../../../', 'http://books.toscrape.com/catalogue/')
            book_urls.append(book_url)

        # Pagination check
        next_page = soup.select_one('li.next a')
        if next_page:
            next_href = next_page['href']
            category_url = urljoin(category_url, next_href)
        else:
            break
    return book_urls

def scrape_book_data(book_url):
    soup = get_soup(book_url)

    upc = soup.find('th', text='UPC').find_next_sibling('td').text
    title = soup.find('h1').text
    price_incl_tax = soup.find('th', text='Price (incl. tax)').find_next_sibling('td').text
    price_excl_tax = soup.find('th', text='Price (excl. tax)').find_next_sibling('td').text
    availability = soup.find('th', text='Availability').find_next_sibling('td').text
    quantity_available = ''.join(filter(str.isdigit, availability))
    description_tag = soup.find('meta', attrs={"name": "description"})
    description = description_tag['content'].strip() if description_tag else ''
    category = soup.select_one('ul.breadcrumb li:nth-of-type(3) a').text
    rating_class = soup.select_one('p.star-rating')['class'][1]
    image_relative_url = soup.select_one('div.item.active img')['src']
    image_url = f"http://books.toscrape.com/{image_relative_url.replace('../', '')}"

    return {
        "product_page_url": book_url,
        "universal_product_code": upc,
        "book_title": title,
        "price_including_tax": price_incl_tax,
        "price_excluding_tax": price_excl_tax,
        "quantity_available": quantity_available,
        "product_description": description,
        "category": category,
        "review_rating": rating_class,
        "image_url": image_url
    }

def main():
    print("Getting book URLs...")
    book_urls = get_book_urls(CATEGORY_URL)
    print(f"Found {len(book_urls)} books")

    all_data = []

    for url in book_urls:
        print(f"Scraping {url}")
        try:
            data = scrape_book_data(url)
            all_data.append(data)
        except Exception as e:
            print(f"Failed to scrape {url}: {e}")

    output_file = "data/category_books.csv"
    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=all_data[0].keys())
        writer.writeheader()
        writer.writerows(all_data)

    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    main()