import pytest
import responses

from image_scraper.image_scraper import ImageScraper
from image_scraper.scrapers import scraper, bs4_scraper
from image_scraper.models import ImagesSource, Image


@pytest.fixture
def prepare_image_scraper(
    prepare_website_data: dict[str, str | int], prepare_image
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
                current_url_address: string containing URL address of the website to
                    scan for the next page.
                domain: string containing domain and protocol of the website to scan for
                    the next page.
                pagination_class: string containing class of div or section element
                    containing pagination URLs.
                scraped_urls: to avoid duplicates, it is required to provide previously
                    scanned URLs.

            Returns: tuple containing the next URL address, and set of scraped URLs."""
            return "https://webludus.pl/imagocms", {
                "https://webludus.pl",
            }

    yield ImageScraper(prepare_website_data, ScraperMocker())


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
        prepare_image_model_data: dict[str, str],
    ) -> None:
        prepare_image_scraper.start_sync()

        assert prepare_image_scraper.synchronization_data == [prepare_image_model_data]


@pytest.mark.integtests
class TestSynchronizationDataSetter:
    def test_synchronization_data_should_have_correct_output(
        self, prepare_image: Image, prepare_image_scraper: ImageScraper
    ) -> None:
        images = {prepare_image}

        prepare_image_scraper.synchronization_data = images

        assert isinstance(prepare_image_scraper.synchronization_data, list)
        assert isinstance(prepare_image_scraper.synchronization_data[0], dict)
        assert prepare_image_scraper.synchronization_data[0] == prepare_image.as_dict


@pytest.mark.integtests
class TestImageScraper:
    def test_synchronization_data_should_be_correct(
        self,
        prepare_website_data: dict[str, str | int],
        mocked_responses: responses.RequestsMock,
        prepare_html_doc: str,
        prepare_second_html_doc: str,
    ):
        images_source_website_page_1 = mocked_responses.get(
            prepare_website_data["website_url"], body=prepare_html_doc
        )
        images_source_website_page_2 = mocked_responses.get(
            prepare_website_data["website_url"] + "page/2", body=prepare_html_doc
        )
        images_source_website_page_3 = mocked_responses.get(
            prepare_website_data["website_url"] + "page/3", body=prepare_second_html_doc
        )
        expected_sync_data = sorted(
            [
                {
                    "source": "https://webludus.pl/00",
                    "title": "Imagocms",
                    "url_address": "https://webludus.pl/img/image.jpg",
                },
                {
                    "source": "https://webludus.pl/01",
                    "title": "Image 01",
                    "url_address": "https://webludus.pl/img/image01.jpg",
                },
                {
                    "source": "https://webludus.pl/02",
                    "title": "Image 02",
                    "url_address": "https://webludus.pl/img/image02.jpg",
                },
            ],
            key=lambda image: image["source"],
        )

        image_scraper = ImageScraper(prepare_website_data, bs4_scraper.Bs4Scraper())
        image_scraper.start_sync()
        sync_data = sorted(
            image_scraper.synchronization_data, key=lambda image: image["source"]
        )

        assert images_source_website_page_1.call_count == 2
        assert images_source_website_page_2.call_count == 2
        assert images_source_website_page_3.call_count == 1
        assert expected_sync_data == sync_data
