#!/usr/bin/env python
import os
from setuptools import setup


def read(*rnames):
    with open(os.path.join(os.path.dirname(__file__), *rnames)) as read_file:
        return read_file.read()


setup(
    name="isodate",
    version="0.7.0.dev0",
    packages=["isodate"],
    package_dir={"": "src"},
    # PyPI metadata
    author="Gerhard Weis",
    author_email="gerhard.weis@proclos.com",
    description="An ISO 8601 date/time/duration parser and formatter",
    license="BSD-3-Clause",
    license_files=("LICENSE",),
    # keywords = '',
    url="https://github.com/gweis/isodate/",
    long_description=(read("README.rst") + read("CHANGES.txt") + read("TODO.txt")),
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        # 'Environment :: Web Environment',
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    test_suite="isodate.tests.test_suite",
)
