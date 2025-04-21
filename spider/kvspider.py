import logging
from lxml import html
from config import xpaths
from typing import Optional
from utils import http, parser


class KVSpider:
    def __init__(self):
        logging.info("Initializing KVSpider")
        self.session = http.create_session()

    def run_scraper(self):
        # Get Initial URL
        current_url = http.get_initial_url()

        # Page counter
        current_page = 1

        # While there are url to scrape - scraper will work
        while current_url:
            next_url, success = self._process_single_page(current_url, current_page)
            if not success:
                break
            current_url = next_url
            current_page += 1

    def _process_single_page(self, url:str, page_number:int) -> tuple[Optional[str], bool]:
        logging.info(f"-------------------------> Processing page {page_number} <-------------------------")

        # Send request to given url
        response = http.send_request(session=self.session, url=url)
        if response is None:
            logging.warning(f"Skipping page {page_number} due to request failure")
            return None, False

        # Get html from a response
        html = parser.parse_html(response)
        if html is None:
            logging.warning(f"Skipping page {page_number} due to HTML parsing failure")
            return None, False

        # Process apartments on current page
        processed_count = self._process_page_apartments(html)
        logging.info(f"-------------------------> Processed {processed_count} apartments on page {page_number} <-------------------------")

        # Get next page URL
        next_page_url = self._get_next_page_url(html)
        if next_page_url:
            return http.generate_url(relative_url=next_page_url), True

        logging.info("Reached last page")
        return None, True

    def _process_page_apartments(self, html: html.HtmlElement) -> int:
        processed_count = 0
        apartments_urls = self._get_apartments_urls(html)

        if not apartments_urls:
            logging.warning("No apartment URLs found on page")
            return processed_count

        logging.info(f"-------------------------> Found {len(apartments_urls)} apartment URLs <-------------------------")

        for apartment_url in apartments_urls:
            full_url = http.generate_url(relative_url=apartment_url)
            print(full_url)
            # ...
            http.delay()

        return processed_count

    def _get_apartments_urls(self, html):
        urls = parser.extract_element(element=html, xpath=xpaths.APARTMENTS_URLS_LIST)
        return urls

    def _get_next_page_url(self, html):
        next_page = parser.extract_element(element=html, xpath=xpaths.NEXT_URL)

        if next_page is None:
            logging.info("No next page URL found")
            return None

        logging.debug(f"Found next page URL: {next_page[0]}")
        return next_page[0]
