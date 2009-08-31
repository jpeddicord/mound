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
    """
    Main window UI procedures.
    
    Takes an instance of Mound, which is used to load applications.
    """

    selected_app = None

    def __init__(self, mound_inst):
        self.mound = mound_inst
        self.builder = gtk.Builder()
        try:
            self.builder.add_from_file('mound.ui')
        except:
            self.builder.add_from_file('/usr/share/mound-data-manager/mound.ui')

        gtk.window_set_default_icon_name('mound-data-manager')

        # widgets to load
        load = [
            'win_main',
            'item_quit',
            'item_about',
            'dlg_about',
            'apps_scroll',
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
        self.item_quit.connect('activate', gtk.main_quit)
        self.item_about.connect('activate',
                lambda s: self.dlg_about.run())
        self.dlg_about.connect('response',
                lambda s, r: s.hide())
        
        try:
            from Mound.info import version
            self.dlg_about.set_version(version)
        except: pass
        
        self.apps_scroll.connect('scroll-event', self.handle_scroll)
        self.apps_iconview.connect('selection-changed', self.update_ui)
        self.btn_snapshots.connect('clicked',
                lambda s: self.snapshots_ui.show_snapshots(self.selected_app))
        self.btn_delete.connect('clicked', self.delete_application_data)

        self.update_ui()

        self.win_main.connect('focus-in-event', self.update_ui)
        self.win_main.connect('destroy', gtk.main_quit)
        self.win_main.show_all()

    def load_applications(self):
        """
        Load the applications from the Mound instance and add them to our
        display.
        """
        for app in self.mound.applications_lst:
            self.lst_applications.append((app.name, app.full_name, app.icon))
        # force a 5-row widget
        self.apps_iconview.props.columns = ceil(float(len(self.mound.applications)) / 5)

    def delete_application_data(self, source=None):
        """
        Trigger a dialog to delete data for an application. The user is
        prompted to take a snapshot beforehand.
        """
        def response(src, resp):
            if resp == gtk.RESPONSE_OK:
                self.selected_app.delete_data()
                self.selected_app.calculate_size(force=True)
                self.update_ui()
            elif resp == 10:
                src.hide()
                self.snapshots_ui.show_snapshots(self.selected_app)
                self.snapshots_ui.new_snapshot_ui()
        dlg_confirm = gtk.MessageDialog(self.win_main, 0, gtk.MESSAGE_WARNING)
        dlg_confirm.set_markup("<i>You may want to take a snapshot before continuing.</i>\n\nAre you sure you want to destroy all data, settings, and preferences for <b>%s</b>?" % self.selected_app.full_name)
        dlg_confirm.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        dlg_confirm.add_button("Take Snapshot", 10)
        dlg_confirm.add_button(gtk.STOCK_DELETE, gtk.RESPONSE_OK)
        dlg_confirm.connect('response', response)
        dlg_confirm.run()
        dlg_confirm.destroy()
    
    def handle_scroll(self, widget, scroll):
        """
        Allow scrolling horizontally with the mouse wheel, since there is
        no vertical scrolling.
        """
        adjustment = widget.get_hadjustment()
        if scroll.direction == gtk.gdk.SCROLL_UP:
            adjustment.props.value -= adjustment.props.step_increment * 1.5
        elif scroll.direction == gtk.gdk.SCROLL_DOWN:
            adjustment.props.value += adjustment.props.step_increment * 1.5
        # set limits so the GTK scrollbar doesn't commit suicide
        max_value = adjustment.props.upper - adjustment.props.page_size
        if adjustment.props.value > max_value:
            adjustment.props.value = max_value
        elif adjustment.props.value < adjustment.props.lower:
            adjustment.props.value = adjustment.props.lower
    
    def update_ui(self, *args, **kwargs):
        """
        Update the bottom panel with information about the selected
        application. Disable certain buttons if their features are not
        available for use on the application.
        """
        selection = self.apps_iconview.get_selected_items()
        if selection:
            # find the selected application
            selection = selection[0]
            selection_iter = self.lst_applications.get_iter(selection)
            selected = self.lst_applications.get_value(selection_iter, 0)
            app = self.selected_app = self.mound.applications[selected]
            # update the title & icon
            self.lbl_title.props.label = "<span font='Sans Bold 14'>%s</span>" % app.full_name
            self.img_appicon.set_from_pixbuf(app.icon)
            # check if it's running
            running = self.selected_app.check_running()
            txt = []
            if running:
                txt.append("<b>Please close %s before managing it.</b>" % self.selected_app.full_name)
                self.btn_snapshots.props.sensitive = False
                self.btn_delete.props.sensitive = False
            else:
                self.btn_snapshots.props.sensitive = True
                self.btn_delete.props.sensitive = True
            # grab the size
            app.calculate_size()
            if app.data_size > 0:
                size = format_size(app.data_size)
                txt.append("<i>This application is using <b>" + size + "</b> of space.</i>")
            else:
                txt.append("<i>This application is not storing any data.</i>")
                self.btn_delete.props.sensitive = False
            # check for errors
            if app.errors:
                txt = ["<b>A problem occurred. This application cannot be managed.</b>"]
                self.btn_snapshots.props.sensitive = False
                self.btn_delete.props.sensitive = False
            self.lbl_app_details.props.label = "\n\n".join(txt)
        else:
            self.selected_app = None
            self.lbl_app_details.props.label = ""
            self.lbl_title.props.label = "<span font='Sans Bold 14'>Select an Application</span>";
            self.img_appicon.set_from_stock('gtk-dialog-question', gtk.ICON_SIZE_DND);
            self.btn_snapshots.props.sensitive = False
            self.btn_delete.props.sensitive = False
