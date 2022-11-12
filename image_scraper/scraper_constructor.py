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
    **kwargs
) -> ImageScraper:
    """Constructor for the ImageScraper object. Imports scrapers and delivers them to
    ImageScraper based on the information in the scraper variable.

    Args:
        website_url: the URL address of website to scan.
        container_class: a class of div or section element containing image
        pagination_class: a class of div or section element containing pagination
            URLs.
        pages_to_scan: how many pages should be scraped.

    Returns: the ImageScraper object."""
    args = [website_url, container_class, pagination_class, pages_to_scan]
    if kwargs.get("scraper"):
        if kwargs["scraper"] in SCRAPERS:
            args.append(SCRAPERS[kwargs["scraper"]])
        else:
            raise ValueError("This tool is not supported.")
    else:
        args.append(SCRAPERS["bs4"])

    if kwargs.get("last_sync_data"):
        last_sync_data = kwargs["last_sync_data"]
        if isinstance(last_sync_data, tuple) and all(
            isinstance(i, str) for i in last_sync_data
        ):
            args.append(last_sync_data)
        else:
            raise ValueError("Last sync data should be tuple")

    return ImageScraper(*args)
