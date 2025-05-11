import time
import logging
from lxml import html
from config import xpaths
from utils.db import DatabaseManager
from utils import http, parser, storage
from typing import List, Dict, Any, Optional, Tuple


class KVSpider:
    def __init__(self, db_manager: DatabaseManager | None):
        self.session = http.create_session()
        self.db_manager = db_manager
        self.apartments: List[Dict[str, Any]] = []


    # Main function
    def run_scraper(self) -> None:
        # Get initial url
        current_page_url = http.get_initial_url()

        # While there are url to scrape - scraper will work
        current_page_nr = 1
        while current_page_url:
            next_page_url = self.process_page(current_page_url, current_page_nr)
            current_page_url = next_page_url
            current_page_nr += 1


    # Spider functions
    def process_page(self, url: str, page_number: int) -> Optional[str]:
        logging.info(f"Processing page {page_number}: {url}")

        # Send request to given url and parse response
        # Response contains URLs to detailed apartment pages
        html = self._fetch_and_parse(url, page_number)
        if html is None:
            logging.error(f"Failed to fetch apartments page: {url}")
            return None # at this moment the whole process will be terminated

        # Process apartments on current page
        processed_count, exists_in_db_count, failed_cnt = self.process_apartments(html, page_number)
        logging.info(f"Total processed: {processed_count} / skipped: {exists_in_db_count} / failed: {failed_cnt} apartments from page {page_number}: {url}")


        # Save processed apartments from current page (if there is any)
        if self.apartments:
            logging.info(f"Saving {len(self.apartments)} apartments...")

            # Save to both JSON and database (if available)
            storage.save_to_json(self.apartments)

            if self.db_manager:
                self.db_manager.save_apartments(self.apartments)

            self.apartments.clear()

        logging.info(f"{'-'*100}")

        # Get next page URL
        next_page_url = self._get_next_page_url(html, xpaths.NEXT_URL)
        return http.generate_url(relative_url=next_page_url) if next_page_url else None

    def process_apartments(self, html: html.HtmlElement, page_number: int) -> Tuple[int, int, int]:
        # Counters
        processed_count = 0
        exists_in_db_count = 0
        failed_cnt = 0

        # Extract apartment URLs from provided HTML
        apartments_urls = self._get_apartments_urls(html, xpaths.APARTMENTS_URLS_LIST)

        if apartments_urls is None:
            logging.warning("No apartments URLs found.")
            return processed_count, exists_in_db_count, failed_cnt # will be 0
        logging.info(f"Found {len(apartments_urls)} apartment URLs on page {page_number}") # by default 50 apartments per page

        # Process each apartment URL
        for idx, apartment_url in enumerate(apartments_urls, start=1):
            logging.info(f"At the moment processed: {processed_count} / skipped: {exists_in_db_count} / failed: {failed_cnt}")

            full_url = http.generate_url(relative_url=apartment_url)
            logging.info(f"Processing apartment [{idx}/{len(apartments_urls)}] on page {page_number}. Apartment URL: {full_url}")

            # Check if apartment already exists is database
            # Condition will be omitted if database is not connected
            if self.db_manager is not None and self.db_manager.check_apartment_exists(full_url):
                logging.info("Apartment already exists in database. Status: SKIPPED.")
                time.sleep(0.5)
                exists_in_db_count += 1
                continue

            # Process apartment
            # We will send request, parse then clean response and store result in self.apartments list
            # The result will be dictionary with scraped data about specific apartment
            if self.process_single_apartment(full_url):
                logging.info("Successfully processed! Status: OK.")
                processed_count += 1
            else:
                failed_cnt += 1

        return processed_count, exists_in_db_count, failed_cnt

    def process_single_apartment(self, apartment_full_url: str) -> bool:
        try:
            # Send and parse
            apartment_html = self._fetch_and_parse(apartment_full_url)
            if apartment_html is None:
                logging.error(f"Failed to fetch apartment page: {apartment_full_url}. Status: FAILED.")
                return False

            # Extract apartment data (returns dictionary)
            apartment = parser.extract_apartment_data(apartment_html, apartment_full_url)

            # Append parsed apartment data to the list
            self.apartments.append(apartment)
            return True
        except Exception as e:
            logging.error(f"Error processing apartment: {e}. URL: {apartment_full_url}")
            return False


    # Function helpers
    def _fetch_and_parse(self, url: str, page_number: Optional[int] = None) -> Optional[html.HtmlElement]:
        response = http.send_request(session=self.session, url=url)
        if response is None:
            logging.error(f"Request failed on page {page_number}: {url}")
            return None

        html = parser.parse_response(response)
        if html is None:
            logging.error(f"HTML parsing failed on page {page_number}: {response.url}")
            return None

        http.delay()
        return html

    def _get_apartments_urls(self, html: html.HtmlElement, xpath: str) -> Optional[List[str]]:
        logging.debug("Looking for apartment URLs from parsed HTML.")
        urls = parser.extract_element(element=html, xpath=xpath)
        return urls

    def _get_next_page_url(self, html: html.HtmlElement, xpath: str) -> Optional[str]:
        logging.debug("Looking for next page...")
        next_page = parser.extract_element(element=html, xpath=xpath)

        if next_page is None:
            logging.warning("No next page URL found")
            return None

        logging.info(f"Found next page URL: {next_page[0]}")
        return next_page[0]
