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
import locale

try:
    import xdg.BaseDirectory
    XDGDATA = xdg.BaseDirectory.xdg_data_home
    XDGCONFIG = xdg.BaseDirectory.xdg_config_home
    XDGCACHE = xdg.BaseDirectory.xdg_cache_home
    XDGDATADIRS = xdg.BaseDirectory.xdg_data_dirs
except:
    XDGDATA = os.path.expanduser('~/.local/share')
    XDGCONFIG = os.path.expanduser('~/.config')
    XDGCACHE = os.path.expanduser('~/.cache')
    XDGDATADIRS = [XDGDATA, '/usr/local/share', '/usr/share']

LANG_FULL = locale.getdefaultlocale()[0]
LANG_SHORT = LANG_FULL[:2]

def format_size(size):
    """Format a size (bytes) into something more readable."""
    size = float(size)
    if size > 1024*1024:
        return "%0.1f MB" % (size / 1024 / 1024)
    elif size > 1024:
        return "%0.1f KB" % (size / 1024)
    else:
        # bytes aren't a friendly unit, use more precision instead
        return "%0.2f KB" % (size / 1024)
