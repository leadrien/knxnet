#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup

__author__ = "Adrien Lescourt"
__copyright__ = "HES-SO 2014, Project EMG4B"
__credits__ = ["Adrien Lescourt"]
__version__ = "1.0.1"
__email__ = "adrien.lescourt@gmail.com"
__status__ = "Prototype"


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="knxnet",
    version="1.0.1",
    author="Adrien Lescourt",
    author_email="adrien.lescourt@gmail.com",
    description="Knxnet datagram frame creator / handler",
    license="HES-SO 2015, Project EMG4B",
    keywords="KNX",
    packages=['knxnet', 'tests'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
    ],
)
