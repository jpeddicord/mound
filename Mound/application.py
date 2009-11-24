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
from shutil import rmtree, copyfile
from Mound.util import XDGDATA, XDGCONFIG, XDGCACHE

MOUND_DATA = os.path.join(XDGDATA, 'mound')
MOUND_SNAPSHOTS = os.path.join(MOUND_DATA, 'snapshots')
USER_HOME = os.path.expanduser('~')

# skip loading GTK if there is no display
if os.environ.get('DISPLAY', None):
    import gtk
    ICON_THEME_DEFAULT = gtk.icon_theme_get_default()
    ICON_UNKNOWN = gtk.Invisible().render_icon(gtk.STOCK_DIALOG_QUESTION, gtk.ICON_SIZE_DND)
else:
    ICON_UNKNOWN = None

# these cannot be managed
RESTRICTED = (
    USER_HOME,
    XDGDATA,
    XDGCONFIG,
    XDGCACHE,
# re-state the XDG directories in case they have been changed
    '~/.local',
    '~/.local/share',
    '~/.cache',
    '~/.config',
# and some extras
    '~/.gnome2',
    '~/.gconf',
)

class ApplicationError(Exception):
    def __init__(self, application, message):
        self.application = application
        self.msg = message
class LocationError(ApplicationError):
    def __init__(self, application, message):
        self.application = application
        self.msg = message
        application.errors.append(self)
        print _("Error in %(application)s: %(error)s") % {'application': application.name, 'error': message}
class SnapshotError(ApplicationError): pass

