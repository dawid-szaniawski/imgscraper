from datetime import datetime

import pytest
import responses
from freezegun import freeze_time

from image_scraper.src.core import ImageScraper
from image_scraper.src.scrapers import scraper, bs4_scraper
from image_scraper.src.models import ImagesSource, Image


@pytest.fixture
def prepare_image_scraper(
    prepare_website_data: tuple[str, str, str, int], prepare_image
) -> ImageScraper:
    """Returns a mocker of the class inheriting from the Scraper. It contains mocks of
    the basic function of the scraper implementation."""

    class ScraperMocker(scraper.Scraper):
        """Mocker of the Scraper class.
        It has implementation of all the scraper methods."""

        def get_images_data(self, image_source: ImagesSource) -> set[Image]:
            """The method that starts the synchronization process.

            Args:
                image_source: the ImagesSource object. Contains website data.

            Returns: set containing dicts with images data:
                - image source (image page),
                - url_address (src from image object),
                - title (alt from image object)."""
            return {
                prepare_image,
            }

        def find_next_page(
            self,
            current_url_address: str,
            domain: str,
            pagination_class: str,
            scraped_urls: set[str],
        ) -> tuple[str, set[str]]:
            """Search the HTML DOM for the next page URL address.

            Args:
                current_url_address: URL address of the website to scan for the next
                    page.
                domain: domain and protocol of the website to scan for the next page.
                pagination_class: a class of div or section element containing
                    pagination URLs.
                scraped_urls: to avoid duplicates, it is required to provide previously
                    scanned URLs.

            Returns: tuple containing the next URL address, and set of scraped URLs."""
            return "https://webludus.pl/imagocms", {
                "https://webludus.pl",
            }

    website_url, container_cls, pagination_cls, pages = prepare_website_data
    yield ImageScraper(
        website_url=website_url,
        container_class=container_cls,
        pagination_class=pagination_cls,
        pages_to_scan=pages,
        scraper=ScraperMocker(),
    )


@pytest.mark.unittests
class TestInit:
    def test_image_scraper_object_should_have_correct_data(
        self, prepare_image_scraper: ImageScraper, prepare_images_source: ImagesSource
    ) -> None:
        assert prepare_image_scraper.image_source == prepare_images_source
        assert isinstance(prepare_image_scraper.scraper, scraper.Scraper)
        assert prepare_image_scraper.synchronization_data == []


@pytest.mark.integtests
class TestStartSync:
    def test_synchronization_process(
        self,
        prepare_image_scraper: ImageScraper,
        prepare_image: Image,
    ) -> None:
        prepare_image_scraper.start_sync()

        assert prepare_image_scraper.synchronization_data == [prepare_image]


@pytest.mark.integtests
class TestSynchronizationDataSetter:
    def test_synchronization_data_should_have_correct_output(
        self, prepare_image: Image, prepare_image_scraper: ImageScraper
    ) -> None:
        images = [prepare_image]

        prepare_image_scraper.synchronization_data = images

        assert isinstance(prepare_image_scraper.synchronization_data, list)
        assert isinstance(prepare_image_scraper.synchronization_data[0], Image)
        assert prepare_image_scraper.synchronization_data[0] == prepare_image

    def test_raise_attribute_error_if_user_does_not_use_list(
        self, prepare_image: Image, prepare_image_scraper: ImageScraper
    ):
        images = (prepare_image,)
        message = "Invalid variable type.\nElement type: <class 'tuple'>."

        with pytest.raises(AttributeError, match=message):
            prepare_image_scraper.synchronization_data = images

    def test_raise_attribute_error_if_there_are_no_images_in_list(
        self, prepare_image: Image, prepare_image_scraper: ImageScraper
    ):
        images = [prepare_image, "str"]
        message = (
            "Only Image objects can appear in the sync data.\nInvalid element: str.\n"
            "Invalid element type: <class 'str'>."
        )

        with pytest.raises(AttributeError, match=message):
            prepare_image_scraper.synchronization_data = images


@pytest.mark.integtests
class TestImageScraper:
    def test_synchronization_data_should_be_correct(
        self,
        prepare_website_data: tuple[str, str, str, int],
        mocked_responses: responses.RequestsMock,
        prepare_html_doc: str,
        prepare_second_html_doc: str,
    ):
        website_url, container_class, pagination_class, pages = prepare_website_data
        images_source_website_page_1 = mocked_responses.get(
            website_url, body=prepare_html_doc
        )
        images_source_website_page_2 = mocked_responses.get(
            website_url + "page/2", body=prepare_html_doc
        )
        images_source_website_page_3 = mocked_responses.get(
            website_url + "page/3", body=prepare_second_html_doc
        )
        creation_time = datetime(2022, 10, 12, 14, 28, 21, 720446)
        expected_sync_data = [
            Image(
                source="https://webludus.pl/00",
                title="Webludus",
                url_address="https://webludus.pl/img/image.jpg",
                created_at=creation_time,
            ),
            Image(
                source="https://webludus.pl/01",
                title="Image 01",
                url_address="https://webludus.pl/img/image01.jpg",
                created_at=creation_time,
            ),
            Image(
                source="https://webludus.pl/02",
                title="Image 02",
                url_address="https://webludus.pl/img/image02.jpg",
                created_at=creation_time,
            ),
        ]
        image_scraper = ImageScraper(
            website_url=website_url,
            container_class=container_class,
            pagination_class=pagination_class,
            pages_to_scan=pages,
            scraper=bs4_scraper.Bs4Scraper(),
        )

        with freeze_time(creation_time):
            image_scraper.start_sync()

        assert images_source_website_page_1.call_count == 2
        assert images_source_website_page_2.call_count == 2
        assert images_source_website_page_3.call_count == 1
        assert len(image_scraper.synchronization_data) == len(expected_sync_data)
        assert set(image_scraper.synchronization_data) == set(expected_sync_data)
