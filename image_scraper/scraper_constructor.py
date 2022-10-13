from image_scraper.src.core import ImageScraper
from image_scraper.src.scrapers.bs4_scraper import Bs4Scraper


SCRAPERS = {
    "bs4": Bs4Scraper(),
}


def create_image_scraper(
    website_url: str,
    container_class: str,
    pagination_class: str,
    pages_to_scan: int,
    scraper: str,
):
    if scraper in SCRAPERS:
        return ImageScraper(
            website_url=website_url,
            container_class=container_class,
            pagination_class=pagination_class,
            pages_to_scan=pages_to_scan,
            scraper=SCRAPERS[scraper],
        )
    else:
        raise NameError("This tool is not supported.")
