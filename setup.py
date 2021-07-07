#!/usr/bin/env python3

from setuptools import setup
import re
import os
import subprocess
from subprocess import CalledProcessError

with open("README.rst", "r") as fh:
    long_description = fh.read()     


def version2pep440(version):
    '''normalises the version from git describe to pep440
    
    https://www.python.org/dev/peps/pep-0440/#id29
    '''
    if version[0] == 'v':
        version = version[1:]

    if u'-' in version:
        v = version.split('-')
        v_pep440 = "{}.dev{}".format(v[0], v[1])
    else:
        v_pep440 = version

    return v_pep440


git_version_string = subprocess.check_output('git describe', shell=True).decode("utf-8").rstrip()


if os.environ.get('CONDA_BUILD', 0) == 0:
    install_requires = []
    with open('requirements.txt', 'r') as f:
        while True:
            line = f.readline()
            if line == '':
                break
            if not line.strip().startswith('#'):
                install_requires.append(line.strip())
    cwd = os.getcwd()
    version = version2pep440( git_version_string )
else:
    # if it is a conda build requirements are going to be satisfied by conda
    install_requires = []
    cwd = os.path.join(os.environ.get('RECIPE_DIR'),'..')
    version = git_version_string

fname = os.path.join(cwd, 'brem', 'version.py')

if os.path.exists(fname):
    os.remove(fname)
with open(fname, 'w') as f:
    f.write('version = \'{}\''.format(version))

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