class Application:
    """
    Handles a single managed application. self.set_locations must be used
    before any other method.
    """
    
    def __init__(self, name):
        self.name = name
        self.locations = []
        self.desktop_path = ""
        self.full_name = ""
        self.icon_name = ""
        self.icon = None
        self.data_size = 0
        self.exec_name = ""
        self.snapshots = {}
        self.running = False
        self._app_snapshot_dir = os.path.join(MOUND_SNAPSHOTS, self.name)
        self.errors = []
    
    def __repr__(self):
        return "%s: %s" % (self.name, self.full_name)
    
    @property
    def app_snapshot_dir(self):
        """
        Check/create the app snapshot directory when we need it.
        """
        if not os.path.isdir(self._app_snapshot_dir):
            os.makedirs(self._app_snapshot_dir)
        return self._app_snapshot_dir
    
    def set_locations(self, locations):
        """
        Check and set a list of user data locations for this application.
        """
        self.locations = []
        for loc in locations:
            # substitute in XDG locations
            loc = loc.replace('$DATA', XDGDATA)
            loc = loc.replace('$CONFIG', XDGCONFIG)
            loc = loc.replace('$CACHE', XDGCACHE)
            # set absolute pathnames
            loc = os.path.expanduser(loc)
            # we only allow locations in the home directory
            if loc.find(USER_HOME) != 0:
                raise LocationError(self, _("Location is not in home directory"))
            # prevent crucial directories from being managed
            for restriction in RESTRICTED:
                if os.path.normpath(loc) == os.path.normpath(os.path.expanduser(restriction)):
                    raise LocationError(self, _("Cannot manage restricted location"))
            self.locations.append(loc)

    def load_icon(self):
        """
        Try to load the icon for this application from the icon theme.
        If that fails, try loading from the pixmaps directory.
        And if that fails, use a default "unknown" icon.
        """
        try:
            assert self.icon_name
            try:
                self.icon = ICON_THEME_DEFAULT.load_icon(self.icon_name, 32, 0)
            except:
                if '/' not in self.icon_name:
                    self.icon_name = '/usr/share/pixmaps/' + self.icon_name
                self.icon = gtk.gdk.pixbuf_new_from_file(self.icon_name)
                self.icon = self.icon.scale_simple(32, 32, gtk.gdk.INTERP_BILINEAR)
        except:
            self.icon_name = None
            self.icon = ICON_UNKNOWN

    def calculate_size(self, force=False):
        """
        Try to calculate the size of the application's user data.
        Cache the result unless force is True.
        """
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
        """
        Check the system to see if the application is currently running.
        Not foolproof, but can stop many oopses.
        """
        for root, dirs, files in os.walk('/proc'):
            for d in dirs:
                try:
                    pid = int(d)
                    f = open('/proc/%d/cmdline' % pid, 'r')
                except:
                    continue
                exec_path = f.read().split('\x00')[0]
                f.close()
                exec_name = os.path.basename(exec_path)
                if self.exec_name == exec_name:
                    self.running = True
                    return True
            break # we only want toplevel, so only itereate once
        self.running = False
        return False

    def delete_data(self):
        """
        Delete the user data for the application. Use with caution!
        """
        for loc in self.locations:
            if os.path.isdir(loc):
                rmtree(loc)
            elif os.path.exists(loc):
                os.remove(loc)

    def load_snapshots(self, force=False):
        """
        Read the list of snapshots from the application snapshot directory.
        """
        if self.snapshots and not force:
            return
        self.snapshots = {}
        ss_dir = os.path.join(MOUND_SNAPSHOTS, self.name)
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
        """
        Take a new snapshot using tar and store it in the snapshots
        directory.
        """
        snap_filename = os.path.join(self.app_snapshot_dir, '%s.snapshot.tar.gz' % snapshot_name)
        cmd = ['tar', '-cvzf',
            snap_filename,
            '-C', USER_HOME
        ]
        for loc in self.locations:
            # make sure path exists
            if not os.path.exists(loc):
                continue
            # strip off the home directory for tar
            loc = loc.replace(USER_HOME + '/', '')
            cmd.append(loc)
        print "#", ' '.join(cmd)
        p = Popen(cmd)
        returncode = p.wait()
        assert returncode == 0
        self.load_snapshots(force=True)

    def revert_to_snapshot(self, snapshot_name):
        """
        Revert a snapshot from the snapshots directory. Use with caution!
        """
        if not os.path.exists(self.snapshots[snapshot_name][0]):
            return
        cmd = ['tar', '-xvz', '-C', USER_HOME,
            '-f', self.snapshots[snapshot_name][0],
        ]
        print "#", ' '.join(cmd)
        p = Popen(cmd)
        returncode = p.wait()
        assert returncode == 0

    def delete_snapshot(self, snapshot_name):
        """
        Delete a snapshot.
        """
        snap_filename = self.snapshots[snapshot_name][0]
        os.remove(snap_filename)

    def export_snapshot(self, snapshot_name, export_location):
        """
        Export a snapshot with a custom gzip header.
        """
        snap_filename = self.snapshots[snapshot_name][0]
        orig = open(snap_filename, 'rb')
        # sanity check
        header = orig.read(10)
        if header[3] != '\x00':
            raise SnapshotError(self, _("Bad source snapshot"))
        # open the export
        export = open(export_location, 'wb')
        # write the gzip header with the FCOMMENT flag
        export.write(header[:3] + '\x10' + header[4:])
        # begin writing metadata
        export.write('MOUNDSNAPSHOT\n%s\n%s' % (self.name, snapshot_name))
        # end of metadata
        export.write('\x00')
        # write the rest of the snapshot
        while True:
            buf = orig.read(4096)
            if not buf: break
            export.write(buf)
        export.close()
        orig.close()

    def import_snapshot(self, import_location):
        """
        Import a snapshot, using checks to make sure it is valid for this
        application. We need a valid MOUNDSNAPSHOT FCOMMENT header,
        the application contained in the header needs to match, and
        the header needs to define a snapshot name.
        We then write it to the snapshot directory in a reverse fashion
        of self.export_snapshot, saving it without the FCOMMENT header.
        """
        snap = open(import_location, 'rb')
        # check the gzip flag
        header = snap.read(10)
        if header[3] != '\x10':
            snap.close()
            raise SnapshotError(self, _("Not a Mound snapshot"))
        # read the FCOMMENT header, one byte at a time
        fcomment = ""
        while True:
            byte = snap.read(1)
            if not byte or byte == '\x00':
                break
            fcomment += byte
        # extract and check the metadata
        meta = fcomment.split('\n')
        if len(meta) != 3 or meta[0] != 'MOUNDSNAPSHOT':
            snap.close()
            raise SnapshotError(self, _("Not a Mound snapshot"))
        if meta[1] != self.name:
            snap.close()
            raise SnapshotError(self, _("Snapshot does not match application"))
        if meta[2] in self.snapshots.keys():
            snap.close()
            raise SnapshotError(self, _("Snapshot already exists"))
        # all valid, write it to the snapshot location
        final_fn = os.path.join(self.app_snapshot_dir, '%s.snapshot.tar.gz' % meta[2])
        final = open(final_fn, 'wb')
        # reset the flag & write the header
        final.write(header[:3] + '\x00' + header[4:])
        # write the rest of the snapshot out into the new file
        # snap should already have the read pointer set correctly
        while True:
            buf = snap.read(4096)
            if not buf: break
            final.write(buf)
        snap.close()
        final.close()
        self.load_snapshots(force=True)

