import pytest
import responses
from bs4 import BeautifulSoup, ResultSet
from pytest_mock import MockerFixture
from requests import Session

from imgscraper.src.models import Image, ImagesSource
from imgscraper.src.scrapers.bs4_scraper import Bs4Scraper


@pytest.fixture(scope="session")
def prepare_beautiful_soup(prepare_html_doc: str) -> BeautifulSoup:
    """Prepares the BeautifulSoup object based on prepare_html_doc fixture."""
    return BeautifulSoup(prepare_html_doc, "html.parser")


@pytest.mark.unittests
class TestGetImagesData:
    def test_find_image_holders_and_prepare_image_objects_should_be_called(
        self,
        mocker: MockerFixture,
        prepare_images_source: ImagesSource,
        prepare_beautiful_soup: BeautifulSoup,
    ) -> None:
        get_html_dom_mock = mocker.patch(
            "imgscraper.src.scrapers.bs4_scraper.Bs4Scraper._get_html_dom"
        )
        get_html_dom_mock.return_value = prepare_beautiful_soup
        prepare_image_objects = mocker.patch(
            "imgscraper.src.scrapers.bs4_scraper.Bs4Scraper._prepare_image_objects"
        )

        Bs4Scraper().get_images_data(img_source=prepare_images_source)

        get_html_dom_mock.assert_called_once_with(
            session=prepare_images_source.session,
            url_address=prepare_images_source.current_url_address,
        )
        prepare_image_objects.assert_called_once_with(
            domain=prepare_images_source.current_url_address,
            image_holders=prepare_beautiful_soup.select(
                "." + prepare_images_source.container_class
            ),
            last_sync_data=None,
        )


@pytest.mark.unittests
class TestGetHtmlDom:
    def test_request_get_should_be_called(
        self,
        prepare_images_source: ImagesSource,
        mocked_responses: responses.RequestsMock,
        anonymous_session: Session,
    ) -> None:
        images_source_website = mocked_responses.get(
            prepare_images_source.current_url_address
        )

        Bs4Scraper._get_html_dom(
            session=anonymous_session,
            url_address=prepare_images_source.current_url_address,
        )

        assert images_source_website.call_count == 1

    def test_return_value_should_be_beautiful_soup_object(
        self,
        prepare_images_source: ImagesSource,
        mocked_responses: responses.RequestsMock,
        prepare_html_doc: str,
        anonymous_session: Session,
    ) -> None:
        mocked_responses.get(
            prepare_images_source.current_url_address, body=prepare_html_doc
        )

        beautiful_soup = Bs4Scraper._get_html_dom(
            session=anonymous_session,
            url_address=prepare_images_source.current_url_address,
        )

        assert isinstance(beautiful_soup, BeautifulSoup)


