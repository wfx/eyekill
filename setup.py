#!/usr/bin/env python
from distutils.core import setup
setup(
    name = 'eyekill',
    version = '2014.08.16.0',
    description = 'Eyekill is a tiny taskkiller',
    license = "GNU GPL",
    author = 'Wolfgang Morawetz (wfx)',
    author_email = 'wolfgang.morawetz@gmail.com',
    scripts = ['bin/eyekill.py'],
    data_files = [
        ('share/applications', ['data/eyekill.desktop']),
        ('share/icons', ['data/eyekill.png'])
    ]
)
