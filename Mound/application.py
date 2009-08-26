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
from subprocess import Popen, call
from shutil import rmtree, copyfile
import gtk

try:
    import xdg
    XDGDATA = xdg.xdg_data_home
    XDGCONFIG = xdg.xdg_config_home
    XDGCACHE = xdg.xdg_cache_home
except:
    XDGDATA = os.path.expanduser('~/.local/share')
    XDGCONFIG = os.path.expanduser('~/.config')
    XDGCACHE = os.path.expanduser('~/.cache')

mound_snapshots = os.path.join(XDGDATA, 'mound-snapshots')
user_home = os.path.expanduser('~')
icon_theme_default = gtk.icon_theme_get_default()
icon_unknown = gtk.Invisible().render_icon(gtk.STOCK_DIALOG_QUESTION, gtk.ICON_SIZE_DND)

class Application:

    def __init__(self, name):
        self.name = name
        self.locations = []
        self.full_name = ""
        self.icon_name = ""
        self.icon = None
        self.data_size = 0
        self.exec_name = ""
        self.snapshots = {}
        self.app_snapshot_dir = os.path.join(mound_snapshots, self.name)
    
    def __repr__(self):
        return "%s: %s" % (self.name, self.full_name)
    
    def set_locations(self, locations):
        self.locations = []
        for loc in locations:
            # substitute in XDG locations
            loc = loc.replace("$DATA", XDGDATA)
            loc = loc.replace("$CONFIG", XDGCONFIG)
            loc = loc.replace("$CACHE", XDGCACHE)
            loc = os.path.expanduser(loc)
            # we only allow locations in the home directory
            assert loc.find(user_home) == 0
            self.locations.append(loc)

    def load_icon(self):
        try:
            assert self.icon_name
            try:
                self.icon = icon_theme_default.load_icon(self.icon_name, 32, 0)
            except:
                if '/' not in self.icon_name:
                    self.icon_name = '/usr/share/pixmaps/' + self.icon_name
                self.icon = gtk.gdk.pixbuf_new_from_file(self.icon_name)
                self.icon = self.icon.scale_simple(32, 32, gtk.gdk.INTERP_BILINEAR)
        except:
            self.icon_name = None
            self.icon = icon_unknown

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
                        if os.path.isfile(os.path.join(root, f)):
                            self.data_size += os.path.getsize(os.path.join(root, f))
            else:
                self.data_size += os.path.getsize(location)
        return self.data_size

    def check_running(self):
        for root, dirs, files in os.walk("/proc"):
            for d in dirs:
                try:
                    pid = int(d)
                    f = open("/proc/%d/cmdline" % pid, "r")
                except:
                    continue
                exec_path = f.read().split("\x00")[0]
                f.close()
                exec_name = os.path.basename(exec_path)
                if self.exec_name == exec_name:
                    return True
            break # we only want toplevel, so only itereate once
        return False

    def delete_data(self):
        for loc in self.locations:
            if os.path.isdir(loc):
                rmtree(loc)
            elif os.path.exists(loc):
                os.remove(loc)

    def load_snapshots(self, force=False):
        if self.snapshots and not force:
            return
        self.snapshots = {}
        ss_dir = os.path.join(mound_snapshots, self.name)
        for root, dirs, files in os.walk(ss_dir):
            for f in files:
                if not '.snapshot.tar.gz' in f:
                    continue
                f = os.path.join(root, f)
                snap_name = os.path.basename(f).split('.', 1)[0]
                self.snapshots[snap_name] = (
                    f,
                    os.path.getmtime(f),
                    os.path.getsize(f)
                )

    def take_snapshot(self, snapshot_name):
        if not os.path.isdir(self.app_snapshot_dir):
            os.makedirs(self.app_snapshot_dir)
        snap_filename = os.path.join(self.app_snapshot_dir, '%s.snapshot.tar.gz' % snapshot_name)
        cmd = ['tar', '-cvzf',
            snap_filename,
            '-C', user_home
        ]
        for loc in self.locations:
            # strip off the home directory for tar
            loc = loc.replace(user_home + '/', '')
            cmd.append(loc)
        p = Popen(cmd)
        returncode = p.wait()
        assert returncode == 0
        self.snapshots[snapshot_name] = (
            snap_filename,
            os.path.getmtime(snap_filename),
            os.path.getsize(snap_filename)
        )

    def revert_to_snapshot(self, snapshot_name):
        if not os.path.exists(self.snapshots[snapshot_name][0]):
            return
        cmd = ['tar', '-xvz', '-C', user_home,
            '-f', self.snapshots[snapshot_name][0],
        ]
        p = Popen(cmd)
        returncode = p.wait()
        assert returncode == 0

    def delete_snapshot(self, snapshot_name):
        snap_filename = self.snapshots[snapshot_name][0]
        os.remove(snap_filename)

    def export_snapshot(self, snapshot_name, export_location):
        snap_filename = self.snapshots[snapshot_name][0]
        copyfile(snap_filename, export_location)

    def import_snapshot(self, import_location):
        copyfile(import_location, self.app_snapshot_dir)
