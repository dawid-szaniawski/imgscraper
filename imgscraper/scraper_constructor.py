from logging import getLogger

from requests import Session

from imgscraper.src.core import ImageScraper
from imgscraper.src.scrapers.bs4_scraper import Bs4Scraper

log = getLogger(__name__)
SCRAPERS = {
    "bs4": Bs4Scraper,
}


def create_scraper(
    website_url: str, container_class: str, pagination_class: str, **kwargs
) -> ImageScraper:
    """Constructor for the ImageScraper object. Imports scrapers and delivers them to
    ImageScraper based on the information in the scraper variable.

    Args:
        website_url: the URL address of website to scan.
        container_class: a class of div or section element containing image
        pagination_class: a class of div or section element containing pagination
            URLs.

    Returns: the ImageScraper object."""
    pages_to_scan = kwargs.get("pages_to_scan", 1)
    if not isinstance(pages_to_scan, int):
        raise ValueError("The page_to_scan value should be INT type.")

    scraper = kwargs.get("scraper", "bs4")
    if scraper not in SCRAPERS:
        raise ValueError("This tool is not supported.")

    session = kwargs.get("session", None)
    if not isinstance(session, Session):
        log.info("No valid Session object found. Creating a new one...")
        session = Session()
        session.headers = {"User-Agent": "scrapper"}

    return ImageScraper(
        website_url=website_url,
        container_class=container_class,
        pagination_class=pagination_class,
        pages_to_scan=pages_to_scan,
        scraper=SCRAPERS[scraper](),
        session=session,
    )
