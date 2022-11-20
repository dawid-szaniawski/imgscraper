Image_Scraper: yet another web scraper
====================================================
.. image:: https://github.com/dawid-szaniawski/image_scraper/actions/workflows/tox_tests.yml/badge.svg
   :target: https://github.com/dawid-szaniawski/image_scraper/actions
.. image:: https://codecov.io/gh/dawid-szaniawski/image_scraper/branch/master/graph/badge.svg?token=ILZBZ7HW6G
 :target: https://codecov.io/gh/dawid-szaniawski/image_scraper
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
        pagination_class="pagination"
    )

    img_scraper.start_sync()

    print(img_scraper.synchronization_data)

Output:

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

Pages to scan and scraper
~~~~~~~~~
The user can specify how many subpages should be scraped and what tool the application should use.

.. code-block:: python

    from image_scraper.scraper_constructor import create_image_scraper

    img_scraper = create_image_scraper(
        website_url="https://imagocms.webludus.pl/",
        container_class="image-holder",
        pagination_class="pagination",
        pages_to_scan=1,
        scraper="bs4"
    )

Last sync data
~~~~~~~~~
When starting the synchronization process, the user can provide data from the last synchronization (img.src).
If the application encounters a provided image, the process is terminated. All previously synced images are available.

.. code-block:: python

    from image_scraper.scraper_constructor import create_image_scraper

    img_scraper.start_sync(
        (
            "https://imagocms.webludus.pl/img/01.jpg",
            "https://imagocms.webludus.pl/img/02.jpg",
        )
    )


Image Object
~~~~~~~~~
The Image object provides the ``.as_dict()`` method to turn it into a dictionary.

.. code-block:: python

    img = Image(
            source="https://imagocms.webludus.pl/images/01/",
            url_address="https://imagocms.webludus.pl/img/01.jpg",
            title="String",
            created_at=datetime.datetime(2022, 10, 13, 16, 17, 39, 196078)
        ).as_dict()

Output:

.. code-block:: python

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

    $ pip install git+https://github.com/dawid-szaniawski/image_scraper
