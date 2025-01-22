from logging import getLogger

from bepatient import wait_for_value_in_request
from bs4 import BeautifulSoup, ResultSet, Tag
from requests import Session

from imgscraper.src.models import Image, ImagesSource
from imgscraper.src.scrapers.scraper import Scraper

log = getLogger(__name__)


class Bs4Scraper(Scraper):
    """Scans websites for images and returns data about them."""

    def get_images_data(
        self, img_source: ImagesSource, last_sync_data: tuple[str] | None = None
    ) -> tuple[list[Image], bool]:
        """Method that starts the synchronization process.
        If, during synchronization, encounters an image located in last_sync_data,
        it stops synchronization and returns True as the second argument.
        If the synchronization is complete, the second argument will be False.

        Args:
            img_source: the ImagesSource object. Contains website data.
            last_sync_data: URLs of recently downloaded images (img_src).

        Returns: a tuple in which there is a set with Image objects and bool."""
        html_dom = self._get_html_dom(
            session=img_source.session, url_address=img_source.current_url_address
        )
        return self._prepare_image_objects(
            domain=img_source.domain,
            image_holders=html_dom.select("." + img_source.container_class),
            last_sync_data=last_sync_data,
        )

    @staticmethod
    def _get_html_dom(session: Session, url_address: str) -> BeautifulSoup:
        """Convert string containing URL address into Response object,
        and then convert it into BeautifulSoup object.

        Args:
            url_address: string containing URL of scraped website.

        Returns: BeautifulSoup object containing HTML DOM."""
        text_response = wait_for_value_in_request(
            request=session.get(url=url_address), session=session
        ).text
        return BeautifulSoup(text_response, "html.parser")

    def _prepare_image_objects(
        self,
        domain: str,
        image_holders: ResultSet,
        last_sync_data: tuple[str] | None = None,
    ) -> tuple[list[Image], bool]:
        """Iterates over ResultSet of image holders and add images into a set.
        If it hits a previously scanned image, stops the iterations and returns True
        as the second argument.

        Args:
            domain: domain of the scraped website.
            image_holders: ResultSet object containing the images' data.
            last_sync_data: URLs of recently downloaded images (img_src).

        Returns: a tuple in which there is a set with Image objects and bool."""
        images: list[Image] = []
        duplicates = False

        for div in image_holders:
            if duplicates:
                break

            images_data = self._find_images_data(div, domain)
            if not images_data:
                continue

            for image in images_data:
                if last_sync_data and image[1] in last_sync_data:
                    log.debug("Previously provided image found. Interrupting sync...")
                    duplicates = True
                    break

                images.append(
                    Image(source=image[0], url_address=image[1], title=image[2])
                )

        return images, duplicates

    def _find_images_data(
        self, div: Tag, domain: str
    ) -> list[tuple[str, str, str]] | None:
        """Searches the Tag object for image-related data: source link, image source,
        and image description (alt).

        Args:
            div: Tag object containing a div with image.
            domain: domain of the scraped website.

        Returns: Image object based on the supplied div or None (if the required data
            cannot be found or the image source does not have the extension)."""
        div_data = div.find_all("img")
        if len(div_data) > 1:
            log.debug("Multiple images found in tag")
        images = []

        for image in div_data:
            try:
                image_source = self.add_domain_into_url_address(
                    domain, div.find("a")["href"]
                )
                img_src = self.add_domain_into_url_address(domain, image["src"])

                if img_src[-4] == "." or img_src[-5] == ".":
                    images.append((image_source, img_src, image["alt"]))

            except (TypeError, KeyError):
                log.exception("Encountered an issue. The image is being skipped.")

        return images[::-1] if len(images) > 0 else None

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
        scraped_urls.add(img_source.current_url_address)
        html_dom = self._get_html_dom(
            session=img_source.session, url_address=img_source.current_url_address
        )
        pagination_div = html_dom.select_one("." + img_source.pagination_class)

        next_url = self.add_domain_into_url_address(
            img_source.domain,
            pagination_div.find("a")["href"],
        )
        next_url_index = 0

        while not self._is_this_really_the_next_page(
            img_source.domain, next_url, scraped_urls
        ):
            scraped_urls.add(next_url)
            next_url_index += 1
            if next_url_index > 5:
                message = (
                    "Couldn't find the URL of the next subpage.\n"
                    f"Scraped URLs: {scraped_urls}\nCurrent URL: {next_url}"
                )
                raise IndexError(message)
            next_url = self.add_domain_into_url_address(
                domain=img_source.domain,
                item_url=pagination_div.find_all("a")[next_url_index]["href"],
            )

        return next_url, scraped_urls

    @staticmethod
    def add_domain_into_url_address(domain: str, item_url: str) -> str:
        """Adds domain if not present in URL address and deletes double slashes.

        Args:
            domain: domain of the scraped website.
            item_url: URL address there the domain may be missing.

        Returns: string containing correct URL address."""
        item_url = item_url.split("?")[0]
        if domain in item_url:
            return item_url
        if "https://" in item_url or "http://" in item_url:
            return item_url
        item_url.replace("//", "/")
        if item_url[0] == "/":
            item_url = item_url[1:]
        return str(domain + item_url)

    @staticmethod
    def _is_this_really_the_next_page(
        domain: str, new_url: str, scraped_urls: set[str]
    ) -> bool:
        """Return True if new_url is a valid URL address and has not been scraped
            before.

        Args:
            domain: domain of the scraped website.
            new_url: a URL address to check.
            scraped_urls: set of previously checked URL addresses."""
        scraped_urls.update((domain + "#", "#"))
        if new_url in scraped_urls:
            return False
        try:
            return int(new_url.split("/")[-1]) > 1
        except ValueError:
            return False
