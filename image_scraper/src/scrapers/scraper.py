from abc import ABC, abstractmethod

from image_scraper.src.models import ImagesSource, Image


class Scraper(ABC):
    """Scans websites for images and returns data about them."""

    @abstractmethod
    def get_images_data(
        self, image_source: ImagesSource, last_sync_data: tuple[str] | tuple[()] = ()
    ) -> tuple[set[Image], bool]:
        """The method that starts the synchronization process.

        Args:
            image_source: the ImagesSource object. Contains website data.
            last_sync_data: URLs of recently downloaded images (img_src).

        Returns: set containing the Image objects."""
        pass

    @abstractmethod
    def find_next_page(
        self,
        current_url_address: str,
        domain: str,
        pagination_class: str,
        scraped_urls: set[str],
    ) -> tuple[str, set[str]]:
        """Search the HTML DOM for the next page URL address.

        Args:
            current_url_address: the URL address of the website to scan for the next
                page.
            domain: domain and protocol of the website to scan for the next page.
            pagination_class: class of div or section element containing pagination
                URLs.
            scraped_urls: to avoid duplicates, it is required to provide previously
                scanned URLs.

        Returns: tuple containing the next URL address, and set of scraped URLs."""
        pass
