import logging
from lxml import html
from utils import http
from config import xpaths
from typing import Optional
from utils.parser import Parser


class KVSpider:
    def __init__(self):
        self.session = http.create_session()

    # Main function
    def run_scraper(self):
        # Get initial url
        current_page_url = http.get_initial_url()

        # While there are url to scrape - scraper will work
        current_page_nr = 1
        while current_page_url:
            next_page_url = self.process_page(current_page_url, current_page_nr)
            current_page_url = next_page_url
            current_page_nr += 1

    # Spider functions
    def process_page(self, url:str, page_number:int) -> Optional[str]:
        logging.info(f"Processing page {page_number}: {url}")

        # Send request to given url and parse response
        html = self._fetch_and_parse(url, page_number)
        if html is None:
            logging.error(f"Failed to fetch apartments page: {url}")
            return None

        # Process apartments on current page
        processed_count = self.process_apartments(html, page_number)
        logging.info(f"Processed {processed_count} apartments on page {page_number}: {url}")

        # Get next page URL
        next_page_url = self._get_next_page_url(html, xpaths.NEXT_URL)
        return http.generate_url(relative_url=next_page_url) if next_page_url else None

    def process_apartments(self, html: html.HtmlElement, page_number: int) -> int:
        # Processed apartments counter
        processed_count = 0

        # Extract apartment URLs from provided HTML
        apartments_urls = self._get_apartments_urls(html, xpaths.APARTMENTS_URLS_LIST)
        if apartments_urls is None:
            logging.warning("No apartments URLs found.")
            return processed_count # will be 0
        logging.info(f"Found {len(apartments_urls)} apartment URLs on page {page_number}")

        # Process each apartment URL
        for idx, apartment_url in enumerate(apartments_urls, start=1):
            full_url = http.generate_url(relative_url=apartment_url)
            logging.info(f"Processing page {page_number}.{idx}: {full_url}")
            if self.process_single_apartment(full_url):
                processed_count += 1

        return processed_count

    def process_single_apartment(self, apartment_full_url: str) -> bool:
        try:
            # Send and parse
            apartment_html = self._fetch_and_parse(apartment_full_url)
            if apartment_html is None:
                logging.error(f"Failed to fetch apartment page: {apartment_full_url}")
                return False

            # Extract apartment data
            apartment = Parser.extract_apartment_data(apartment_html, apartment_full_url)
            print(apartment)
            return True

        except Exception as e:
            logging.error(f"Error processing apartment: {e}. URL: {apartment_full_url}")
            return False

    # Function helpers
    def _fetch_and_parse(self, url, page_number=None):
        response = http.send_request(session=self.session, url=url)
        if response is None:
            logging.error(f"Request failed on page {page_number}: {url}")
            return None

        html = Parser.parse_response(response)
        if html is None:
            logging.error(f"HTML parsing failed on page {page_number}: {response.url}")
            return None

        http.delay()
        return html

    def _get_apartments_urls(self, html, xpath):
        logging.debug("Looking for apartment URLs from parsed HTML.")
        urls = Parser.extract_element(element=html, xpath=xpath)
        return urls

    def _get_next_page_url(self, html, xpath):
        logging.debug("Looking for next page.")
        next_page = Parser.extract_element(element=html, xpath=xpath)

        if next_page is None:
            logging.warning("No next page URL found")
            return None

        logging.info(f"Found next page URL: {next_page[0]}")
        return next_page[0]
