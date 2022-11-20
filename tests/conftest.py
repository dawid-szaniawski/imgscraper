from datetime import datetime
from typing import Generator

from pytest import fixture
from responses import RequestsMock

from image_scraper.src.models import ImagesSource, Image


FAKE_TIME: datetime = datetime(2022, 10, 12, 14, 28, 21, 720446)
WEBSITE_URL: str = "https://webludus.pl/"
IMAGE_URL: str = "https://webludus.pl/img/image.jpg"
TITLE: str = "Webludus"
CONTAINER_CLASS: str = "simple-image"
PAGINATION_CLASS: str = "pagination"
PAGES_TO_SCAN: int = 4


@fixture(scope="class")
def mocked_responses() -> Generator[RequestsMock, None, None]:
    """Yields responses.RequestsMock as a context manager."""
    with RequestsMock() as response:
        yield response


@fixture(scope="session")
def prepare_website_data() -> tuple[str, str, str, int]:
    return WEBSITE_URL, CONTAINER_CLASS, PAGINATION_CLASS, PAGES_TO_SCAN


@fixture(scope="class")
def prepare_images_source() -> ImagesSource:
    return ImagesSource(
        current_url_address=WEBSITE_URL,
        container_class=CONTAINER_CLASS,
        pagination_class=PAGINATION_CLASS,
        pages_to_scan=PAGES_TO_SCAN,
    )


@fixture(scope="session")
def prepare_image_model_data() -> dict[str, str | datetime]:
    return {
        "source": WEBSITE_URL,
        "url_address": IMAGE_URL,
        "title": TITLE,
        "created_at": FAKE_TIME,
    }


@fixture(scope="session")
def prepare_image(prepare_image_model_data: dict[str, str | datetime]) -> Image:
    return Image(
        source=WEBSITE_URL, url_address=IMAGE_URL, title=TITLE, created_at=FAKE_TIME
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
            <a href="https://webludus.pl/02">
                <img src="https://webludus.pl/img/last_seen_image.jpg" alt="Image">
            </a>
        </div>
        <div class="{PAGINATION_CLASS}">
            <a href="https://webludus.pl">1</a>
            <a href="#">3</a>
            <a href="https://webludus.pl/page/4">Next</a>
        </div>
    </body></html>"""
