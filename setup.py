#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Christopher C. Strelioff <chris.strelioff@gmail.com>
#
# Distributed under terms of the MIT license.

"""setup.py

Setup for lastfmapi-python3 project.
"""
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='py3fm',
    version='0.1',
    description='A Python 3 package for accessing the lasfm api.',
    long_description=long_description,
    url='https://github.com/cstrelioff/lastfmapi-python3',
    author='Christopher C. Strelioff',
    author_email='chris.strelioff@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='music API lastfm',
    packages=['py3fm']
)


