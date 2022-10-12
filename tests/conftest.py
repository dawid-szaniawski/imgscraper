from pytest import fixture
from responses import RequestsMock

from image_scraper.models import ImagesSource, Image


@fixture(scope="class")
def mocked_responses() -> RequestsMock:
    """Yields responses.RequestsMock as a context manager."""
    with RequestsMock() as response:
        yield response


@fixture(scope="class")
def prepare_website_data() -> dict[str, str | int]:
    return {
        "website_url": "https://webludus.pl/",
        "container_class": "simple-image",
        "pagination_class": "pagination",
        "pages_to_scan": 3,
    }


@fixture(scope="session")
def prepare_image_model_data() -> dict[str, str]:
    return {
        "source": "https://webludus.pl",
        "url_address": "https://webludus.pl/img/image.jpg",
        "title": "Webludus",
    }


@fixture(scope="class")
def prepare_images_source(prepare_website_data: dict[str, str | int]) -> ImagesSource:
    yield ImagesSource(
        current_url_address=prepare_website_data["website_url"],
        container_class=prepare_website_data["container_class"],
        pagination_class=prepare_website_data["pagination_class"],
        pages_to_scan=prepare_website_data["pages_to_scan"],
    )


@fixture(scope="class")
def prepare_image(prepare_image_model_data) -> Image:
    yield Image(
        source=prepare_image_model_data["source"],
        url_address=prepare_image_model_data["url_address"],
        title=prepare_image_model_data["title"],
    )


@fixture(scope="session")
def prepare_html_doc() -> str:
    yield """<html><head><title>BS4 Mock</title></head>
    <body>
        <div class="simple-image">
            <a href="https://webludus.pl/00">
                <img src="https://webludus.pl/img/image.jpg" alt="Imagocms">
            </a>
        </div>
        <div class="simple-image">
            <a href="https://webludus.pl/01">
                <img src="https://webludus.pl/img/image01.jpg" alt="Image 01">
            </a>
        </div>
        <div class="simple-image">
            <a href="https://webludus.pl/01">
                <img src="https://webludus.pl/img/image01.jpg" alt="Image 01">
            </a>
        </div>
        <div class="simple-image">
            <a href="https://webludus.pl/00">
                <img src="https://webludus.pl/img/image.jpg">
            </a>
        </div>
        <div class="pagination">
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
    yield """<html><head><title>BS4 Mock</title></head>
    <body>
        <div class="simple-image">
            <a href="https://webludus.pl/02">
                <img src="https://webludus.pl/img/image02.jpg" alt="Image 02">
            </a>
        </div>
    </body></html>"""
