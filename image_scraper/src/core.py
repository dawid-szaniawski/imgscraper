from image_scraper.src.models import ImagesSource, Image
from image_scraper.src.scrapers.scraper import Scraper


class ImageScraper:
    """Image information retrieval tool."""

    def __init__(
        self,
        website_url: str,
        container_class: str,
        pagination_class: str,
        pages_to_scan: int,
        scraper: Scraper,
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
        if isinstance(images, list):
            for image in images:
                if isinstance(image, Image):
                    self._synchronization_data.append(image)
                else:
                    raise AttributeError(
                        f"Only Image objects can appear in the sync data.\n"
                        f"Invalid element: {image}.\n"
                        f"Invalid element type: {type(image)}."
                    )
        else:
            raise AttributeError(
                f"Invalid variable type.\nElement type: {type(images)}."
            )
