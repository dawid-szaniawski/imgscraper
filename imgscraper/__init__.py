"""Simple library that allows you to retrieve image information from meme sites"""
from logging import NullHandler, getLogger

from .scraper_constructor import create_scraper

__version__ = "0.1.0"
__all__ = [
    "create_scraper",
]

getLogger(__name__).addHandler(NullHandler())
