from abc import ABC, abstractmethod

from imgscraper.src.models import Image, ImagesSource


class Scraper(ABC):
    """Scans websites for images and returns data about them."""

    @abstractmethod
    def get_images_data(
        self, img_source: ImagesSource, last_sync_data: tuple[str] | None = None
    ) -> tuple[list[Image], bool]:
        """The method that starts the synchronization process.
        If, during synchronization, encounters an image located in last_sync_data,
        it stops synchronization and returns True as the second argument.
        If the synchronization is complete, the second argument will be False.

        Args:
            img_source: the ImagesSource object. Contains website data.
            last_sync_data: URLs of recently downloaded images (img_src).

        Returns: a tuple in which there is a set with Image objects and bool."""

    @abstractmethod
    def find_next_page(
        self,
        img_source: ImagesSource,
        scraped_urls: set[str],
    ) -> tuple[str, set[str]]:
        """Search the HTML DOM for the next page URL address.

        Args:
            img_source: the ImagesSource object. Contains website data.
            scraped_urls: to avoid duplicates, it is required to provide previously
                scanned URLs.

        Returns: tuple containing the next URL address, and set of scraped URLs."""
