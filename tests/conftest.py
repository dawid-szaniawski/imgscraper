# pylint: disable=redefined-outer-name

from datetime import datetime
from typing import Generator

from bs4 import BeautifulSoup, ResultSet
from pytest import fixture
from requests import Session
from responses import RequestsMock

from imgscraper.src.core import ImageScraper
from imgscraper.src.models import Image, ImagesSource
from imgscraper.src.scrapers.scraper import Scraper

WEBSITE_URL: str = "https://webludus.pl/"
IMAGE_URL: str = "https://webludus.pl/img/image.jpg"
TITLE: str = "Webludus"
CONTAINER_CLASS: str = "simple-image"
PAGINATION_CLASS: str = "pagination"
PAGES_TO_SCAN: int = 4


@fixture(scope="session")
def anonymous_session() -> Session:
    session = Session()
    session.headers["User-Agent"] = "Chrome/118.0.0.0"
    return session


@fixture(scope="class")
def mocked_responses() -> Generator[RequestsMock, None, None]:
    """Yields responses.RequestsMock as a context manager."""
    with RequestsMock() as response:
        yield response


@fixture(scope="session")
def prepare_website_data() -> tuple[str, str, str, int]:
    return WEBSITE_URL, CONTAINER_CLASS, PAGINATION_CLASS, PAGES_TO_SCAN


@fixture(scope="class")
def prepare_images_source(anonymous_session: Session) -> ImagesSource:
    return ImagesSource(
        current_url_address=WEBSITE_URL,
        container_class=CONTAINER_CLASS,
        pagination_class=PAGINATION_CLASS,
        pages_to_scan=PAGES_TO_SCAN,
        session=anonymous_session,
    )


@fixture(scope="session")
def prepare_image_model_data() -> dict[str, str | datetime]:
    return {
        "source": WEBSITE_URL,
        "url_address": IMAGE_URL,
        "title": TITLE,
    }


@fixture(scope="session")
def prepare_image() -> Image:
    return Image(source=WEBSITE_URL, url_address=IMAGE_URL, title=TITLE)


@fixture
def prepare_image_scraper(
    prepare_website_data: tuple[str, str, str, int],
    prepare_image: Image,
    anonymous_session: Session,
) -> Generator[ImageScraper, None, None]:
    """Returns a mocker of the class inheriting from the Scraper. It contains mocks of
    the basic function of the scraper implementation."""

    class ScraperMocker(Scraper):
        """Mocker of the Scraper class.
        It has implementation of all the scraper methods."""

        def get_images_data(
            self,
            img_source: ImagesSource,
            last_sync_data: tuple[str] | None = None,
        ) -> tuple[list[Image], bool]:
            """The method that starts the synchronization process.

            Args:
                img_source: the ImagesSource object. Contains website data.
                last_sync_data: URLs of recently downloaded images (img_src).

            Returns: set containing dicts with images data:
                - image source (image page),
                - url_address (src from image object),
                - title (alt from image object)."""
            if img_source.current_url_address == "https://webludus.pl/":
                return [prepare_image], False
            if img_source.current_url_address == "https://webludus.pl/page/2":
                return [prepare_image], False
            return [prepare_image], True

        def find_next_page(
            self,
            img_source: ImagesSource,
            scraped_urls: set[str],
        ) -> tuple[str, set[str]]:
            """Search the HTML DOM for the next page URL address.

            Args:
                img_source: the ImagesSource object. Contains website data.
                scraped_urls: to avoid duplicates, it is required to provide previously
                    scanned URLs.

            Returns: tuple containing the next URL address, and set of scraped URLs."""
            if img_source.current_url_address == "https://webludus.pl/":
                return "https://webludus.pl/page/2", {
                    "https://webludus.pl/",
                }
            return "https://webludus.pl/page/3", {
                "https://webludus.pl/",
                "https://webludus.pl/page/2",
            }

    website_url, container_cls, pagination_cls, pages = prepare_website_data
    yield ImageScraper(
        website_url=website_url,
        container_class=container_cls,
        pagination_class=pagination_cls,
        pages_to_scan=pages,
        session=anonymous_session,
        scraper=ScraperMocker(),
    )


@fixture(scope="session")
def prepare_html_doc() -> str:
    return f"""<html><head><title>BS4 Mock</title></head>
    <body>
        <div class="{CONTAINER_CLASS}">
            <a href="https://webludus.pl/00">
                <img src="{IMAGE_URL}" alt="{TITLE}">
            </a>
        </div>
        <div class="{CONTAINER_CLASS}">
            <a href="https://webludus.pl/01">
                <img src="https://webludus.pl/img/image01.jpg" alt="Image 01">
            </a>
        </div>
        <div class="{CONTAINER_CLASS}">
            <a href="https://webludus.pl/01">
                <img src="https://webludus.pl/img/image01.jpg" alt="Image 01">
            </a>
        </div>
        <div class="{CONTAINER_CLASS}">
            <a href="https://webludus.pl/00">
                <img src="https://webludus.pl/img/image.jpg">
            </a>
        </div>
        <div class="{PAGINATION_CLASS}">
            <a href="https://webludus.pl">1</a>
            <a href="#">1</a>
            <a href="https://webludus.pl/random">Random</a>
            <a href="https://webludus.pl/page/1">1</a>
            <a href="https://webludus.pl/page/2">2</a>
            <a href="https://webludus.pl/page/3">3</a>
        </div>
    </body></html>"""


@fixture(scope="session")
def prepare_second_html_doc() -> str:
    return f"""<html><head><title>BS4 Mock</title></head>
        <body>
            <div class={CONTAINER_CLASS}>
                <a href="https://webludus.pl/02">
                    <img src="/img/image02.jpg" alt="Image 02">
                </a>
            </div>
            <div class="{CONTAINER_CLASS}">
                <a href="https://webludus.pl/01">
                    <img src="https://webludus.pl/img/image01.jpg" alt="Image 01">
                </a>
            </div>
            <div class="{CONTAINER_CLASS}">
                <a href="https://webludus.pl/03">
                    <img src="https://webludus.pl/img/last_seen_image.jpg" alt="Image">
                </a>
            </div>
            <div class="{CONTAINER_CLASS}">
                <a href="https://webludus.pl/04">
                    <img src="https://webludus.pl/img/image04.jpg" alt="Image 04">
                </a>
            </div>
            <div class="{PAGINATION_CLASS}">
                <a href="https://webludus.pl">1</a>
                <a href="#">3</a>
                <a href="https://webludus.pl/page/4">Next</a>
            </div>
        </body></html>"""


@fixture(scope="session")
def multiple_nested_images() -> ResultSet:
    html_doc = f"""<html><head><title>BS4 Mock</title></head>
        <body>
            <div class={CONTAINER_CLASS}>
                <div><div>
                    <a href="https://webludus.pl/10"><div>
                    <div><img src="/img/img099.jpg" alt="Image 099"></div>
                    <div><img src="/img/img100.jpg" alt="Image 100"></div>
                    </a>
                </div></div></div>
            </div>
        </body></html>"""
    return BeautifulSoup(html_doc, "html.parser").select(f".{CONTAINER_CLASS}")
