#!/usr/bin/env python
from distutils.core import setup

setup(
  name='reacter',
  version='0.1.0',
  author='Gary Hetzel',
  author_email='ghetzel@outbrain.com',
  packages=['reacter', 'reacter.agents'],
  scripts=['bin/reacter'],
  url='http://pypi.python.org/pypi/reacter/',
  license='LICENSE.txt',
  description='',
  long_description=open('reacter/README.md').read(),
  install_requires=[
    "PyYAML >= 3.1.0",
  ],
)