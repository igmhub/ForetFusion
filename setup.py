#!/usr/bin/env python
import distutils
from distutils.core import setup

description = "Coadding Lya-forest data in BOSS and eBOSS."

setup(name="b", 
      version="0.1.0",
      description=description,
      url="https://github.com/igmhub/ForetFusion",
      author="Anze Slosar, Jose Vazquez",
      packages=['ffusion'])


