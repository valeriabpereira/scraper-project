# scraper-project

# Objective
Build a Python web scraper that extracts book metadata from https://books.toscrape.com/ and
saves the results in JSON Lines format with proper logging and a clear output structure.

# Instructions

1. Edit the file on data/input/categories_to_scrape.csv with a list of the categories provided on the left side in https://books.toscrape.com/.
2. Create a virtual environment using on CLI "python -m venv venv"
3. Activate your virtual environment using "venv\Scripts\activate"
4. Install requirements using "pip install -r requirements.txt"
5. Run the script using "python scraper.py"

# Cloud Deployment

The Cloud Deployment should be done by using Azure Functions and also Azure Blob Storage. Once the categories_to_scrape.csv is changed and uploaded into the blob storage, it will trigger a function and start scraper. Instructions detailed on "Cloud-Deployment.docx".

# Improvements

There are few steps that can be improved on this project:

1. Create a "utils.py" file and a class scrapeBooks with all get_category_links, read_categories_from_csv and get_book_links_from_category functions inside the class to make the notebook cleaner and easier to maintain;
2. Instead of hard coding the website url, fields and classes/tags, create a JSON file with those parameters that should be read by scraper.py in case those parameters changes over time to facilitate maintenance;
