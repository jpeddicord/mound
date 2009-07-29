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
from subprocess import Popen
from gtk import icon_theme_get_default

try:
    import xdg
    XDGDATA = xdg.xdg_data_home
    XDGCONFIG = xdg.xdg_config_home
    XDGCACHE = xdg.xdg_cache_home
except:
    XDGDATA = os.path.expanduser("~/.local/share")
    XDGCONFIG = os.path.expanduser("~/.config")
    XDGCACHE = os.path.expanduser("~/.cache")

mound_snapshots = os.path.join(XDGDATA, "mound-snapshots")
user_home = os.path.expanduser("~")
icon_theme_default = icon_theme_get_default()

class Application:
    
    def __init__(self, name):
        self.name = name
        self.locations = []
        self.full_name = ""
        self.icon_name = ""
        self.icon = None
        self.data_size = 0
        self.snapshots = {}
    
    def set_locations(self, locations):
        self.locations = []
        for loc in locations:
            loc = os.path.expanduser(loc)
            # we only allow locations in the home directory
            assert loc.find(user_home) == 0
            self.locations.append(loc)
    
    def load_icon(self):
        if not self.icon_name:
            return
        self.icon = icon_theme_default.load_icon(self.icon_name, 32, 0)
    
    def calculate_size(self, force=False):
        if self.data_size > 0 and not force:
            return self.data_size
        self.data_size = 0
        for location in self.locations:
            if not os.path.exists(location):
                continue
            if os.path.isdir(location):
                for root, dirs, files in os.walk(location):
                    for f in files:
                        self.data_size += os.path.getsize(os.path.join(root, f))
            else:
                self.data_size += os.path.getsize(location)
        return self.data_size
    
    def load_snapshots(self, force=False):
        if self.snapshots and not force:
            return
        ss_dir = os.path.join(mound_snapshots, self.name)
        for root, dirs, files in os.walk(ss_dir):
            for f in files:
                if not ".snapshot.tar.gz" in f:
                    continue
                f = os.path.join(root, f)
                snap_name = os.path.basename(f).split(".", 1)[0]
                self.snapshots[snap_name] = (
                    f,
                    os.path.getmtime(f),
                    os.path.getsize(f)
                )
    
    def take_snapshot(self, snapshot_name):
        app_snapshot_dir = os.path.join(mound_snapshots, self.name)
        if not os.path.isdir(app_snapshot_dir):
            os.makedirs(app_snapshot_dir)
        snap_filename = os.path.join(app_snapshot_dir, "%s.snapshot.tar.gz" % snapshot_name)
        cmd = ["tar", "-czf",
            snap_filename,
            "-C", user_home
        ]
        for loc in self.locations:
            # strip off the home directory for tar
            loc = loc.replace(user_home + "/", "")
            cmd.append(loc)
        print cmd
        p = Popen(cmd)
        returncode = p.wait()
        assert returncode == 0
        self.snapshots[snapshot_name] = (
            snap_filename,
            os.path.getmtime(snap_filename),
            os.path.getsize(snap_filename)
        )
    
    def revert_to_snapshot(self, snapshot_name):
        pass #TODO
    
    def delete_snapshot(self, snapshot_name):
        pass #TODO
