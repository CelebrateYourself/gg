from setuptools import setup, find_packages
from os.path import join, dirname

with open(join(dirname(__file__), 'README.md')) as f:
    description = f.read()

setup(
    name="gallows",
    version="0.6.0",
    author="CelebrateYourself",
    description="The GUI program to test the knowledge with some modes",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/CelebrateYourself/gg",
    packages=find_packages(),
    include_package_data=True,
)
