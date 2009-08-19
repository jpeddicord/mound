#!/usr/bin/python

import distutils.core

setup_info = dict(
    name='Mound',
    version='0.1',
    description='Mound Data Manager',
    author='Jacob Peddicord',
    author_email='jpeddicord@ubuntu.com',
    url='https://launchpad.net/mound',
    packages=['Mound', 'Mound.ui'],
    scripts=['mound-data-manager'],
    data_files=[('share/mound', ['mound.ui'])]
)

distutils.core.setup(**setup_info)

