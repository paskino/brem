#!/usr/bin/env python3

from setuptools import setup
import re
import os
import subprocess
from subprocess import CalledProcessError

with open("README.rst", "r") as fh:
    long_description = fh.read()


install_requires = []
with open('requirements.txt', 'r') as f:
    while True:
        line = f.readline()
        if line == '':
            break
        if not line.strip().startswith('#'):
            install_requires.append(line.strip())
        


def version2pep440(version):
    '''normalises the version from git describe to pep440
    
    https://www.python.org/dev/peps/pep-0440/#id29
    '''
    if version[0] == 'v':
        version = version[1:]

    v = version.split('-')

    if len(v) >= 2:
        v_pep440 = "{}.dev{}".format(v[0], v[1])
    else:
        v_pep440 = "{}.dev{}".format(v[0])

    return v_pep440

version = version2pep440(
    subprocess.check_output('git describe', shell=True).decode("utf-8").rstrip()
)


if os.environ.get('CONDA_BUILD', 0) == 0:
      cwd = os.getcwd()
else:
      cwd = os.path.join(os.environ.get('RECIPE_DIR'),'..')

fname = os.path.join(cwd, 'brem', 'version.py')

if os.path.exists(fname):
    os.remove(fname)
with open(fname, 'w') as f:
    f.write('version = \'{}\''.format(version))

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
