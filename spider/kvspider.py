import logging
from lxml import html
from config import xpaths
from typing import Optional
from utils import http, parser


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

            # Extract data
            apartment_address = parser.extract_element(apartment_html, xpaths.APARTMENT_ADDRESS)
            apartment_price = parser.extract_element(apartment_html, xpaths.APARTMENT_PRICE)
            apartment_price_per_m2 = parser.extract_element(apartment_html, xpaths.APARTMENT_PRICE_PER_M2)
            apartment_images = parser.extract_element(apartment_html, xpaths.APARTMENT_IMAGES)
            apartment_rooms = parser.extract_element(apartment_html, xpaths.APARTMENT_ROOMS)
            apartment_bedrooms = parser.extract_element(apartment_html, xpaths.APARTMENT_BEDROOMS)
            apartment_total_area = parser.extract_element(apartment_html, xpaths.APARTMENT_TOTAL_AREA)
            apartment_floor = parser.extract_element(apartment_html, xpaths.APARTMENT_FLOOR)
            apartment_build_year = parser.extract_element(apartment_html, xpaths.APARTMENT_BUILD_YEAR)
            apartment_cadastre_nr = parser.extract_element(apartment_html, xpaths.APARTMENT_CADASTRE_NR)
            apartment_energy_mark = parser.extract_element(apartment_html, xpaths.APARTMENT_ENERGY_MARK)
            apartment_utilities_summer = parser.extract_element(apartment_html, xpaths.APARTMENT_UTILITIES_SUMMER)
            apartment_utilities_winter = parser.extract_element(apartment_html, xpaths.APARTMENT_UTILITIES_WINTER)
            apartment_ownership_form = parser.extract_element(apartment_html, xpaths.APARTMENT_OWNERSHIP_FORM)
            apartment_condition = parser.extract_element(apartment_html, xpaths.APARTMENT_CONDITION)
            print({
                "url": apartment_full_url,
                "address": apartment_address,
                "price": apartment_price,
                "price_per_m2": apartment_price_per_m2,
                "images": apartment_images,
                "rooms": apartment_rooms,
                "bedrooms": apartment_bedrooms,
                "total_area": apartment_total_area,
                "floor": apartment_floor,
                "build_year": apartment_build_year,
                "cadastre_nr": apartment_cadastre_nr,
                "energy_mark": apartment_energy_mark,
                "utilities_summer": apartment_utilities_summer,
                "utilities_winter": apartment_utilities_winter,
                "ownership_form": apartment_ownership_form,
                "condition": apartment_condition
            })
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

        html = parser.parse_html(response)
        if html is None:
            logging.error(f"HTML parsing failed on page {page_number}: {response.url}")
            return None

        http.delay()
        return html

    def _get_apartments_urls(self, html, xpath):
        logging.debug("Looking for apartment URLs from parsed HTML.")
        urls = parser.extract_element(element=html, xpath=xpath)
        return urls

    def _get_next_page_url(self, html, xpath):
        logging.debug("Looking for next page.")
        next_page = parser.extract_element(element=html, xpath=xpath)

        if next_page is None:
            logging.warning("No next page URL found")
            return None

        logging.info(f"Found next page URL: {next_page[0]}")
        return next_page[0]
