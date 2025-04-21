from utils import logger
from spider.kvspider import KVSpider


log = logger.setup_logger()


def main():
    log.info("Application started")

    scraper = KVSpider()
    scraper.run_scraper()

if __name__ == "__main__":
    main()
