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
default_dirs.reverse()

application_dirs = []
for d in XDGDATADIRS:
    application_dirs.insert(0, os.path.join(d, 'applications'))


class UserData:
    """
    Loads and manages userdata entries for applications.
    """

    def __init__(self):
        self.default_locations = DefaultsParser()
        self.applications = {}
        self._desktop_loaded = []

    def load_defaults(self, scan_directories=default_dirs):
        """
        Load the userdata defaults from all of the scan_directories.
        Directories loaded later with conflicting userdata entries will
        overwrite values from earlier files, so system directories should
        be loaded first and user last.
        """
        for sdir in scan_directories:
            userdata_file = os.path.join(sdir, 'userdata')
            try:
                self.default_locations.load_defaults(userdata_file)
            except: pass
        return self.default_locations
    
    def load_applications(self, scan_directories=application_dirs):
        """
        Load up the applications we can manage, using defaults from
        load_defaults if available. Searches scan_directories for applications
        to load, preferring earlier discovered userdata.
        """
        # scan all application directories
        for appdir in scan_directories:
            if not os.path.isdir(appdir):
                continue
            for f in os.listdir(appdir):
                # we only want .desktop files, cheap check
                if not '.desktop' in f:
                    continue
                # check for duplicates
                appname = f.replace('.desktop', '')
                
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

class ParsingError(Exception):
    pass
class DuplicateDefaultError(ParsingError):
    pass

class DefaultsParser(dict):
    """
    A simple parser for the default userdata files.
    Returns a dictionary of with appnames as keys and location lists as values.
    """

    def load_defaults(self, filename):
        """
        Load defaults from a file and merge with this list.
        """
        f = open(filename, 'r')
        loaded = {}
        for line in f:
            line = line.strip()
            if len(line) > 0 and line[0] != '#':
                appname, locations = line.split(' ', 1)
                appname, locations = appname.strip(), locations.strip()
                if appname in loaded:
                    raise DuplicateDefaultError, "%s is used more than once" % appname
                loaded[appname] = locations
        self.update(loaded)

