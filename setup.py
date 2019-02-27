# -*- coding: utf-8 -*-

from distutils.core import setup
import os
import shutil
shutil.copy('README.md', 'tutil/README.md')

dir_setup = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_setup, 'tutil', 'release.py')) as f:
    # Defines __version__
    exec(f.read())

setup(name='tutil',
      version=__version__,
      description='Simple latex tools and command line interface.',
      author="Peter Bingham",
      author_email="petersbingham@hotmail.co.uk",
      packages=['tutil'],
      package_data={'tutil': ['README.md']}
     )
