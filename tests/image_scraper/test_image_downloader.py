from pathlib import Path
from typing import Callable

import pytest
from pytest_mock import MockerFixture
from responses import RequestsMock

from image_scraper.image_downloader import Downloader


@pytest.fixture
def prepare_downloader(tmp_path: Path) -> Downloader:
    yield Downloader(tmp_path)


@pytest.mark.unittests
class TestDownloaderInit:
    def test_upload_folder_should_have_proper_value(self, tmp_path: Path) -> None:

        downloader = Downloader(tmp_path)

        assert downloader.upload_folder == tmp_path


@pytest.mark.unittests
class TestDownloaderSaveImage:
    def test_convert_string_into_bytes_object_should_be_called(
        self, tmp_path: Path, mocker: MockerFixture
    ) -> None:

        filename, file_src, file_bytes = "file_name", "file_src", b"WebLudus"
        convert_string_into_bytes_object_mock = mocker.patch(
            "image_scraper.image_downloader.Downloader.convert_string_into_bytes_object"
        )
        convert_string_into_bytes_object_mock.return_value = file_bytes
        write_bytes_to_file_mock = mocker.patch(
            "image_scraper.image_downloader.Downloader.write_bytes_to_file"
        )
        downloader = Downloader(tmp_path)

        downloader.save_image(filename, file_src)

        convert_string_into_bytes_object_mock.assert_called_once_with(file_src)
        write_bytes_to_file_mock.assert_called_once_with(tmp_path, filename, file_bytes)


@pytest.mark.unittests
class TestConvertStringIntoBytesObject:
    def test_request_get_and_content_should_be_called(
        self, prepare_downloader: Downloader, mocked_responses: RequestsMock
    ) -> None:
        file_src, request_body = "https://webludus.pl", "ImagoCMS"
        request = mocked_responses.get(
            file_src,
            body=request_body,
            status=200,
        )

        bytes_object = prepare_downloader.convert_string_into_bytes_object(file_src)

        assert bytes_object == bytes(request_body, encoding="utf-8")
        assert request.call_count == 1

    def test_if_response_status_is_not_200_raise_connection_error(
        self, prepare_downloader: Downloader, mocked_responses: RequestsMock
    ) -> None:
        file_src = "https://webludus.pl"
        mocked_responses.get(file_src, status=404)

        with pytest.raises(ConnectionError):
            prepare_downloader.convert_string_into_bytes_object(file_src)


@pytest.mark.integtests
class TestWriteBytesToFile:
    def test_file_should_have_proper_name_and_be_in_correct_place(
        self,
        tmp_path: Path,
        bytes_generator: Callable[[str], bytes],
    ) -> None:

        filename = "image.jpeg"
        image_bytes = bytes_generator(filename)

        Downloader.write_bytes_to_file(
            upload_folder=tmp_path, filename=filename, bytes_object=image_bytes
        )

        assert Path(tmp_path / filename).exists()
