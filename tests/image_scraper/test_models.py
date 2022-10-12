from pytest import mark

from image_scraper.models import ImagesSource, Image


@mark.unittests
class TestImageSource:
    def test_image_source_domain_should_have_correct_data(
        self, prepare_images_source: ImagesSource
    ) -> None:
        image_source = prepare_images_source

        assert image_source.domain == "https://webludus.pl/"


@mark.unittests
class TestImage:
    def test_property_as_dict_should_have_correct_data(
        self, prepare_image: Image, prepare_image_model_data: dict[str, str]
    ) -> None:
        image = prepare_image

        assert isinstance(image.as_dict, dict)
        assert image.as_dict == prepare_image_model_data
