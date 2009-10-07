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

import re
import datetime
import gobject
import gtk
from Mound.util import format_size

RX_SNAPSHOT_NAME = re.compile('^[\w\-\s]+$')

class SnapshotsUI:
    """
    The UI for the Snapshots window.
    
    Takes a Mound instance like MainUI, as well as MainUI's GtkBuilder
    instance.
    """

    def __init__(self, mound_inst, builder):
        self.mound = mound_inst
        self.builder = builder

        load = [
            'win_main',
            'lbl_snapshots_info',
            'lst_snapshots',
            'snapshots_treeview',
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

        self.snapshots_treeview_sel = self.snapshots_treeview.get_selection()
        self.snapshots_treeview.connect('cursor-changed', self.update_ui)

        self.tb_snap_new.connect('clicked', self.new_snapshot_ui)
        self.tb_snap_delete.connect('clicked', self.delete_selected_snapshot)
        self.tb_snap_revert.connect('clicked', self.revert_to_selected)
        self.tb_snap_import.connect('clicked', self.import_snapshot)
        self.tb_snap_export.connect('clicked', self.export_selected_snapshot)

        self.dlg_new_snapshot.connect('response', self.new_snapshot_ui_response)
        self.dlg_new_snapshot.set_default_response(gtk.RESPONSE_OK)

    def show_snapshots(self, selected_app=False):
        """
        Show and update the snapshots window.
        Can be called while already open to update the UI.
        """
        if selected_app != False:
            self.selected_app = selected_app
        if self.selected_app:
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
        else:
            self.lst_snapshots.clear()
        self.update_ui()

    def new_snapshot_ui(self, source=None):
        """
        Show a dialog prompting for a snapshot name. Default to the current
        date/time.
        """
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H%M")
        self.entry_snapshot_name.props.text = dt
        self.entry_snapshot_name.grab_focus()
        self.dlg_new_snapshot.run()

    def new_snapshot_ui_response(self, source, response):
        """
        Handle the "new snapshot" dialog. (See self.new_snapshot_ui)
        Prevents invalid snapshot names. Takes a snapshot once valid.
        """
        if response == gtk.RESPONSE_OK:
            snap_name = self.entry_snapshot_name.props.text
            # check for valid name
            if not RX_SNAPSHOT_NAME.match(snap_name):
                dlg_error = gtk.MessageDialog(self.dlg_new_snapshot, 0,
                        gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                        _("The snapshot name may only consist of letters, numbers, spaces, underscores, and dashes."))
                dlg_error.run()
                dlg_error.destroy()
                return
            # duplicates not allowed
            if snap_name in self.selected_app.snapshots.keys():
                dlg_error = gtk.MessageDialog(self.dlg_new_snapshot, 0,
                        gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                        _("This snapshot already exists."))
                dlg_error.run()
                dlg_error.destroy()
                return
            # disable the interface & change to busy cursor
            watch = gtk.gdk.Cursor(gtk.gdk.WATCH)
            self.dlg_new_snapshot.get_window().set_cursor(watch)
            for c in self.dlg_new_snapshot.get_children():
                c.props.sensitive = False
            gobject.idle_add(self.new_snapshot_cb, snap_name)
        else:
            self.dlg_new_snapshot.hide()
    
    def new_snapshot_cb(self, snap_name):
        """
        Create a snapshot in an idle callback, and re-enable the interface
        when finished.
        """
        self.selected_app.take_snapshot(snap_name)
        self.dlg_new_snapshot.get_window().set_cursor(None)
        for c in self.dlg_new_snapshot.get_children():
            c.props.sensitive = True
        self.show_snapshots()
        self.dlg_new_snapshot.hide()

    def delete_selected_snapshot(self, source=None):
        """
        As described: delete the currently selected snapshot.
        Present a confirmation dialog "just in case."
        """
        dlg_confirm = gtk.MessageDialog(self.win_main, 0,
                gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL)
        dlg_confirm.set_markup(
            _("Are you sure you want to delete the \"%s\" snapshot?") \
                % ("<b>%s</b>" % self.selected_snapshot_name) +
            "\n\n<i>" +
            _("This will not delete any data %s currently uses.") \
                % self.selected_app.full_name + "</i>"
        )
        if dlg_confirm.run() == gtk.RESPONSE_OK:
            self.selected_app.delete_snapshot(self.selected_snapshot_name)
            self.selected_app.load_snapshots(force=True)
            self.show_snapshots()
        dlg_confirm.destroy()

    def revert_to_selected(self, source=None):
        """
        Prompt the user to revert to the selected snapshot, giving an
        option to take another snapshot just to be safe.
        """
        dlg_confirm = gtk.MessageDialog(self.win_main, 0, gtk.MESSAGE_WARNING)
        dlg_confirm.set_markup(
            "<i>" + _("You may want to take a snapshot before reverting.") +
            "</i>\n\n" +
            _("Do you want to revert to the \"%s\" snapshot?") % \
                ("<b>%s</b>" % self.selected_snapshot_name)
        )
        dlg_confirm.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        dlg_confirm.add_button(_("Take Snapshot"), 10)
        dlg_confirm.add_button(gtk.STOCK_REVERT_TO_SAVED, gtk.RESPONSE_OK)
        response = dlg_confirm.run()
        if response == gtk.RESPONSE_OK:
            # disable the interface & change to busy cursor
            watch = gtk.gdk.Cursor(gtk.gdk.WATCH)
            dlg_confirm.get_window().set_cursor(watch)
            for c in dlg_confirm.get_children():
                c.props.sensitive = False
            gobject.idle_add(self.revert_to_selected_cb, dlg_confirm,
                             self.selected_snapshot_name)
            return
        elif response == 10:
            dlg_confirm.hide()
            self.new_snapshot_ui()
        dlg_confirm.destroy()
    
    def revert_to_selected_cb(self, dlg_confirm, snap_name):
        """
        Revert to the snapshot in an idle callback. We don't need to unlock
        the dialog here because we destroy it anyway.
        """
        self.selected_app.revert_to_snapshot(snap_name)
        dlg_success = gtk.MessageDialog(dlg_confirm, 0,
                gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE,
                _("Successfully reverted %s to the \"%s\" snapshot.") % (
                    self.selected_app.full_name,
                    self.selected_snapshot_name
                ))
        dlg_success.run()
        dlg_success.destroy()
        dlg_confirm.destroy()
    
    def import_snapshot(self, source=None):
        """
        Ask for a snapshot to import. Check it & extract it.
        """
        dlg_import = gtk.FileChooserDialog(_("Open Snapshot"), self.win_main,
                gtk.FILE_CHOOSER_ACTION_OPEN, (
                    gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                    gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT,
                ))
        ff = gtk.FileFilter()
        ff.set_name(_("Mound Snapshots") + " (*.mtgz)")
        ff.add_pattern('*.mtgz')
        ff.add_pattern('*.tar.gz')
        dlg_import.add_filter(ff)
        def response(s, r):
            if r != gtk.RESPONSE_ACCEPT:
                return
            try:
                self.selected_app.import_snapshot(dlg_import.get_filename())
            except Exception, e:
                error = "A problem occurred. This snapshot cannot be used."
                if getattr(e, 'msg', False):
                    error += "\n\nError:\n" + e.msg
                dlg_error = gtk.MessageDialog(self.dlg_new_snapshot, 0,
                        gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, error)
                dlg_error.run()
                dlg_error.destroy()
        dlg_import.connect('response', response)
        dlg_import.run()
        dlg_import.destroy()
    
    def export_selected_snapshot(self, source=None):
        """
        Present a dialog allowing the user to export a snapshot.
        """
        # ask for a filename
        dlg_export = gtk.FileChooserDialog("Save Snapshot As", self.win_main,
                gtk.FILE_CHOOSER_ACTION_SAVE, (
                    gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                    gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT,
                ))
        dlg_export.props.do_overwrite_confirmation = True
        ff = gtk.FileFilter()
        ff.set_name("Mound Snapshots (*.mtgz)")
        ff.add_pattern('*.mtgz')
        ff.add_pattern('*.tar.gz')
        dlg_export.add_filter(ff)
        dlg_export.set_current_name("%s.mtgz" % self.selected_snapshot_name)
        if dlg_export.run() == gtk.RESPONSE_ACCEPT:
            # run the export
            self.selected_app.export_snapshot(self.selected_snapshot_name,
                                              dlg_export.get_filename())
        dlg_export.destroy()

    def update_ui(self, source=None):
        """
        Set the sensitivity of toolbar items depending on the snapshot
        selected. Disable the interface if the application has errors,
        or if nothing is selected.
        """
        if not self.selected_app or self.selected_app.errors or self.selected_app.running:
            self.snapshots_treeview.props.sensitive = False
            self.tb_snap_new.props.sensitive = False
            self.tb_snap_revert.props.sensitive = False
            self.tb_snap_delete.props.sensitive = False
            self.tb_snap_import.props.sensitive = False
            self.tb_snap_export.props.sensitive = False
            return
        else:
            self.snapshots_treeview.props.sensitive = True
            self.tb_snap_import.props.sensitive = True
        self.tb_snap_new.props.sensitive = (self.selected_app.data_size > 0)
        model, ti = self.snapshots_treeview_sel.get_selected()
        if not ti:
            self.tb_snap_revert.props.sensitive = False
            self.tb_snap_delete.props.sensitive = False
            self.tb_snap_export.props.sensitive = False
        else:
            self.selected_snapshot_name = self.lst_snapshots.get_value(ti, 0)
            self.tb_snap_revert.props.sensitive = True
            self.tb_snap_delete.props.sensitive = True
            self.tb_snap_export.props.sensitive = True

