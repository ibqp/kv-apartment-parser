from utils import logger, storage
from config.db import DATABASE_URL
from utils.db import DatabaseManager
from spider.kvspider import KVSpider
from contextlib import contextmanager


log = logger.setup_logger()


@contextmanager
def create_spider(db_manager: DatabaseManager | None):
    spider = KVSpider(db_manager)

    def save_apartments() -> None:
        if hasattr(spider, 'apartments') and spider.apartments:
            log.info(f"Saving {len(spider.apartments)} apartments...")

            # Save to JSON
            storage.save_to_json(spider.apartments)

            # Save to Database (if database is connected)
            if spider.db_manager:
                spider.db_manager.save_apartments(spider.apartments)

    try:
        yield spider
    except KeyboardInterrupt:
        log.info("Interrupted by user.")
        save_apartments()
    except Exception as e:
        log.error(f"Fatal error: {e}")
        save_apartments()
    finally:
        if hasattr(spider, 'session'):
            spider.session.close()
            log.info("Session closed!")


def main():
    log.info("Apartment scraping process started.")

    try:
        log.info("Preparing database...")
        db_manager = DatabaseManager(DATABASE_URL)
        db_manager.init_db()
        log.info("Database ready.")
    except Exception:
        log.error("Failed to initialize database. Continuing without database support.")
        db_manager = None

    with create_spider(db_manager) as spider:
        spider.run_scraper()

    log.info("Apartment scraping process ended.")


if __name__ == "__main__":
    main()
