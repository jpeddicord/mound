# Mound Data Manager <https://launchpad.net/mound>
# Copyright (C) 2009-2010 Jacob Peddicord <jpeddicord@ubuntu.com>
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
from Mound.util import XDGCONFIGDIRS, XDGDATADIRS, LANG_FULL, LANG_SHORT


default_dirs = list(XDGCONFIGDIRS)
default_dirs.append('/etc')

class UserData:
    """
    Loads and manages userdata entries for applications.
    """
    default_locations = {}
    applications = {}
    _defaults_loaded = []
    _desktop_loaded = []

    def load_defaults(self, scan_directories=default_dirs):
        """
        Load the userdata defaults from all of the scan_directories,
        preferring userdata from files first in the list.
        """
        for sdir in scan_directories:
            userdata_file = os.path.join(sdir, 'userdata')
            print "Loading", userdata_file, "..."
            try:
                f = open(userdata_file, 'r')
            except:
                print '     failed.'
                continue
            # read this userdata file
            for line in f:
                line = line.rstrip()
                try:
                    appline = line.split(' ', 1)
                    # don't add to list if already loaded earlier
                    if appline[0] in self._defaults_loaded:
                        continue
                    self.default_locations[appline[0]] = appline[1]
                    # save to loaded list
                    self._defaults_loaded.append(appline[0])
                except:
                    continue
            f.close()
        return self.default_userdata
    
    def load_applications(self, scan_directories=XDGDATADIRS):
        """
        Load up the applications we can manage, using defaults from
        load_defaults if available. Searches scan_directories for applications
        to load, preferring earlier discovered userdata.
        """
        # scan all application directories
        for sdir in scan_directories:
            appdir = os.path.join(sdir, 'applications')
            if not os.path.isdir(appdir):
                continue
            for f in os.listdir(appdir):
                # we only want .desktop files, cheap check
                if not '.desktop' in f:
                    continue
                # check for duplicates
                appname = f.replace('.desktop', '')
                if appname in self._applications_loaded:
                    continue
                
                # create an application
                app = Application(appname)
                app.desktop_path = os.path.join(appdir, f)
                
                # load the desktop entry
                cp = RawConfigParser()
                try:
                    cp.read(app.desktop_path)
                except:
                    continue
                
                # look for the X-UserData key
                try:
                    locs = cp.get('Desktop Entry', 'X-UserData')
                except:
                    # load the default if available, otherwise skip
                    try:
                        locs = self.default_locations[appname]
                        app.is_default = True
                    except:
                        continue
                try:
                    app.set_locations(locs.split(';'))
                except:
                    app.locations = []
                
                # load the full name, i18nizing if we can
                try:
                    for lname in ('Name[%s]' % LANG_FULL, 'Name[%s]' % LANG_SHORT):
                        if cp.has_option('Desktop Entry', lname):
                            app.full_name = cp.get('Desktop Entry', lname)
                            break
                    if not app.full_name:
                        app.full_name = cp.get('Desktop Entry', 'Name')
                except:
                    app.full_name = appname

                # load the icon (works if gtk & display are available)
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

                self.applications[appname] = app
                
                # store the name if we loaded from the desktop entry to
                # prevent duplicates. if we loaded a default, don't add it
                # in case there is a line in a later file.
                if not app.is_default:
                    self._applications_loaded.append(appname)
