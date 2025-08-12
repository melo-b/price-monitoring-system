# Price Monitoring System

This project is a multi-phase Python scraping system that collects book data from [Books to Scrape](http://books.toscrape.com) and outputs structured CSV data.  
By Phase 4, it can scrape **all categories**, download images, and store them alongside the CSV data.

---

## Features

**Phase 1: Single Book Scraper**
- Extracts:
  - Product page URL
  - Universal Product Code (UPC)
  - Book title
  - Prices (with and without tax)
  - Stock availability
  - Product description
  - Category
  - Review rating
  - Image URL

**Phase 2: Category Scraper**
- Scrapes all product URLs in a given category.
- Uses Phase 1 logic to extract book details.

**Phase 3: All Categories Scraper**
- Scrapes every category on the site.
- Saves one CSV file per category into `data/`.

**Phase 4: Image Download and Conversion**
- Downloads each book's product image.
- Converts images to `.jpg` format using Pillow (if installed).
- Stores images in `data/images/`.
- Saves CSV files with an extra `image_filename` column in `data/data_and_image/`.

---

## Setup

1. **Clone this repository:**
   ```bash
   git clone <your_repo_url>
   cd <your_repo_folder>

2. Create and activate a virtual environment

3. Install dependencies


## Usage

Phase 1 - Single book scraper - RUN book_scraper.py
Phase 2 - Category scraper - RUN category_scraper.py
Phase 3 and Phase 4 - All categories scraper w/ image download - RUN all_categories_scraper.py


## Output & Structure

The extracted data will be saved to `data/book_data.csv`.

data/
│
├── images/
│   ├── <book_title>_<UPC>.jpg
│   └── ...
│
└── data_and_image/
    ├── <category_name>.csv
    └── ...


## Notes

- Pillow is optional. If installed, all images will be converted to .jpg. If not installed, raw images are saved in their original format
- Built with `requests` and `BeautifulSoup`.
- The script does not track prices over time.
- CSV output files and images are not committed to the repository.
- Make sure not to commit your virtual environment.
- The script currently works only for the "Books to Scraper" site structure
