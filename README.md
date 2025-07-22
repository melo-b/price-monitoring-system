# Price Monitoring System

This is a Python script that scrapes book data from a single product page on [Books to Scrape](http://books.toscrape.com) and exports it to a CSV file.

## Features

- Extracts:
  - product page URL
  - universal product code (UPC)
  - book title
  - prices (with and without tax)
  - stock availability
  - product description
  - category
  - review rating
  - image URL

## Setup

1. Create and activate a virtual environment:
2. Clone this repository.
3. Ensure you have Python 3.8+ installed.
4. Install dependencies:
5. Run the scraper:


## Output

The extracted data will be saved to `data/book_data.csv`.

## Notes

- Only works on a single book product page for now.
- Built with `requests` and `BeautifulSoup`.
- The script does not track prices over time.
- CSV output files are not committed to the repository.
- Make sure not to commit your virtual environment.
