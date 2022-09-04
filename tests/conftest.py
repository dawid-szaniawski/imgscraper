from pathlib import Path

from pytest import fixture
from responses import RequestsMock
from bs4 import BeautifulSoup

from image_scraper.models import ImagesSource, Image


@fixture
def bytes_generator():
    def prepare_bytes(filename: str) -> bytes:
        file_path = Path(__file__) / f"../example_data/{filename}"
        with open(file_path, "rb") as f:
            return f.read()

    yield prepare_bytes


@fixture
def mocked_responses() -> RequestsMock:
    with RequestsMock() as response:
        yield response


@fixture(scope="class")
def prepare_website_data() -> dict[str, str | int]:
    return {
        "website_url": "https://webludus.pl",
        "container_class": "simple-image",
        "pagination_class": "pagination",
        "pages_to_scan": 2,
    }


@fixture(scope="class")
def prepare_image_source(prepare_website_data) -> ImagesSource:
    yield ImagesSource(
        current_url_address=prepare_website_data["website_url"],
        container_class=prepare_website_data["container_class"],
        pagination_class=prepare_website_data["pagination_class"],
        pages_to_scan=prepare_website_data["pages_to_scan"],
    )


@fixture(scope="class")
def prepare_image() -> Image:
    yield Image(
        source="https://webludus.pl/images/logo.png",
        title="Logo",
        url_address="https://webludus.pl",
    )


@fixture(scope="module")
def html_doc():
    yield """<html><head><title>BS4 Mock</title></head>
    <body>
        <div class="simple-image">
            <a href="https://webludus.pl">
                <img src="https://webludus.pl/img/image.jpg" alt="Imagocms">
            </a>
        </div>
        <div class="simple-image">
            <a href="https://webludus.pl">
                <img src="https://webludus.pl/img/image.jpg">
            </a>
        </div>
        <div class="pagination">
            <a href="https://webludus.pl">1</a>
            <a href="#">1</a>
            <a href="https://webludus.pl/random">Random</a>
            <a href="https://webludus.pl/page/1">1</a>
            <a href="https://webludus.pl/page/2">2</a>
        </div>
    </body></html>"""


@fixture(scope="module")
def prepare_beautiful_soup(html_doc) -> BeautifulSoup:
    yield BeautifulSoup(html_doc, "html.parser")
