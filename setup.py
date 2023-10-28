import sys

from setuptools import setup

REQUIRED_PYTHON = (3, 10)

if sys.version_info[:2] < REQUIRED_PYTHON:
    sys.stderr.write(
        f"""\nUnsupported Python version\n.
        This version of ImgScraper requires at least
         Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}"""
    )
    sys.exit(1)

setup()
