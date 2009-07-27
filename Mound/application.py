

import os
import gtk

try:
    import xdg
    XDGDATA = xdg.xdg_data_home
    XDGCONFIG = xdg.xdg_config_home
    XDGCACHE = xdg.xdg_cache_home
except:
    XDGDATA = os.path.expanduser("~/.local/share")
    XDGCONFIG = os.path.expanduser("~/.config")
    XDGCACHE = os.path.expanduser("~/.cache")

icon_theme_default = gtk.icon_theme_get_default()

class Application:
    name = ""
    locations = []
    full_name = ""
    icon_name = ""
    icon = None
    data_size = 0
    
    def set_locations(self, locations):
        self.locations = []
        for loc in locations:
            loc = os.path.expanduser(loc)
            self.locations.append(loc)
    
    def load_icon(self):
        if not self.icon_name:
            return
        self.icon = icon_theme_default.load_icon(self.icon_name, 32, 0)
    
    def calculate_size(self, force=False):
        if self.data_size > 0 and not force:
            return self.data_size
        self.data_size = 0
        for location in self.locations:
            if not os.path.exists(location):
                continue
            if os.path.isdir(location):
                for root, dirs, files in os.walk(location):
                    for f in files:
                        self.data_size += os.path.getsize(os.path.join(root, f))
            else:
                self.data_size += os.path.getsize(location)
        return self.data_size

