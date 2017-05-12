#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from importlib.machinery import SourceFileLoader

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# avoid loading the package before requirements are installed:
version = SourceFileLoader('version', 'restcli/version.py').load_module()

__version__ = str(version.VERSION)

if sys.argv[-1] == 'tag':
    os.system("git tag -a %s -m 'version %s'" % (__version__, __version__))
    os.system("git push --tags")
    sys.exit()

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'test':
    os.system('pytest')
    sys.exit()

with open('README.rst', 'r') as f:
    readme = f.read()
with open('HISTORY.rst', 'r') as f:
    history = f.read()

setup(
    name='restcli',
    version=__version__,
    description='An API client library and CLI written in Python. Postman for terminal lovers!',
    long_description=readme + '\n\n' + history,
    author='Dustin Rohde',
    author_email='dustin.rohde@gmail.com',
    url='https://github.com/dustinrohde/restcli',
    include_package_data=True,
    license="Apache",
    zip_safe=False,
    keywords='rest, http, api, client, cli, testing',
    packages=['restcli'],
    package_dir={'restcli': 'restcli'},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
    ],
    test_suite='tests',
    entry_points="""
    [console_scripts]
    restcli=restcli.cli:cli
    """,
    install_requires=[
        'click>=6,<7',
        'jinja2>=2,<3',
        'prompt_toolkit>=1,<2',
        'Pygments>=2,<3',
        'PyYAML>=3,<4',
        'requests>=2,<3',
    ],
    extras_require={
        'testing': ['pytest>=3.0.5'],
    }
)
