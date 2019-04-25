import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pyogre",
    version = "0.0.2",
    author = "Huseyin BIYIK",
    author_email = "boogiepop@gmx.com",
    description = ("TradeOgre python wrapper"),
    license = "GPL",
    keywords = "trade exchange tradegore bitcoin",
    url = "https://github.com/hbiyik/pyogre",
    packages=['pyogre'],
    long_description=read('readme.md'),
    install_requires=["requests"]
)