@pytest.mark.integtests
class TestPrepareImageObjects:
    @pytest.fixture(scope="class")
    def prepare_image_holders(
        self, prepare_beautiful_soup: BeautifulSoup, prepare_images_source: ImagesSource
    ) -> ResultSet:
        """Prepares a ResultSet containing all of divs that have image inside.
        For this, it uses prepare_beautiful_soup and prepare_images_source fixture."""
        return prepare_beautiful_soup.select(
            "." + prepare_images_source.container_class
        )

    @pytest.fixture(scope="class")
    def prepare_second_image_holders(
        self, prepare_second_html_doc: str, prepare_images_source: ImagesSource
    ) -> ResultSet:
        """Prepares a ResultSet containing all of divs that have image inside.
        For this, it uses prepare_second_html_doc and prepare_images_source fixture."""
        return BeautifulSoup(prepare_second_html_doc, "html.parser").select(
            "." + prepare_images_source.container_class
        )

    def test_output_should_be_in_correct_type(
        self, prepare_image_holders: ResultSet, prepare_images_source: ImagesSource
    ) -> None:
        images = Bs4Scraper()._prepare_image_objects(
            prepare_images_source.current_url_address, prepare_image_holders
        )

        assert isinstance(images, tuple)
        assert isinstance(images[0], list)
        assert isinstance(images[1], bool)
        assert isinstance(images[0][0], Image)

    def test_output_should_have_correct_data(
        self,
        prepare_image_holders: ResultSet,
        prepare_images_source: ImagesSource,
    ) -> None:
        expected_images = [
            Image(
                source="https://webludus.pl/00",
                url_address="https://webludus.pl/img/image.jpg",
                title="Webludus",
            ),
            Image(
                source="https://webludus.pl/01",
                url_address="https://webludus.pl/img/image01.jpg",
                title="Image 01",
            ),
            Image(
                source="https://webludus.pl/01",
                url_address="https://webludus.pl/img/image01.jpg",
                title="Image 01",
            ),
        ]
        images = Bs4Scraper()._prepare_image_objects(
            prepare_images_source.current_url_address, prepare_image_holders
        )[0]
        assert images == expected_images

    def test_output_should_have_all_images(
        self, prepare_images_source: ImagesSource, multiple_nested_images: ResultSet
    ):
        expected = [
            Image(
                source="https://webludus.pl/10",
                url_address="https://webludus.pl/img/img100.jpg",
                title="Image 100",
            ),
            Image(
                source="https://webludus.pl/10",
                url_address="https://webludus.pl/img/img099.jpg",
                title="Image 099",
            ),
        ]
        images = Bs4Scraper()._prepare_image_objects(
            prepare_images_source.current_url_address, multiple_nested_images
        )[0]
        assert images == expected

    def test_first_image_in_document_should_be_most_recent(
        self,
        prepare_image_holders: ResultSet,
        prepare_images_source: ImagesSource,
    ):
        scraper = Bs4Scraper()
        img = scraper._prepare_image_objects(
            domain=prepare_images_source.current_url_address,
            image_holders=prepare_image_holders,
        )[0]

        assert img[0].title == "Webludus"
        assert img[0].source == "https://webludus.pl/00"
        assert img[0].url_address == "https://webludus.pl/img/image.jpg"
        assert img[-1].title == "Image 01"
        assert img[-1].source == "https://webludus.pl/01"
        assert img[-1].url_address == "https://webludus.pl/img/image01.jpg"

    def test_stop_scraping_if_image_is_in_last_sync_data(
        self,
        prepare_image_holders: ResultSet,
        prepare_images_source: ImagesSource,
    ):
        scraper = Bs4Scraper()
        last_sync = ("https://webludus.pl/img/image.jpg",)
        images_data = scraper._prepare_image_objects(
            prepare_images_source.current_url_address, prepare_image_holders, last_sync
        )
        assert len(images_data[0]) == 0
        assert images_data[1] is True


@pytest.mark.unittests
class TestFindImageData:
    def test_happy_path(self, prepare_second_html_doc: str) -> None:
        div = BeautifulSoup(prepare_second_html_doc, "html.parser").div
        expected_image_data = [
            (
                "https://webludus.pl/02",
                "https://webludus.pl/img/image02.jpg",
                "Image 02",
            )
        ]
        image_data = Bs4Scraper()._find_images_data(div, "https://webludus.pl/")
        assert image_data == expected_image_data

    def test_in_case_of_key_error_return_none(self) -> None:
        div_data = """
        <div class="simple-image">
            <a href="https://webludus.pl">
                <img src="https://webludus.pl/img/image.jpg">
            </a></div>"""
        div = BeautifulSoup(div_data, "html.parser").div
        assert Bs4Scraper()._find_images_data(div, "https://webludus.pl/") is None

    def test_in_case_of_type_error_return_none(self) -> None:
        div_data = """<div class="simple-image"></div>"""
        div = BeautifulSoup(div_data, "html.parser").div
        assert Bs4Scraper()._find_images_data(div, "https://webludus.pl/") is None

    def test_if_there_is_no_extension_in_img_src_return_none(self):
        div_data = """
        <div class="simple-image">
            <a href="https://webludus.pl">
                <img src="https://webludus.pl/img/image" alt="Webludus">
            </a></div>"""
        soup = BeautifulSoup(div_data, "html.parser")
        div = soup.div
        assert Bs4Scraper()._find_images_data(div, "https://webludus.pl/") is None


