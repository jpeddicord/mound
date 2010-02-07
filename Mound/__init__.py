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
from optparse import OptionParser


try:
    from Mound.info import version
except:
    version = None

def run_cli():
    """
    Parse the command-line options given and do what we're told.
    """
    
    p = OptionParser(usage="%prog [action [options]] [application]", version=version)
    
    p.add_option('--list-applications',
        action='store_true', dest='list_applications', default=False,
        help=_("List applications that have valid userdata."))
    p.add_option('--take-snapshot', metavar='FILENAME',
        action='store', type='string', dest='take_snapshot',
        help=_("Take a snapshot of an application."))
    p.add_option('--revert-snapshot', metavar='FILENAME',
        action='store', type='string', dest='revert_snapshot',
        help=_("Load a snapshot from a file and revert to it."))
    p.add_option('--delete-data',
        action='store_true', dest='delete_data', default=False,
        help=_("Delete data for an application."))

    (opts, args) = p.parse_args()

    optsum = 0
    for opt in ['list_applications', 'take_snapshot', 'revert_snapshot', 'delete_data']:
        if opts.__dict__[opt]:
            optsum += 1

    if optsum > 1:
        p.error(_("Only one action may be used at a time."))
    # if there were no parsable options, there's probably just an appname
    elif optsum == 0:
        # load the gui
        import gtk
        from Mound.userdata import UserData
        from Mound.ui import MainUI
        ud = UserData()
        ud.load_defaults()
        ud.load_applications()
        ui = MainUI(ud, args[0])
        ui.load_applications()
        gtk.main()
        return

    # we _could_ use callbacks instead, but we also only want one option
    # to run at a time.
    if opts.list_applications:
        from Mound.userdata import UserData
        ud = UserData()
        ud.load_defaults()
        ud.load_applications()
        for app in ud.applications:
            print ud.applications[app].name, ';'.join(ud.applications[app].locations)
    
    elif opts.take_snapshot:
        pass
    
    elif opts.revert_snapshot:
        pass
    
    elif opts.delete_data:
        pass
    
