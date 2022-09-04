from image_scraper.models import ImagesSource, Image
from image_scraper.scrapers.scraper import Scraper


class ImageScraper:
    def __init__(self, website_data: dict[str, str | int], scraper: Scraper):
        self.image_source = self.prepare_images_source(website_data)
        self.scraper = scraper
        self._synchronization_data = []

    @staticmethod
    def prepare_images_source(website_data: dict[str, str | int]) -> ImagesSource:
        return ImagesSource(
            current_url_address=website_data["website_url"],
            container_class=website_data["container_class"],
            pagination_class=website_data["pagination_class"],
            pages_to_scan=website_data["pages_to_scan"],
        )

    def start_sync(self):
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
        self.synchronization_data = images_data

    @property
    def synchronization_data(self) -> list[dict]:
        return self._synchronization_data

    @synchronization_data.setter
    def synchronization_data(self, images: set[Image]) -> None:
        for image in images:
            self._synchronization_data.append(image.as_dict)
