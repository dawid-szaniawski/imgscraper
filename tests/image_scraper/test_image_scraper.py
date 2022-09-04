import pytest
from pytest_mock import MockerFixture
from bs4 import BeautifulSoup

from image_scraper.image_scraper import ImageScraper
from image_scraper.models import ImagesSource, Image
from image_scraper.scrapers.bs4_scraper import Bs4Scraper


@pytest.fixture
def prepare_image_scraper(prepare_website_data: dict[str, str | int]) -> ImageScraper:
    yield ImageScraper(prepare_website_data, Bs4Scraper())


@pytest.mark.unittests
class TestInit:
    def test_image_scraper_object_should_have_correct_data(
        self, prepare_image_scraper: ImageScraper, prepare_image_source: ImagesSource
    ) -> None:
        assert prepare_image_scraper.image_source == prepare_image_source
        assert isinstance(prepare_image_scraper.scraper, Bs4Scraper)
        assert prepare_image_scraper.synchronization_data == []


@pytest.mark.integtests
class TestStartSync:
    def test_synchronization_process(
        self,
        prepare_image_scraper: ImageScraper,
        mocker: MockerFixture,
        prepare_beautiful_soup: BeautifulSoup,
    ) -> None:
        get_html_dom = mocker.patch(
            "image_scraper.scrapers.bs4_scraper.Bs4Scraper.get_html_dom"
        )
        get_html_dom.return_value = prepare_beautiful_soup

        prepare_image_scraper.start_sync()

        assert prepare_image_scraper.synchronization_data == [
            {
                "source": "https://webludus.pl",
                "url_address": "https://webludus.pl/img/image.jpg",
                "title": "Imagocms",
            }
        ]


class TestSynchronizationDataSetter:
    def test_synchronization_data_should_have_correct_output(
        self, prepare_image: Image, prepare_image_scraper: ImageScraper
    ) -> None:
        images = {prepare_image}

        prepare_image_scraper.synchronization_data = images

        assert isinstance(prepare_image_scraper.synchronization_data, list)
        assert isinstance(prepare_image_scraper.synchronization_data[0], dict)
        assert prepare_image_scraper.synchronization_data[0] == prepare_image.as_dict
