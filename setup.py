import sys

from setuptools import setup

REQUIRED_PYTHON = (3, 10)

if sys.version_info[:2] < REQUIRED_PYTHON:
    sys.stderr.write(
        """\nUnsupported Python version\n.
        This version of ImgScraper requires at least Python {}.{}""".format(
            *REQUIRED_PYTHON
        )
    )
    sys.exit(1)

setup()
