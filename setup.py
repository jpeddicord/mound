#!/usr/bin/python

import distutils.core

setup_info = dict(
    name='mound',
    version='0.3.1',
    description='Mound Data Manager',
    author='Jacob Peddicord',
    author_email='jpeddicord@ubuntu.com',
    url='https://launchpad.net/mound',
    packages=['Mound', 'Mound.ui'],
    scripts=['mound-data-manager'],
    data_files=[
        ('share/mound-data-manager', ['data/mound.ui']),
        ('share/applications', ['data/mound-data-manager.desktop']),
        ('/etc', ['data/userdata']),
        ('share/icons/hicolor/16x16/apps', ['data/16x16/mound-data-manager.png']),
        ('share/icons/hicolor/22x22/apps', ['data/22x22/mound-data-manager.png']),
        ('share/icons/hicolor/24x24/apps', ['data/24x24/mound-data-manager.png']),
        ('share/icons/hicolor/scalable/apps', ['data/scalable/mound-data-manager.svg']),
    ]
)

f = open('Mound/info.py', 'w')
for item in ('name', 'version', 'description', 'author', 'author_email', 'url'):
    f.write("%s = '%s'\n" % (item, setup_info[item]))
f.close()

distutils.core.setup(**setup_info)

