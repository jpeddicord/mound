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

from math import ceil
import gtk
from Mound.util import format_size
from Mound.ui.snapshots import SnapshotsUI

class MainUI:
    
    selected_app = None
    
    def __init__(self, mound_inst):
        self.mound = mound_inst
        self.builder = gtk.Builder()
        try:
            self.builder.add_from_file('mound.ui')
        except:
            self.builder.add_from_file('/usr/share/mound/mound.ui')
        
        # widgets to load
        load = [
            'win_main',
            'lst_applications',
            'apps_iconview',
            'img_appicon',
            'lbl_title',
            'lbl_app_details',
            'btn_snapshots',
            'btn_delete',
        ]
        for item in load:
            self.__dict__[item] = self.builder.get_object(item)
        
        self.snapshots_ui = SnapshotsUI(mound_inst, self.builder)
        
        # signals
        self.apps_iconview.connect('selection-changed', self.update_ui)
        self.btn_snapshots.connect('clicked',
                lambda s: self.snapshots_ui.show_snapshots(self.selected_app))
        
        self.update_ui()
        
        self.win_main.connect('destroy', gtk.main_quit)
        self.win_main.show_all()
    
    def load_applications(self):
        for appname in self.mound.applications:
            self.lst_applications.append((
                self.mound.applications[appname].name,
                self.mound.applications[appname].full_name,
                self.mound.applications[appname].icon
            ))
        # force a 4-row widget
        self.apps_iconview.props.columns = ceil(float(len(self.mound.applications)) / 4)
        
    def update_ui(self, source=None):
        selection = self.apps_iconview.get_selected_items()
        if selection:
            # find the selected application
            selection = selection[0]
            selection_iter = self.lst_applications.get_iter(selection)
            selected = self.lst_applications.get_value(selection_iter, 0)
            app = self.selected_app = self.mound.applications[selected]
            # check if it's running
            sensitive = self.selected_app.check_running() == False
            txt = ""
            if not sensitive:
                txt = "<b>Please close %s before managing it.</b>\n\n" % self.selected_app.full_name
            # grab the size
            app.calculate_size()
            if app.data_size > 0:
                size = format_size(app.data_size)
                txt += "<i>This application is using <b>" + size + "</b> of space.</i>"
            else:
                txt += "<i>This application is not storing any data.</i>"
            self.lbl_app_details.props.label = txt
            self.lbl_title.props.label = "<span font='Sans Bold 14'>%s</span>" % app.full_name
            self.img_appicon.set_from_pixbuf(app.icon)
            self.btn_snapshots.props.sensitive = sensitive
            self.btn_delete.props.sensitive = sensitive
        else:
            self.selected_app = None
            self.lbl_app_details.props.label = ""
            self.lbl_title.props.label = "<span font='Sans Bold 14'>Select an Application</span>";
            self.img_appicon.set_from_stock('gtk-dialog-question', gtk.ICON_SIZE_DND);
            self.btn_snapshots.props.sensitive = False
            self.btn_delete.props.sensitive = False