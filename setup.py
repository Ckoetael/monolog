"""
Mongo logger package
"""
from setuptools import setup, find_packages

import monolog


DESCRIPTION = 'MongoDB logger + std_logger'
AUTHOR = 'Alex Minko'
AUTHOR_EMAIL = "minko.a.r@gmail.com"
URL = "https://github.com/Ckoetael/monolog"
VERSION = monolog.__version__

setup(
    name="monolog",
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="BSD",
    url=URL,
    packages=find_packages(),
    install_requires=['pymongo >= 3.10'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    zip_safe=False,
)
