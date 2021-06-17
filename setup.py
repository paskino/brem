#!/usr/bin/env python3

from setuptools import setup
import re
import os

with open("README.rst", "r") as fh:
    long_description = fh.read()

with open('brem/__init__.py') as fd:
    version = re.search("__version__ = '(.*)'", fd.read()).group(1)

install_requires = []
with open('requirements.txt', 'r') as f:
    while True:
        line = f.readline()
        if line == '':
            break
        if not line.strip().startswith('#'):
            install_requires.append(line.strip())
        

# if it is a conda build requirements are going to be satisfied by conda
if os.environ.get('CONDA_BUILD', 0) == 1:
    install_requires = []

name = "brem"

setup(name=name,
      version = version,
      description = 'Basic Remote Execution Manager',
      long_description = long_description,
      author = 'Alin M Elena, Edoardo Pasca',
      author_email = 'alin-marin.elena@stfc.ac.uk, edoardo.pasca@stfc.ac.uk',
      url = 'https://github.com/paskino/brem',
      packages = ['brem', 'brem.ui'],
      license = 'BSD-3',
      install_requires=install_requires,
      classifiers = [
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Physics",
      ],
      )
