from pytest import mark

from image_scraper.models import ImagesSource, Image


@mark.unittests
class TestImageSource:
    def test_image_source_domain_should_have_correct_data(
        self, prepare_image_source: ImagesSource
    ) -> None:
        image_source = prepare_image_source

        assert image_source.domain == "https://webludus.pl"


@mark.unittests
class TestImage:
    image_model_data = {
        "source": "https://webludus.pl/images/logo.png",
        "title": "Logo",
        "url_address": "https://webludus.pl",
    }

    def test_property_as_dict_should_have_correct_data(
        self, prepare_image: Image
    ) -> None:
        image = prepare_image

        assert isinstance(image.as_dict, dict)
        assert image.as_dict == self.__class__.image_model_data
