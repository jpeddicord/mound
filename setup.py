#!/usr/bin/python

from distutils.core import setup
from DistUtilsExtra.command import *

setup_info = dict(
    name='mound',
    version='0.4.1',
    description='Mound Data Manager',
    author='Jacob Peddicord',
    author_email='jpeddicord@ubuntu.com',
    url='https://launchpad.net/mound',
    packages=['Mound', 'Mound.ui'],
    scripts=['mound-data-manager'],
    cmdclass={
        'build': build_extra.build_extra,
        'build_i18n': build_i18n.build_i18n,
    },
    data_files=[
        ('share/mound-data-manager', ['data/mound.ui']),
        ('/etc/xdg', ['data/userdata']),
        ('share/icons/hicolor/16x16/apps', ['data/16x16/mound-data-manager.png']),
        ('share/icons/hicolor/22x22/apps', ['data/22x22/mound-data-manager.png']),
        ('share/icons/hicolor/24x24/apps', ['data/24x24/mound-data-manager.png']),
        ('share/icons/hicolor/scalable/apps', ['data/scalable/mound-data-manager.svg']),
    ]
)

# write package information
f = open('Mound/info.py', 'w')
for item in ('name', 'version', 'description', 'author', 'author_email', 'url'):
    f.write("%s = '%s'\n" % (item, setup_info[item]))
f.close()

# write manpage
try:
    from docutils.core import publish_file
    from docutils.writers import manpage
    publish_file(source_path='data/mound-data-manager.txt',
                 destination_path='data/mound-data-manager.1',
                 writer=manpage.Writer())
except:
    print "manpage generation error; ignoring"

setup(**setup_info)