@pytest.mark.integtests
class TestFindNextPage:
    def test_output_should_have_correct_value(
        self,
        prepare_images_source: ImagesSource,
        mocker: MockerFixture,
        prepare_beautiful_soup: BeautifulSoup,
    ) -> None:
        get_html_dom = mocker.patch(
            "imgscraper.src.scrapers.bs4_scraper.Bs4Scraper._get_html_dom"
        )
        get_html_dom.return_value = prepare_beautiful_soup

        next_url, scraped_urls = Bs4Scraper().find_next_page(
            img_source=prepare_images_source,
            scraped_urls=set(),
        )

        assert next_url == "https://webludus.pl/page/2"
        assert scraped_urls == {
            "#",
            "https://webludus.pl",
            "https://webludus.pl/",
            "https://webludus.pl/#",
            "https://webludus.pl/random",
            "https://webludus.pl/page/1",
        }

    def test_if_reach_index_6_in_pagination_div_raise_index_error(
        self, mocker: MockerFixture, prepare_images_source: ImagesSource
    ) -> None:
        html_doc = """
        <div class="pagination">
            <a href="https://webludus.pl">1</a>
            <a href="https://webludus.pl">1</a>
            <a href="https://i1.webludus.pl">1</a>
            <a href="#">1</a>
            <a href="https://webludus.pl/random">Random</a>
            <a href="https://webludus.pl/page/1">1</a>
        </div>"""
        get_html_dom = mocker.patch(
            "imgscraper.src.scrapers.bs4_scraper.Bs4Scraper._get_html_dom"
        )
        get_html_dom.return_value = BeautifulSoup(html_doc, "html.parser")

        with pytest.raises(IndexError):
            Bs4Scraper().find_next_page(
                img_source=prepare_images_source,
                scraped_urls=set(),
            )


@pytest.mark.unittests
class TestAddDomainIntoURLAddress:
    def test_url_address_should_not_have_query_symbol(self) -> None:
        domain = "https://webludus.pl/"
        new_url = "https://webludus.pl/page/2?utm_source=image_scraper"

        bs4_url = Bs4Scraper().add_domain_into_url_address(domain, new_url)

        assert bs4_url == "https://webludus.pl/page/2"

    def test_return_new_url_if_it_have_http_protocol(self) -> None:
        domain = "https://webludus.pl/"
        new_url = "https://i1.webludus.pl/page/2"

        bs4_url = Bs4Scraper().add_domain_into_url_address(domain, new_url)

        assert bs4_url == new_url

    def test_add_domain_if_url_address_does_not_have_it(self) -> None:
        domain = "https://webludus.pl/"
        new_url = "/page/2"

        bs4_url = Bs4Scraper().add_domain_into_url_address(domain, new_url)

        assert bs4_url == domain + new_url[1:]


@pytest.mark.unittests
class TestIsThisReallyTheNextPage:
    domain = "https://webludus.pl"
    scraped = {domain}

    def test_false_if_new_url_is_in_scraped_urls(self) -> None:
        assert not Bs4Scraper()._is_this_really_the_next_page(
            self.domain, self.domain, self.scraped
        )

    def test_false_if_number_sign_is_in_new_url(self) -> None:
        new_url = "https://webludus.pl#"

        assert not Bs4Scraper()._is_this_really_the_next_page(
            self.domain, new_url, self.scraped
        )

    def test_false_if_ordinal_number_is_less_than_two(self) -> None:
        new_url = "https://webludus.pl/page/1"

        assert not Bs4Scraper()._is_this_really_the_next_page(
            self.domain, new_url, self.scraped
        )

    def test_false_if_next_url_does_not_have_ordinal_number(self) -> None:
        new_url = "https://webludus.pl/page/one"

        assert not Bs4Scraper()._is_this_really_the_next_page(
            self.domain, new_url, self.scraped
        )

    def test_true_if_next_url_is_ok(self) -> None:
        new_url = "https://webludus.pl/page/2"

        assert Bs4Scraper()._is_this_really_the_next_page(
            self.domain, new_url, self.scraped
        )
