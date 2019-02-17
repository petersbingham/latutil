# -*- coding: utf-8 -*-

from distutils.core import setup
import os
import shutil
shutil.copy('README.md', 'latutil/README.md')

dir_setup = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_setup, 'latutil', 'release.py')) as f:
    # Defines __version__
    exec(f.read())

setup(name='latutil',
      version=__version__,
      description='Simple latex tools and command line interface.',
      author="Peter Bingham",
      author_email="petersbingham@hotmail.co.uk",
      packages=['latutil'],
      package_data={'latutil': ['README.md']}
     )
