from image_scraper.models import ImagesSource, Image
from image_scraper.scrapers.scraper import Scraper


class ImageScraper:
    """Image information retrieval tool.

    Args:
        website_url:
        container_class:
        pagination_class:
        pages_to_scan:
        scraper:
    """

    def __init__(
        self,
        website_url: str,
        container_class: str,
        pagination_class: str,
        pages_to_scan: int,
        scraper: Scraper,
    ) -> None:
        self.image_source = ImagesSource(
            current_url_address=website_url,
            container_class=container_class,
            pagination_class=pagination_class,
            pages_to_scan=pages_to_scan,
        )
        self.scraper = scraper
        self._synchronization_data: list[Image] = []

    def start_sync(self) -> None:
        """Initiates the synchronization process, collecting the data of the images
        searched according to the provided guidelines."""
        images_data = set()
        scraped_urls = {
            self.image_source.current_url_address,
        }

        while self.image_source.pages_to_scan > 0:
            images_data.update(self.scraper.get_images_data(self.image_source))
            if self.image_source.pages_to_scan > 1:
                next_page_data = self.scraper.find_next_page(
                    current_url_address=self.image_source.current_url_address,
                    domain=self.image_source.domain,
                    pagination_class=self.image_source.pagination_class,
                    scraped_urls=scraped_urls,
                )
                self.image_source.current_url_address, scraped_urls = next_page_data
            self.image_source.pages_to_scan -= 1
        self.synchronization_data = list(images_data)

    @property
    def synchronization_data(self) -> list[Image]:
        return self._synchronization_data

    @synchronization_data.setter
    def synchronization_data(self, images: list[Image]) -> None:
        """Converts a set of Image objects into a list of dictionaries and append it
        into synchronization data."""
        self._synchronization_data.extend(images)
