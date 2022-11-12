import pytest

from image_scraper.scraper_constructor import create_image_scraper
from image_scraper.src.scrapers.bs4_scraper import Bs4Scraper


@pytest.mark.integtests
class TestCreateImageScraper:
    def test_happy_path(self, prepare_website_data: tuple[str, str, str, int]) -> None:
        website_url, container_class, pagination_class, pages = prepare_website_data

        scraper = create_image_scraper(
            website_url, container_class, pagination_class, pages, scraper="bs4"
        )

        assert isinstance(scraper.scraper, Bs4Scraper)
        assert scraper.image_source.current_url_address == website_url
        assert scraper.image_source.domain == website_url
        assert scraper.image_source.container_class == container_class
        assert scraper.image_source.pagination_class == pagination_class
        assert scraper.image_source.pages_to_scan == pages

    def test_raise_attribute_error_if_there_are_no_images_in_list(
        self, prepare_website_data: tuple[str, str, str, int]
    ):
        website_url, container_class, pagination_class, pages = prepare_website_data

        with pytest.raises(ValueError, match="This tool is not supported."):
            create_image_scraper(
                website_url, container_class, pagination_class, pages, scraper="TEST"
            )
