# all_categories_scraper.py
import os
import re
import requests
import csv
from io import BytesIO
from urllib.parse import urljoin
from book_scraper import extract_book_data      # reuse your Phase 1 function
from category_scraper import get_category_book_urls   # reuse your Phase 2 function

BASE_URL = "http://books.toscrape.com/"
DATA_DIR = "data"
IMAGES_DIR = os.path.join(DATA_DIR, "images")
CSV_DIR = os.path.join(DATA_DIR, "data_and_image")

# ensure directories exist
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(CSV_DIR, exist_ok=True)

# Optional: Pillow will be used to convert images to JPEG.
try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False


def sanitize_for_filename(s: str, max_len=100) -> str:
    """Sanitize string for filesystem use. Limit length."""
    if s is None:
        s = ""
    # normalize whitespace
    s = re.sub(r'\s+', '_', s.strip())
    # remove characters that are not letters, numbers, dash, underscore, or dot
    s = re.sub(r'[^\w\-.]', '', s)
    return s[:max_len]


def find_upc_in_data(book_data: dict) -> str:
    """Return UPC value from book_data dict (handles different key names)."""
    for k, v in book_data.items():
        if 'upc' in k.lower():
            return v.strip()
    # fallback: try known key names
    for possible in ("universal_product_code (upc)", "universal_product_code", "upc"):
        if possible in book_data:
            return book_data[possible].strip()
    return ""


def find_image_url_in_data(book_data: dict) -> str:
    """Find image URL in the scraped book data (handles different key names)."""
    for k, v in book_data.items():
        if 'image' in k.lower() and v:
            return v.strip()
    # fallback to None
    return None


def download_and_save_image(image_url: str, title: str, upc: str) -> str:
    """
    Downloads image_url and saves to DATA_DIR/images as
    <sanitized_title>_<sanitized_upc>.jpg
    Returns the image filename on success, or empty string on failure.
    """
    if not image_url:
        return ""

    # Normalize the image URL in case it's relative
    image_url = urljoin(BASE_URL, image_url)

    sanitized_title = sanitize_for_filename(title) or "book"
    sanitized_upc = sanitize_for_filename(upc) or "no_upc"
    filename = f"{sanitized_title}_{sanitized_upc}.jpg"
    filepath = os.path.join(IMAGES_DIR, filename)

    # If already exists, skip download
    if os.path.exists(filepath):
        return filename

    try:
        resp = requests.get(image_url, timeout=20)
        resp.raise_for_status()
        content = resp.content

        if PIL_AVAILABLE:
            # convert to RGB and save as JPEG to normalize format
            try:
                img = Image.open(BytesIO(content)).convert("RGB")
                img.save(filepath, format="JPEG", quality=85)
                return filename
            except Exception as e:
                # fallback to saving raw bytes if Pillow fails for some reason
                print(f"Warning: Pillow failed to process image {image_url}: {e}. Falling back to raw save.")
        # If Pillow not available or conversion failed, save raw bytes
        with open(filepath, "wb") as f:
            f.write(content)
        return filename

    except Exception as e:
        print(f"Failed to download/save image from {image_url}: {e}")
        # ensure no half-written file remains
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass
        return ""


def get_all_category_urls():
    """Scrape the homepage to get (category_name, category_url) list."""
    index_url = urljoin(BASE_URL, "index.html")
    resp = requests.get(index_url)
    resp.raise_for_status()
    soup = None
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.content, "html.parser")
    except Exception as e:
        raise RuntimeError("BeautifulSoup required to parse categories") from e

    categories = []
    category_nodes = soup.select('div.side_categories ul li ul li a')
    for node in category_nodes:
        name = node.text.strip()
        rel = node.get("href")
        full = urljoin(BASE_URL, rel)
        categories.append((name, full))
    return categories


def scrape_all_categories():
    """Main orchestrator: scrape each category, download images, write CSV with image_filename col."""
    categories = get_all_category_urls()
    print(f"Found {len(categories)} categories.")

    for category_name, category_url in categories:
        print(f"\nScraping category: {category_name} -> {category_url}")
        # Reuse your Phase 2 function to enumerate all book product URLs for the category
        try:
            book_urls = get_category_book_urls(category_url)
        except Exception as e:
            print(f"Failed to get book URLs for {category_name}: {e}")
            continue

        print(f"Found {len(book_urls)} books in '{category_name}'")
        all_books = []

        for book_url in book_urls:
            print(f"  Extracting: {book_url}")
            try:
                book_data = extract_book_data(book_url)
            except Exception as e:
                print(f"    Failed to extract {book_url}: {e}")
                continue

            # derive UPC & image_url from book_data (handle different key names)
            upc = find_upc_in_data(book_data)
            image_url = find_image_url_in_data(book_data)

            # for title, try multiple key names ("book_title" or "title")
            title = book_data.get("book_title") or book_data.get("title") or ""

            # download image and get filename
            image_filename = download_and_save_image(image_url, title, upc)
            # add image filename to book data (CSV column)
            book_data['image_filename'] = image_filename

            all_books.append(book_data)

        # if no books, skip CSV write
        if not all_books:
            print(f"No book data collected for category {category_name}, skipping CSV.")
            continue

        # prepare CSV file path in data/data_and_image
        safe_name = sanitize_for_filename(category_name)
        csv_path = os.path.join(CSV_DIR, f"{safe_name}.csv")

        # determine headers: union of keys across all dicts (to be safe)
        headers = []
        for d in all_books:
            for k in d.keys():
                if k not in headers:
                    headers.append(k)
        # ensure image_filename included (end)
        if 'image_filename' not in headers:
            headers.append('image_filename')

        # write CSV
        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(all_books)
            print(f"Saved CSV for '{category_name}' -> {csv_path} ({len(all_books)} rows).")
        except Exception as e:
            print(f"Failed to write CSV for '{category_name}': {e}")


if __name__ == "__main__":
    scrape_all_categories()
