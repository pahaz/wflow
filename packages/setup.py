# coding=utf-8
import os
from setuptools import setup, find_packages

__author__ = 'pahaz'
__version__ = '0.2.4'
_root_path = os.path.join(os.path.dirname(__file__), '.')
os.chdir(_root_path)

setup(
    name="core",
    version=__version__,
    packages=find_packages(),
    scripts=[],
    install_requires=['cliff==1.7.0', 'six'],

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        # '': ['*'],
    },

    # metadata for upload to PyPI
    author=__author__,
    author_email="pahaz.blinov@gmail.com",
    description="Wflow core package",
    license="MIT",
    url="http://github.com/pahaz/wflow",
)
