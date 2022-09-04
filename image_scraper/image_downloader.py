from pathlib import Path
from os.path import join

from requests import get


class Downloader:
    def __init__(self, upload_folder: Path):
        self.upload_folder = upload_folder

    def save_image(self, filename: str, file_src: str) -> None:
        bytes_object = self.convert_string_into_bytes_object(file_src)
        self.write_bytes_to_file(self.upload_folder, filename, bytes_object)

    @staticmethod
    def convert_string_into_bytes_object(image_src: str) -> bytes:
        response = get(image_src)
        if response.status_code == 200:
            return response.content
        else:
            raise ConnectionError(
                "Cannot download the file."
                f"The image source replied with a status {response.status_code}"
            )

    @staticmethod
    def write_bytes_to_file(
        upload_folder: Path, filename: str, bytes_object: bytes
    ) -> None:
        with open(join(upload_folder, filename), "wb") as file:
            file.write(bytes_object)
