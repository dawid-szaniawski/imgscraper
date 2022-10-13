Image_Scraper: yet another web scraper
====================================================
.. image:: https://github.com/dawid-szaniawski/image_scraper/actions/workflows/tests.yml/badge.svg
   :target: https://github.com/dawid-szaniawski/image_scraper/actions
.. image:: https://www.codefactor.io/repository/github/dawid-szaniawski/image_scraper/badge
   :target: https://www.codefactor.io/repository/github/dawid-szaniawski/image_scraper
   :alt: CodeFactor
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: black

Image_Scraper is a simple library that allows you to retrieve image information from meme sites.

Usage
____

.. code-block:: python

    from image_scraper.scraper_constructor import create_image_scraper

    img_scraper = create_image_scraper(
        website_url="https://imagocms.webludus.pl/",
        container_class="image-holder",
        pagination_class="pagination",
        pages_to_scan=3,
        scraper="bs4"
    )

    img_scraper.start_sync()

    print(img_scraper.synchronization_data)

Output
~~~~~~~~~

.. code-block:: python

    [
        Image(
            source="https://imagocms.webludus.pl/images/01/",
            url_address="https://imagocms.webludus.pl/img/01.jpg",
            title="String",
            created_at=datetime.datetime(2022, 10, 13, 16, 17, 39, 196078)
        ),
        Image(
            source="https://imagocms.webludus.pl/images/02/",
            url_address="https://imagocms.webludus.pl/img/02.jpg",
            title="String",
            created_at=datetime.datetime(2022, 10, 13, 16, 17, 39, 852106)
        )
    ]

Image Object
~~~~~~~~~
The Image object provides the ``.as_dict`` property to turn it into a dictionary.

.. code-block:: python

    img = Image(
            source="https://imagocms.webludus.pl/images/01/",
            url_address="https://imagocms.webludus.pl/img/01.jpg",
            title="String",
            created_at=datetime.datetime(2022, 10, 13, 16, 17, 39, 196078)
        ).as_dict

    img = {
        "source": "https://imagocms.webludus.pl/images/01/",
        "url_address": "https://imagocms.webludus.pl/img/01.jpg",
        "title": "String",
        "created_at": datetime.datetime(2022, 10, 13, 16, 17, 39, 196078)
        }

Installation
------------

To install Image_Scraper, simply:

.. code-block:: bash

    $ pip install https://github.com/dawid-szaniawski/image_scraper