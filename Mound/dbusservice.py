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

import dbus.service


class MoundService(dbus.service.Object):

    def load_userdata(self):
        from Mound.userdata import UserData
        self.ud = UserData()
        self.ud.load_defaults()
        self.ud.load_applications()
    
    @dbus.service.method('org.mound', out_signature='a{sas}')
    def ListApplications(self):
        result = {}
        for app in self.ud.applications:
            result[app] = self.ud.applications[app].locations
        return result
    
