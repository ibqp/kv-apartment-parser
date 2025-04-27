import time
import random
import logging
import requests
from typing import Optional
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from urllib.parse import urlparse, urljoin


# HTTP Settings
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
BACKOFF_FACTOR = 1.3
RETRY_STATUS_CODES = [403, 408, 429, 500, 502, 503, 504]
DELAY_MIN = 2.0
DELAY_MAX = 7.0
BASE_URL = "https://www.kv.ee"
REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    , "Accept-Encoding": "gzip, deflate, br, zstd"
    , "Accept-Language": "en-GB,en;q=0.5"
    , "Connection": "keep-alive"
    , "DNT": "1"
    , "Host": "www.kv.ee"
    , "Priority": "u=0, i"
    , "Sec-Fetch-Dest": "document"
    , "Sec-Fetch-Mode": "navigate"
    , "Sec-Fetch-Site": "cross-site"
    , "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"
}


def create_session() -> requests.Session:
    # Setup session
    session = requests.Session()

    # Configure retry strategy
    retries = Retry(
        total=MAX_RETRIES
        , backoff_factor=BACKOFF_FACTOR
        , status_forcelist=RETRY_STATUS_CODES
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)

    # Return session with configured retry strategy
    return session

def get_initial_url() -> str:
    default_url = f"{BASE_URL}/en/search?deal_type=1"
    url = input(f"Enter initial URL (default: {default_url}): ").strip()
    parsed = urlparse(url)
    return url if (parsed.scheme and parsed.netloc) else default_url

def generate_url(relative_url: str) -> str:
    url = urljoin(BASE_URL, relative_url)
    logging.debug(f"Generated URL from relative URL: {url}")
    return url

def delay():
    delay = random.uniform(DELAY_MIN, DELAY_MAX) + random.uniform(0.1, 1.0) # jitter
    logging.debug(f"Sleeping {delay:.2f} seconds.")
    time.sleep(delay)

def send_request(session: requests.Session, url: str) -> Optional[requests.Response]:
    try:
        logging.debug(f"Requesting from: {url}")
        # Send request to provided url
        response = session.get(
            url=url
            , headers=REQUEST_HEADERS
            , timeout=REQUEST_TIMEOUT
            , allow_redirects=True
        )
        response.raise_for_status()

        logging.debug(f"Request successful. Response received with status: {response.status_code}.")
        return response
    except requests.RequestException as e:
        logging.error(f"Request failed. Error: {e}. URL: {url}")
        return None
