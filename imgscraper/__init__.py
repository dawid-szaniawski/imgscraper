"""Simple library that allows you to retrieve image information from meme sites"""
from logging import NullHandler, getLogger

from .scraper_constructor import create_scraper
from .src.models import Image


__version__ = "0.3.0"
__all__ = [
    "create_scraper",
    "Image",
]

getLogger(__name__).addHandler(NullHandler())
