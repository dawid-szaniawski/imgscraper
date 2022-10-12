from abc import ABC, abstractmethod

from image_scraper.models import ImagesSource, Image


class Scraper(ABC):
    """Scans websites for images and returns data about them."""

    @abstractmethod
    def get_images_data(self, image_source: ImagesSource) -> set[Image]:
        """The method that starts the synchronization process.

        Args:
            image_source: the ImagesSource object. Contains website data.

        Returns: set containing dicts with images data:
            - image source (image page),
            - url_address (src from image object),
            - title (alt from image object)."""
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
            current_url_address: string containing URL address of the website to scan
            for the next page.
            domain: string containing domain and protocol of the website to scan for
                the next page.
            pagination_class: string containing class of div or section element
                containing pagination URLs.
            scraped_urls: to avoid duplicates, it is required to provide previously
                scanned URLs.

        Returns: tuple containing the next URL address, and set of scraped URLs."""
        pass
