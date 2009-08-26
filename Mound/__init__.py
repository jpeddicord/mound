# Mound Data Manager <https://launchpad.net/mound>
# Copyright (C) 2009 Jacob Peddicord <jpeddicord@ubuntu.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os
from ConfigParser import RawConfigParser
from Mound.application import Application

class Mound:

    default_applications = {}
    applications = {}
    applications_lst = []

    def load_applications(self, appdir):
        """Load up the applications we can manage, using defaults if
        available."""
        self.load_defaults('/etc/userdata')

        for root, dirs, files in os.walk(appdir):
            # only toplevel scan
            if root != appdir:
                continue
            
            files.sort()
            for f in files:
                # we only want .desktop files, cheap check
                if not '.desktop' in f:
                    continue
                cp = RawConfigParser()
                try:
                    cp.read(os.path.join(appdir, f))
                except:
                    continue

                app = Application(f.replace('.desktop', ''))

                # look for the X-UserData key
                try:
                    locs = cp.get('Desktop Entry', 'X-UserData')
                except:
                    # load the default if available, otherwise skip
                    try:
                        locs = self.default_applications[app.name]
                    except:
                        continue
                try:
                    app.set_locations(locs.split(';'))
                except:
                    pass

                try:
                    app.full_name = cp.get('Desktop Entry', 'Name')
                except:
                    app.full_name = app.name

                # load the icon
                try:
                    app.icon_name = cp.get('Desktop Entry', 'Icon')
                except:
                    pass
                app.load_icon()

                # used to check if app is running
                try:
                    app.exec_name = cp.get('Desktop Entry', 'Exec').split(' ', 1)[0]
                    app.exec_name = os.path.basename(app.exec_name)
                except:
                    pass

                self.applications[app.name] = app
                # we need an ordered list as well
                self.applications_lst.append(app)

    def load_defaults(self, defaults_file):
        """Load the userdata defaults."""
        f = open(defaults_file, 'r')
        for line in f:
            line = line.rstrip()
            try:
                app = line.split(' ', 1)
                self.default_applications[app[0]] = app[1]
            except:
                continue
        f.close()
        return self.default_applications
