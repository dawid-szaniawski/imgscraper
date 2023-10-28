import pytest
import responses
from requests import Session

from imgscraper.src.core import ImageScraper
from imgscraper.src.models import Image, ImagesSource
from imgscraper.src.scrapers import bs4_scraper, scraper


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
            prepare_image_scraper.synchronization_data = images  # type: ignore

    def test_raise_attribute_error_if_there_are_no_images_in_tuple(
        self, prepare_image: Image, prepare_image_scraper: ImageScraper
    ):
        images = [prepare_image, "str"]
        message = (
            "Only Image objects can appear in the sync data.\nInvalid element: str.\n"
            "Invalid element type: <class 'str'>."
        )

        with pytest.raises(AttributeError, match=message):
            prepare_image_scraper.synchronization_data = images  # type: ignore


@pytest.mark.integtests
class TestImageScraper:
    def test_synchronization_data_should_be_correct(
        self,
        prepare_website_data: tuple[str, str, str, int],
        mocked_responses: responses.RequestsMock,
        prepare_html_doc: str,
        prepare_second_html_doc: str,
        anonymous_session: Session,
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
        expected_sync_data = [
            Image(
                source="https://webludus.pl/01",
                title="Image 01",
                url_address="https://webludus.pl/img/image01.jpg",
            ),
            Image(
                source="https://webludus.pl/02",
                title="Image 02",
                url_address="https://webludus.pl/img/image02.jpg",
            ),
            Image(
                source="https://webludus.pl/00",
                title="Webludus",
                url_address="https://webludus.pl/img/image.jpg",
            ),
        ]
        image_scraper = ImageScraper(
            website_url=website_url,
            container_class=container_class,
            pagination_class=pagination_class,
            pages_to_scan=pages,
            scraper=bs4_scraper.Bs4Scraper(),
            session=anonymous_session,
        )

        image_scraper.start_sync(("https://webludus.pl/img/last_seen_image.jpg",))
        assert images_source_website_page_1.call_count == 2
        assert images_source_website_page_2.call_count == 2
        assert images_source_website_page_3.call_count == 1
        assert image_scraper.synchronization_data == expected_sync_data
