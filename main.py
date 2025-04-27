from utils import logger
from spider.kvspider import KVSpider


log = logger.setup_logger()


def main():
    log.info("Parser started")

    spider = KVSpider()
    spider.run_scraper()

    log.info("Parser ended")

if __name__ == "__main__":
    main()
