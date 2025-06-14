import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
from datetime import datetime
import argparse
import os
import json

# Create log directory and file
log_dir = "./"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "scraper.log")


# Configure logging
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Start Script message on log
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
logging.info(f"Script started at {now}")

# CLI flag to limit the number of books scraped
parser = argparse.ArgumentParser(description="Scrape books.toscrape.com by category")
parser.add_argument("--max-books", type=int, default=None, help="Maximum number of books to scrape per category")

# Safe parsing
args, _ = parser.parse_known_args()

# Setup headless browser for no browser window
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

base_url = "https://books.toscrape.com/"
driver.get(base_url)

book_data = []

# Load category mapping from the site (name → URL) on class side_categories
def get_category_links():
    category_map = {}
    WebDriverWait(driver, 25).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.side_categories ul li ul li a"))
    )
    categories = driver.find_elements(By.CSS_SELECTOR, "div.side_categories ul li ul li a")

    # Get link from the href
    for cat in categories:
        name = cat.text.strip()
        href = cat.get_attribute("href")
        category_map[name] = href
    return category_map

# Read desired categories from CSV
def read_categories_from_csv(csv_file):
    with open(csv_file, newline='') as file:
        reader = csv.DictReader(file)
        return [row['category_name'].strip() for row in reader]

# Scrape all books from a category page (including pagination)

def get_book_links_from_category(category_url):
    links = []
    try:
        driver.get(category_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "section"))
        )
    except TimeoutException:
        logging.warning(f"Timeout loading category page: {category_url} - Retrying...")
        return links

    while True:
        # Get link from article product_pod class
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.product_pod h3 a"))
            )
            books = driver.find_elements(By.CSS_SELECTOR, "article.product_pod h3 a")

            # Get link from the href
            links += [book.get_attribute("href") for book in books]

            # Try to find the "Next" button and go to the next page
            try:
                next_btn = driver.find_element(By.CLASS_NAME, "next")
                next_link = next_btn.find_element(By.TAG_NAME, "a").get_attribute("href")
                next_url = driver.current_url.rsplit('/', 1)[0] + '/' + next_link
                driver.get(next_url)
            except NoSuchElementException:
                break  # No more pages

        except TimeoutException:
            logging.warning(f"Timeout while loading books in: {category_url} - Retrying...")
            break

    return links

# Extract book data from book page
def extract_book_info(url):
    driver.get(url)
    WebDriverWait(driver, 25).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.product_main h1"))
    )

    # Find the elements
    title = driver.find_element(By.CSS_SELECTOR, "div.product_main h1").text
    rating_class = driver.find_element(By.CLASS_NAME, "star-rating").get_attribute("class").split()[-1]
    category = driver.find_elements(By.CSS_SELECTOR, "ul.breadcrumb li a")[-1].text

    table = driver.find_element(By.CSS_SELECTOR, "table.table.table-striped")
    rows = table.find_elements(By.TAG_NAME, "tr")
    table_data = {
        row.find_element(By.TAG_NAME, "th").text.strip():
        row.find_element(By.TAG_NAME, "td").text.strip()
        for row in rows
    }
    
    # Return a dictionary that will be transformed into a JSON file with all variables needed
    return {
        "title": title,
        "rating": rating_class,
        "category": category,
        "upc": table_data.get("UPC"),
        "product_type": table_data.get("Product Type"),
        "price_excl_tax": table_data.get("Price (excl. tax)"),
        "price_incl_tax": table_data.get("Price (incl. tax)"),
        "tax": table_data.get("Tax"),
        "availability": table_data.get("Availability"),
        "num_reviews": table_data.get("Number of reviews")
    }

# Execute everything
input_categories = read_categories_from_csv("data/input/categories_to_scrape.csv")
site_categories = get_category_links()

# Match input names with website categories
for cat_name in input_categories:

    # Validate if inputed category name exists in website and skip to the next loop if doesn't exist
    if cat_name not in site_categories:
        logging.error(f" Invalid category: {cat_name} — skipping.")
        continue

    cat_url = site_categories[cat_name]
    logging.info(f"  Scraping category: {cat_name}")
    book_links = get_book_links_from_category(cat_url)
    logging.info(f"  Found {len(book_links)} books in {cat_name}")

    for i, link in enumerate(book_links):

        # If --max-books are determined, avoid reaching the limit
        if args.max_books is not None and i >= args.max_books:
            logging.info(f"Reached maximum number of books: ({args.max_books}) for category '{cat_name}'")
            break
        try:
            data = extract_book_info(link)
            book_data.append(data)
            logging.info(f"    {i+1}. {data['title']}")
        except Exception as e:
            logging.error(f"Failed to scrape book at {link}: {e}")

driver.quit()

# Save to JSONL format in ./data/{timestamp}/books_to_scrape.jsonl in row format
timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
output_dir = f"./data/{timestamp}"
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, "books_to_scrape.jsonl")

with open(output_path, "w", encoding="utf-8") as f:
    for book in book_data:
        f.write(json.dumps(book, ensure_ascii=False) + "\n")


logging.info(f"Data saved to: {output_path}")

# Finish Script message on log
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
logging.info(f"Script finished successfully at {now}")