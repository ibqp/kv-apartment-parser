import logging
from lxml import html
from typing import Optional, List
from requests.adapters import Response


def parse_html(response: Response) -> Optional[html.HtmlElement]:
    try:
        logging.debug(f"Parsing HTML from received response. Response URL: {response.url}")
        decoded_content = response.content.decode('utf-8', errors='ignore')
        parsed_html = html.fromstring(decoded_content)
        if len(parsed_html) == 0:
            logging.error("Parsed HTML is empty.")
            return None

        logging.debug("HTML parsed successfully.")
        return parsed_html
    except Exception as e:
        logging.error(f"Failed to parse HTML: {e}")
        return None

def extract_element(element: html.HtmlElement, xpath: str) -> Optional[List[str]]:
    try:
        logging.debug(f"Extracting elements using xpath: {xpath}")
        result = element.xpath(xpath)
        if len(result) == 0:
            logging.debug("No elements found.")
            return None

        logging.debug("Elements extracted successfully.")
        return [str(item).strip() for item in result]
    except Exception as e:
        logging.error(f"Failed to extract elements: {e}")
        return None
