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

import gtk
import re
import datetime
from subprocess import Popen
from Mound.util import format_size

RX_SNAPSHOT_NAME = re.compile('^[\w\-\s]+$')

class DetailsUI:
    """
    The UI for the Details window.
    
    Takes a Mound instance like MainUI, as well as MainUI's GtkBuilder
    instance. Similar to SnapshotsUI.
    """

    def __init__(self, mound_inst, builder):
        self.mound = mound_inst
        self.builder = builder

        load = [
            'dlg_details',
            'directories_treeview',
            'lst_directories',
            'btn_open_external',
            'btn_baobab',
            'lbl_app_information',
        ]
        for item in load:
            self.__dict__[item] = self.builder.get_object(item)

        self.dlg_details.connect('response', lambda s, r: s.hide())
        self.directories_treeview_sel = self.directories_treeview.get_selection()
        self.btn_open_external.connect('clicked', self.open_directory_external)
        self.btn_baobab.connect('clicked', self.open_baobab)
        self.lbl_app_information.connect('activate-link', self.open_snapshots_external)
        
    def show_details(self, selected_app=None):
        """
        Show the details dialog for the selected application.
        """
        if selected_app:
            self.selected_app = selected_app
        self.update_ui()
        self.dlg_details.run()
    
    def open_directory_external(self, source=None):
        pass
    
    def open_baobab(self, source=None):
        pass
    
    def open_snapshots_external(self, *args):
        """
        Open the snapshot directory in a file browser.
        """
        Popen(['xdg-open', self.selected_app.app_snapshot_dir])
        return True
    
    def update_ui(self, source=None):
        """
        Update the information displayed.
        """
        if self.selected_app.errors:
            txt = "This application cannot be managed because of the following problems:\n"
            for error in self.selected_app.errors:
                txt += error.msg + "\n"
        else:
            txt = "%s was loaded from:\n  %s\n\n" % (self.selected_app.full_name, self.selected_app.desktop_path)
            txt += "Snapshots are stored in:\n<a href='%(snapdir)s'>%(snapdir)s</a>" % {'snapdir': self.selected_app.app_snapshot_dir}
        self.lbl_app_information.props.label = txt
