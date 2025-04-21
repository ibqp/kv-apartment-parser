import logging
from lxml import html
from typing import Optional, List
from requests.adapters import Response


def parse_html(response: Response) -> Optional[html.HtmlElement]:
    try:
        parsed_html = html.fromstring(response.content)
        if len(parsed_html) == 0:
            logging.error("Parsed HTML is empty")
            return None

        return parsed_html
    except Exception as e:
        logging.error(f"Failed to parse HTML: {e}")
        return None

def extract_element(element: html.HtmlElement, xpath: str) -> Optional[List[str]]:
    try:
        result = element.xpath(xpath)
        if len(result) == 0:
            logging.error("No elements found")
            return None

        return [str(item).strip() for item in result]
    except Exception as e:
        logging.error(f"Failed to extract element: {e}")
        return None
