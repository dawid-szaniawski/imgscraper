from logging import getLogger

from requests import Session

from imgscraper.src.models import Image, ImagesSource
from imgscraper.src.scrapers.scraper import Scraper

log = getLogger(__name__)


class ImageScraper:
    """Image information retrieval tool."""

    def __init__(
        self,
        website_url: str,
        container_class: str,
        pagination_class: str,
        pages_to_scan: int,
        scraper: Scraper,
        session: Session,
    ) -> None:
        """Constructor.

        Args:
            website_url: the URL address of website to scan.
            container_class: a class of div or section element containing image
            pagination_class: a class of div or section element containing pagination
                URLs.
            pages_to_scan: how many pages should be scraped.
            scraper: tool to be used."""
        self.image_source = ImagesSource(
            current_url_address=website_url,
            container_class=container_class,
            pagination_class=pagination_class,
            pages_to_scan=pages_to_scan,
            session=session,
        )
        self.scraper = scraper
        self._synchronization_data: list[Image] = []

    def start_sync(self, last_sync_data: tuple[str] | None = None) -> None:
        """Initiates the synchronization process, collecting the data of the images
        searched according to the provided guidelines.

        Args:
            last_sync_data: URLs of recently downloaded images (img_src)."""
        images_data: list[Image] = []
        scraped_urls = {
            self.image_source.current_url_address,
        }

        while self.image_source.pages_to_scan > 0:
            images, duplication_flag = self.scraper.get_images_data(
                self.image_source, last_sync_data
            )
            images_data.extend(images)

            if duplication_flag:
                self.image_source.pages_to_scan = 0
            else:
                self.image_source.pages_to_scan -= 1

            if self.image_source.pages_to_scan > 0:
                next_page_data = self.scraper.find_next_page(
                    img_source=self.image_source,
                    scraped_urls=scraped_urls,
                )
                self.image_source.current_url_address, scraped_urls = next_page_data

        log.info("Synchronization completed. Scraped urls: %s", scraped_urls)
        self.synchronization_data = images_data

    @property
    def synchronization_data(self) -> list[Image]:
        return self._synchronization_data

    @synchronization_data.setter
    def synchronization_data(self, images: list[Image]) -> None:
        if not isinstance(images, list):
            raise AttributeError(
                f"Invalid variable type.\nElement type: {type(images)}."
            )

        images.reverse()
        for image in images:
            if image in self._synchronization_data:
                continue

            if isinstance(image, Image):
                self._synchronization_data.append(image)
            else:
                raise AttributeError(
                    f"Only Image objects can appear in the sync data.\n"
                    f"Invalid element: {image}.\n"
                    f"Invalid element type: {type(image)}."
                )
