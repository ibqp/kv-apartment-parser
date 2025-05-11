# 🏢 KV Apartment Parser

A Python-based web scraper that extracts, structures and saves real estate listings from the Estonian real estate website KV.ee. The scraper navigates through apartment listing pages, extracts data from each listing, and stores the information in both JSON files and a PostgreSQL database for further analysis.

⚠️ **NB!** This scraper was developed for personal research purposes to monitor trends in the Estonian real estate market. Please use it responsibly and respect KV.ee's website policies.

---

## ✨ Features

- **Automated Data Collection**: Crawls through KV.ee apartment listings and extracts detailed information
- **Comprehensive Data Extraction**: Collects address, price, floor, area, images, and numerous other property details
- **Duplicate Prevention**: Skips apartments already present in the database
- **Structured Data Storage**: Saves data in both JSON format and PostgreSQL database
- **Per-Page Saving**: Saves data after processing each page (~50 listings) rather than waiting until the end
- **Interruption Protection**: Preserves collected data if scraping is interrupted (preventing data loss)
- **Proper Request Handling**: Implements random delays and retry mechanisms to respect the website's resources
- **Detailed Logging**: Maintains logs of the scraping process for monitoring and debugging

---

## ⚙️ How It Works

1. The scraper prompts you to enter a starting URL
2. For each page of search results, it:
   - Extracts URLs of individual apartment listings
   - Visits each listing to extract detailed property information
   - Parses and structures the data (address, price, rooms, area, etc.)
   - Stores data in both JSON files and a PostgreSQL database
3. It continues to the next page of results until all pages are processed

---

## 🚀 Setup

- **Prerequisites**
  - Python 3.11+
  - PostgreSQL@14
  - Environment variables (for database connection)
    - PG_LOC_DB_USER=<your_db_username>
    - PG_LOC_DB_PASS=<your_db_password>
    - PG_LOC_DB_NAME=<your_db_name>
    - PG_LOC_DB_HOST=<your_host> (localhost default)
    - PG_LOC_DB_PORT=<your_port> (5432 default)
- **Installation**
  - Clone the repository
  - Create a virtual environment
  - Activate the virtual environment
  - Install dependencies: `pip install -r requirements.txt`

---

### ▶️ Running the Scraper

Run the scraper using: `python main.py`

The program will prompt you to enter a starting URL (or use a default URL).

Data will be saved in the `data` directory as JSON files and in the configured PostgreSQL database (if the database is not configured, data will be saved only as JSON files).
