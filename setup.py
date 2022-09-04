from setuptools import setup, find_packages

setup(
    name='images_scraper',
    version='0.1.0',
    install_requires=[
        "requests>=2.28.1",
        "beautifulsoup4>=4.11.1"
    ],
    tests_require=[
        "pytest",
        "pytest-mock",
        "pytest-cov",
        "black",
        "flake8",
        "responses"
    ],
    python_requires=">=3.10",
    packages=find_packages(),
    url='https://github.com/dawid-szaniawski/image_scraper',
    author='Dawid Szaniawski',
    author_email='dawidszaniawskiuz@gmail.com',
    description='Scans web pages for images.'
)
