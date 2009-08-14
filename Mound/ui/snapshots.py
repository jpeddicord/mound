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
from Mound.util import format_size

RX_SNAPSHOT_NAME = re.compile('^[\w\-\s]+$')

class SnapshotsUI:

    def __init__(self, mound_inst, builder):
        self.mound = mound_inst
        self.builder = builder
        
        load = [
            'win_snapshots',
            'lbl_snapshots_info',
            'lst_snapshots',
            'snapshots_treeview',
            'btn_snapshots_close',
            'tb_snap_new',
            'tb_snap_revert',
            'tb_snap_delete',
            'tb_snap_import',
            'tb_snap_export',
            'dlg_new_snapshot',
            'entry_snapshot_name',
        ]
        for item in load:
            self.__dict__[item] = self.builder.get_object(item)
        
        self.win_snapshots.connect('delete-event', gtk.Widget.hide_on_delete)
        self.snapshots_treeview_sel = self.snapshots_treeview.get_selection()
        self.snapshots_treeview.connect('cursor-changed', self.update_ui)
        self.btn_snapshots_close.connect('clicked',
                lambda s: self.win_snapshots.hide())
        
        self.tb_snap_new.connect('clicked', self.new_snapshot_ui)
        self.tb_snap_delete.connect('clicked', self.delete_selected_snapshot)
        self.tb_snap_revert.connect('clicked', self.revert_to_selected)
        
        self.dlg_new_snapshot.connect('response', self.new_snapshot_ui_response)
        self.dlg_new_snapshot.set_default_response(gtk.RESPONSE_OK)
    
    def show_snapshots(self, selected_app=None):
        if selected_app:
            self.selected_app = selected_app
        def snap_cmp(arg1, arg2):
            return cmp(self.selected_app.snapshots[arg1][1],
                       self.selected_app.snapshots[arg2][1])
        self.selected_app.load_snapshots()
        self.lst_snapshots.clear()
        # sort by most recent
        sorted_keys = sorted(self.selected_app.snapshots, cmp=snap_cmp, reverse=True)
        for snapshot in sorted_keys:
            snap_date = datetime.datetime.fromtimestamp(
                    self.selected_app.snapshots[snapshot][1]).strftime(
                            "%Y-%m-%d %H:%M:%S")
            snap_size = format_size(self.selected_app.snapshots[snapshot][2])
            self.lst_snapshots.append((
                snapshot,
                snap_date,
                snap_size,
            ))
        self.tb_snap_revert.props.sensitive = False
        self.tb_snap_delete.props.sensitive = False
        self.tb_snap_export.props.sensitive = False
        self.win_snapshots.props.title = "Snapshots of %s" % self.selected_app.full_name
        self.win_snapshots.show_all()
    
    def new_snapshot_ui(self, source):
        self.entry_snapshot_name.props.text = ""
        self.entry_snapshot_name.grab_focus()
        self.dlg_new_snapshot.run()
    
    def new_snapshot_ui_response(self, source, response):
        if response == gtk.RESPONSE_OK:
            if not RX_SNAPSHOT_NAME.match(self.entry_snapshot_name.props.text):
                dlg_error = gtk.MessageDialog(self.dlg_new_snapshot, 0,
                        gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                        "The snapshot name may only consist of letters, numbers, spaces, underscores, and dashes.")
                dlg_error.run()
                dlg_error.destroy()
                return
            # create a snapshot
            self.selected_app.take_snapshot(self.entry_snapshot_name.props.text)
            self.show_snapshots()
        self.dlg_new_snapshot.hide()
    
    def delete_selected_snapshot(self, source=None):
        def response(src, resp):
            if resp == gtk.RESPONSE_OK:
                self.selected_app.delete_snapshot(self.selected_snapshot_name)
                self.selected_app.load_snapshots(force=True)
                self.show_snapshots()
        dlg_confirm = gtk.MessageDialog(self.win_snapshots, 0,
                gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL)
        dlg_confirm.set_markup("Are you sure you want to delete the \"<b>%s</b>\" snapshot?\n\n<i>This will not delete any data %s currently uses.</i>" % (self.selected_snapshot_name, self.selected_app.full_name))
        dlg_confirm.connect('response', response)
        dlg_confirm.run()
        dlg_confirm.destroy()
        # see the response function a few lines above for the rest
    
    def revert_to_selected(self, source=None):
        def response(src, resp):
            if resp == gtk.RESPONSE_OK:
                self.selected_app.revert_to_snapshot(self.selected_snapshot_name)
                dlg_success = gtk.MessageDialog(self.win_snapshots, 0,
                        gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE,
                        "Successfully reverted %s to the \"%s\" snapshot." % (
                            self.selected_app.full_name,
                            self.selected_snapshot_name
                        ))
                dlg_success.run()
                dlg_success.destroy()
                self.win_snapshots.hide()
        dlg_confirm = gtk.MessageDialog(self.win_snapshots, 0,
                gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL)
        dlg_confirm.set_markup("<i>You may want to take a snapshot before reverting.</i>\n\nDo you want to revert to the \"<b>%s</b>\" snapshot?" % self.selected_snapshot_name)
        dlg_confirm.connect('response', response)
        dlg_confirm.run()
        dlg_confirm.destroy()
        
    def update_ui(self, source=None):
        model, ti = self.snapshots_treeview_sel.get_selected()
        if not ti:
            self.tb_snap_revert.props.sensitive = False
            self.tb_snap_delete.props.sensitive = False
            self.tb_snap_export.props.sensitive = False
            return
        self.selected_snapshot_name = self.lst_snapshots.get_value(ti, 0)
        self.tb_snap_revert.props.sensitive = True
        self.tb_snap_delete.props.sensitive = True
        self.tb_snap_export.props.sensitive = True
