from requests import get
from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag

from image_scraper.models import ImagesSource, Image
from image_scraper.scrapers.scraper import Scraper


class Bs4Scraper(Scraper):
    def get_images_data(self, image_source: ImagesSource) -> set[Image]:
        image_holders = self.find_image_holders(
            image_source.current_url_address, image_source.container_class
        )
        return self.prepare_image_objects(image_source.domain, image_holders)

    @staticmethod
    def get_html_dom(url_address: str) -> BeautifulSoup:
        """Convert string containing URL address into Response object,
        and then convert it into BeautifulSoup object.

        Returns:
            BeautifulSoup object containing HTML DOM."""
        request = get(url_address)
        return BeautifulSoup(request.text, "html.parser")

    def find_image_holders(
        self, url_address: str, images_container_class: str
    ) -> ResultSet:
        html_dom = self.get_html_dom(url_address)
        return html_dom.select("." + images_container_class)

    def prepare_image_objects(
        self, domain: str, image_holders: ResultSet
    ) -> set[Image]:
        images = set()

        for div in image_holders:
            image = self.find_image_data(div, domain)
            if image:
                images.add(image)
        return images

    def find_image_data(self, div: Tag, domain: str) -> Image:
        image = div.find("img")
        try:
            image_source = self.add_domain_into_url_address(
                domain, div.find("a")["href"]
            )
            image_src = self.add_domain_into_url_address(domain, image["src"])
            return Image(source=image_source, url_address=image_src, title=image["alt"])
        except TypeError:
            pass
        except KeyError:
            pass

    def find_next_page(
        self,
        current_url_address: str,
        domain: str,
        pagination_class: str,
        scraped_urls: set[str],
    ) -> tuple[str, set[str]]:
        """Search the HTML DOM for the next page URL address."""
        html_dom = self.get_html_dom(current_url_address)
        pagination_div = html_dom.select_one("." + pagination_class)

        next_url = pagination_div.find("a")["href"]
        next_url_index = 0

        while not self.is_this_really_the_next_page(
            current_url_address, next_url, scraped_urls
        ):
            scraped_urls.add(next_url)
            next_url_index += 1
            if next_url_index > 5:
                raise IndexError("Couldn't find the URL of the next subpage.")
            next_url = self.add_domain_into_url_address(
                domain,
                pagination_div.find_all("a")[next_url_index]["href"],
            )

        return next_url, scraped_urls

    @staticmethod
    def add_domain_into_url_address(domain: str, item_url: str) -> str:
        item_url = item_url.split("?")[0]
        if domain in item_url:
            return item_url
        elif "https://" in item_url or "http://" in item_url:
            return item_url
        return str(domain + item_url)

    @staticmethod
    def is_this_really_the_next_page(
        domain: str, new_url: str, scraped_urls: set[str]
    ) -> bool:
        if new_url in scraped_urls:
            return False
        elif new_url == domain + "#" or new_url == "#":
            return False
        else:
            try:
                return True if int(new_url[-1]) > 1 else False
            except ValueError:
                return False
