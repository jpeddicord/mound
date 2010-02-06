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

class DetailsUI:
    """
    The UI for the Details window.
    
    Takes a Mound instance like MainUI, as well as MainUI's GtkBuilder
    instance. Similar to SnapshotsUI.
    """

    def __init__(self, builder):
        self.builder = builder

        load = [
            'dlg_details',
            'locations_treeview',
            'lst_locations',
            'btn_open_external',
            'btn_baobab',
            'lbl_app_information',
        ]
        for item in load:
            self.__dict__[item] = self.builder.get_object(item)

        self.dlg_details.connect('response', lambda s, r: s.hide())
        self.locations_treeview_sel = self.locations_treeview.get_selection()
        self.locations_treeview.connect('cursor-changed', self.update_ui)
        self.btn_open_external.connect('clicked', self.open_directory_external)
        self.btn_baobab.connect('clicked', self.open_baobab)
        # only available in gtk+ 2.18 and up
        try:
            self.lbl_app_information.connect('activate-link', self.open_snapshots_external)
            self.no_links = False
        except:
            self.no_links = True
        
        # cheap check
        if not os.path.exists("/usr/bin/baobab"):
            self.btn_baobab.props.visible = False
        
    def show_details(self, selected_app=None):
        """
        Show the details dialog for the selected application.
        """
        if selected_app:
            self.selected_app = selected_app
        self.lst_locations.clear()
        for l in self.selected_app.locations:
            self.lst_locations.append((l,))
        self.update_ui()
        self.dlg_details.run()
    
    def open_directory_external(self, source=None):
        Popen(['xdg-open', self.selected_location])
    
    def open_baobab(self, source=None):
        Popen(['baobab', self.selected_location])
        return True  # needed to prevent default GTK+ handler
    
    def open_snapshots_external(self, *args):
        """
        Open the snapshot directory in a file browser.
        """
        Popen(['xdg-open', self.selected_app.app_snapshot_dir])
        return True  # needed to prevent default GTK+ handler
    
    def update_ui(self, source=None):
        """
        Update the information displayed, along with button sensitivity.
        """
        model, ti = self.locations_treeview_sel.get_selected()
        if ti:
            self.selected_location = self.lst_locations.get_value(ti, 0)
        # data display
        if ti and os.path.isdir(self.selected_location):
            self.btn_open_external.props.sensitive = True
            self.btn_baobab.props.sensitive = True
        else:
            self.btn_open_external.props.sensitive = False
            self.btn_baobab.props.sensitive = False
        # information
        if self.selected_app.errors:
            txt = _("This application cannot be managed because of the following problems:") + "\n"
            for error in self.selected_app.errors:
                txt += error.msg + "\n"
        else:
            txt = _("%(application)s was loaded from:") % {'application': self.selected_app.full_name}
            txt += "\n  " + self.selected_app.desktop_path + "\n\n"
            if self.no_links:
                txt += _("Snapshots are stored in:") + "\n  %s" % self.selected_app.app_snapshot_dir
            else:
                txt += _("Snapshots are stored in:") + "\n  <a href='%(snapdir)s'>%(snapdir)s</a>" % {'snapdir': self.selected_app.app_snapshot_dir}
        self.lbl_app_information.props.label = txt
