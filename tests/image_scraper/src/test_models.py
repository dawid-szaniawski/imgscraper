from datetime import datetime

from pytest import mark

from image_scraper.src.models import ImagesSource, Image


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

        assert isinstance(image.as_dict(), dict)
        assert image.as_dict() == prepare_image_model_data

    def test_object_comparison_should_be_done_only_in_the_url_address_field(self):
        dt = datetime(2022, 10, 12, 14, 28, 21, 720446)
        image1 = Image(source="1", url_address="1", title="1", created_at=dt)
        image2 = Image(source="2", url_address="1", title="2", created_at=dt)
        image3 = Image(
            source="2", url_address="2", title="2", created_at=datetime.now()
        )
        image4 = Image(source="1", url_address="2", title="1", created_at=dt)
        image5 = Image(source="1", url_address="3", title="1", created_at=dt)
        images = {image1, image2, image3, image4, image5}
        unique_images = {image1, image3, image5}

        assert image1 == image2
        assert image1 != image3
        assert image1 != image4
        assert image3 == image4
        assert len(images) == 3
        assert images == unique_images

    def test_return_false_if_different_type_is_compared(
        self, prepare_image: Image
    ) -> None:
        assert prepare_image != "TEST"
