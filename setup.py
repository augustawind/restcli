#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import restcli

if sys.argv[-1] == "tag":
    os.system(
        "git tag -a %s -m 'version %s'"
        % (restcli.__version__, restcli.__version__)
    )
    os.system("git push --tags")
    sys.exit()

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist upload")
    os.system("python setup.py bdist_wheel upload")
    sys.exit()

if sys.argv[-1] == "test":
    os.system("pytest")
    sys.exit()

with open("README.rst") as f:
    readme = f.read()
with open("HISTORY.rst") as f:
    history = f.read()
with open("requirements.txt") as f:
    requirements = f.readlines()

setup(
    name="restcli",
    version=restcli.__version__,
    description="An API exploration and testing tool written in Python.",
    long_description=readme + "\n\n" + history,
    author="Dustin Rohde",
    author_email="dustin.rohde@gmail.com",
    url="https://github.com/dustinrohde/restcli",
    include_package_data=True,
    license="Apache",
    zip_safe=False,
    keywords="rest, http, api, client, cli, testing",
    packages=["restcli", "restcli.reqmod"],
    package_dir={
        "restcli": "restcli",
        "restcli.reqmod": "restcli/reqmod",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    test_suite="tests",
    entry_points="""
    [console_scripts]
    restcli=restcli.cli:cli
    """,
    install_requires=requirements,
    extras_require={
        "testing": ["pytest>=5.0.0"],
    },
)
