from setuptools import setup, find_packages
from os.path import join, dirname

with open(join(dirname(__file__), 'README.md')) as f:
    description = f.read()

setup(
    name='gallows',
    version='0.6.0',
    packages=find_packages(),
    long_description=description,
)
