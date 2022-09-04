import pytest
import responses
from pytest_mock import MockerFixture
from bs4 import BeautifulSoup
from bs4.element import ResultSet

from image_scraper.scrapers.bs4_scraper import Bs4Scraper
from image_scraper.models import Image, ImagesSource


@pytest.mark.unittests
class TestGetImagesData:
    def test_find_image_holders_and_prepare_image_objects_should_be_called(
        self, mocker: MockerFixture, prepare_image_source
    ) -> None:
        find_image_holders_mock = mocker.patch(
            "image_scraper.scrapers.bs4_scraper.Bs4Scraper.find_image_holders"
        )
        image_holders = "webludus.pl"
        find_image_holders_mock.return_value = image_holders
        prepare_image_objects = mocker.patch(
            "image_scraper.scrapers.bs4_scraper.Bs4Scraper.prepare_image_objects"
        )

        Bs4Scraper().get_images_data(image_source=prepare_image_source)

        find_image_holders_mock.assert_called_once_with(
            prepare_image_source.current_url_address,
            prepare_image_source.container_class,
        )
        prepare_image_objects.assert_called_once_with(
            prepare_image_source.domain, image_holders
        )


@pytest.mark.unittests
class TestGetHtmlDom:
    def test_request_get_should_be_called(
        self,
        prepare_image_source,
        mocked_responses: responses.RequestsMock,
    ) -> None:
        images_source_website = mocked_responses.get(
            prepare_image_source.current_url_address
        )

        Bs4Scraper.get_html_dom(prepare_image_source.current_url_address)

        assert images_source_website.call_count == 1

    def test_return_value_should_be_beautiful_soup_object(
        self,
        prepare_image_source,
        mocked_responses: responses.RequestsMock,
        html_doc: str,
    ) -> None:
        mocked_responses.get(prepare_image_source.current_url_address, body=html_doc)

        beautiful_soup = Bs4Scraper.get_html_dom(
            prepare_image_source.current_url_address
        )

        assert isinstance(beautiful_soup, BeautifulSoup)


@pytest.mark.unittests
class TestFindImageHolders:
    def test_return_value_should_have_proper_type_and_length(
        self,
        mocker: MockerFixture,
        prepare_image_source,
        prepare_beautiful_soup,
    ) -> None:
        get_html_dom = mocker.patch(
            "image_scraper.scrapers.bs4_scraper.Bs4Scraper.get_html_dom"
        )
        get_html_dom.return_value = prepare_beautiful_soup

        image_holders = Bs4Scraper().find_image_holders(
            prepare_image_source.current_url_address,
            prepare_image_source.container_class,
        )

        assert isinstance(image_holders, ResultSet)
        assert len(image_holders) == 2


@pytest.mark.integtests
class TestPrepareImageObjects:
    @pytest.fixture
    def prepare_image_holders(
        self,
        mocker: MockerFixture,
        prepare_beautiful_soup,
        prepare_image_source,
    ) -> ResultSet:
        get_html_dom = mocker.patch(
            "image_scraper.scrapers.bs4_scraper.Bs4Scraper.get_html_dom"
        )
        get_html_dom.return_value = prepare_beautiful_soup

        image_holders = Bs4Scraper().find_image_holders(
            prepare_image_source.current_url_address,
            prepare_image_source.container_class,
        )

        yield image_holders

    def test_output_should_be_in_correct_type(
        self, prepare_image_holders: ResultSet, prepare_image_source: ImagesSource
    ) -> None:
        images = Bs4Scraper().prepare_image_objects(
            prepare_image_source.current_url_address, prepare_image_holders
        )

        assert len(images) == 1
        assert isinstance(images, set)
        assert isinstance(list(images)[0], Image)

    def test_output_should_have_correct_data(
        self, prepare_image_holders: ResultSet, prepare_image_source: ImagesSource
    ) -> None:
        expected_images = {
            Image(
                source="https://webludus.pl",
                url_address="https://webludus.pl/img/image.jpg",
                title="Imagocms",
            )
        }
        images = Bs4Scraper().prepare_image_objects(
            prepare_image_source.current_url_address, prepare_image_holders
        )
        assert images == expected_images


@pytest.mark.unittests
class TestFindImageData:
    def test_in_case_of_key_error_return_none(self) -> None:
        div_data = """<div class="simple-image"><a href="https://webludus.pl">
                                <img src="https://webludus.pl/img/image.jpg"></a>
                                </div>"""
        soup = BeautifulSoup(div_data, "html.parser")
        div = soup.div
        assert Bs4Scraper().find_image_data(div, "https://webludus.pl") is None

    def test_in_case_of_type_error_return_none(self) -> None:
        div_data = """<div class="simple-image"></div>"""
        soup = BeautifulSoup(div_data, "html.parser")
        div = soup.div
        assert Bs4Scraper().find_image_data(div, "https://webludus.pl") is None


@pytest.mark.integtests
class TestFindNextPage:
    def test_output_should_have_correct_value(
        self,
        prepare_image_source: ImagesSource,
        mocker: MockerFixture,
        prepare_beautiful_soup,
    ) -> None:
        get_html_dom = mocker.patch(
            "image_scraper.scrapers.bs4_scraper.Bs4Scraper.get_html_dom"
        )
        get_html_dom.return_value = prepare_beautiful_soup

        next_url, scraped_urls = Bs4Scraper().find_next_page(
            prepare_image_source.current_url_address,
            prepare_image_source.domain,
            prepare_image_source.pagination_class,
            set(),
        )

        assert next_url == "https://webludus.pl/page/2"
        assert scraped_urls == {
            "https://webludus.pl",
            "https://webludus.pl#",
            "https://webludus.pl/random",
            "https://webludus.pl/page/1",
        }

    def test_if_reach_index_6_in_pagination_div_raise_index_error(
        self, mocker: MockerFixture, prepare_image_source: ImagesSource
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
            "image_scraper.scrapers.bs4_scraper.Bs4Scraper.get_html_dom"
        )
        get_html_dom.return_value = BeautifulSoup(html_doc, "html.parser")

        with pytest.raises(IndexError):
            Bs4Scraper().find_next_page(
                prepare_image_source.current_url_address,
                prepare_image_source.domain,
                prepare_image_source.pagination_class,
                set(),
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

        assert bs4_url == domain + new_url


@pytest.mark.unittests
class TestIsThisReallyTheNextPage:
    domain = "https://webludus.pl"
    scraped = {domain}

    def test_false_if_new_url_is_in_scraped_urls(self) -> None:
        assert not Bs4Scraper().is_this_really_the_next_page(
            self.domain, self.domain, self.scraped
        )

    def test_false_if_number_sign_is_in_new_url(self) -> None:
        new_url = "https://webludus.pl#"

        assert not Bs4Scraper().is_this_really_the_next_page(
            self.domain, new_url, self.scraped
        )

    def test_false_if_ordinal_number_is_less_than_two(self) -> None:
        new_url = "https://webludus.pl/page/1"

        assert not Bs4Scraper().is_this_really_the_next_page(
            self.domain, new_url, self.scraped
        )

    def test_false_if_next_url_does_not_have_ordinal_number(self) -> None:
        new_url = "https://webludus.pl/page/one"

        assert not Bs4Scraper().is_this_really_the_next_page(
            self.domain, new_url, self.scraped
        )

    def test_true_if_next_url_is_ok(self) -> None:
        new_url = "https://webludus.pl/page/2"

        assert Bs4Scraper().is_this_really_the_next_page(
            self.domain, new_url, self.scraped
        )
