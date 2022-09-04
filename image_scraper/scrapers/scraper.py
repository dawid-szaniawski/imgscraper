from abc import ABC, abstractmethod

from image_scraper.models import ImagesSource


class Scraper(ABC):
    @abstractmethod
    def get_images_data(self, image_source: ImagesSource) -> set[dict[str:str]]:
        pass

    @abstractmethod
    def find_next_page(
        self,
        current_url_address: str,
        domain: str,
        pagination_class: str,
        scraped_urls: set[str],
    ) -> tuple[str, list[str]]:
        pass
