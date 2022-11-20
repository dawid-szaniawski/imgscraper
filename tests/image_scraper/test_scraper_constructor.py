import pytest

from image_scraper.scraper_constructor import create_image_scraper
from image_scraper.src.scrapers.bs4_scraper import Bs4Scraper


@pytest.mark.integtests
class TestCreateImageScraper:
    def test_happy_path_without_kwargs(
        self, prepare_website_data: tuple[str, str, str, int]
    ) -> None:
        website_url, container_class, pagination_class, pages = prepare_website_data

        scraper = create_image_scraper(
            website_url,
            container_class,
            pagination_class,
        )

        assert isinstance(scraper.scraper, Bs4Scraper)
        assert scraper.image_source.current_url_address == website_url
        assert scraper.image_source.domain == website_url
        assert scraper.image_source.container_class == container_class
        assert scraper.image_source.pagination_class == pagination_class
        assert scraper.image_source.pages_to_scan == 1

    def test_happy_path_with_kwargs(
        self, prepare_website_data: tuple[str, str, str, int]
    ) -> None:
        website_url, container_class, pagination_class, pages = prepare_website_data

        scraper = create_image_scraper(
            website_url,
            container_class,
            pagination_class,
            pages_to_scan=pages,
            scraper="bs4",
        )

        assert isinstance(scraper.scraper, Bs4Scraper)
        assert scraper.image_source.current_url_address == website_url
        assert scraper.image_source.domain == website_url
        assert scraper.image_source.container_class == container_class
        assert scraper.image_source.pagination_class == pagination_class
        assert scraper.image_source.pages_to_scan == pages

    def test_raise_value_error_scraper_is_not_supported(
        self, prepare_website_data: tuple[str, str, str, int]
    ):
        website_url, container_class, pagination_class, pages = prepare_website_data

        with pytest.raises(ValueError, match="This tool is not supported."):
            create_image_scraper(
                website_url,
                container_class,
                pagination_class,
                scraper="TEST",
            )

    def test_raise_value_error_pages_to_scan_is_not_int_type(
        self, prepare_website_data: tuple[str, str, str, int]
    ):
        website_url, container_class, pagination_class, pages = prepare_website_data
        msg = "The page_to_scan value should be INT type."

        with pytest.raises(ValueError, match=msg):
            create_image_scraper(
                website_url,
                container_class,
                pagination_class,
                pages_to_scan="TEST",
            )
