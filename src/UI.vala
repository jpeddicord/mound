/*
 * Mound <https://launchpad.net/mound>
 *
 * Copyright (C) 2009 Jacob Peddicord <jpeddicord@ubuntu.com>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 */

using Gtk;

namespace Mound {

    class MainUI : GLib.Object {
        
        public Builder builder;
        public Window main_window;
        private Table buttons_table;
        private Mound mound;
        
        public MainUI (ref Mound use_mound) {
            mound = use_mound;
        }
        
        construct {
            builder = new Builder ();
            string filename;
            if (FileUtils.test ("mound.ui", FileTest.EXISTS)) {
                filename = "mound.ui";
            } else {
                filename = "%s/mound.ui".printf(Build.DATADIR);
            }
            
            try {
                builder.add_from_file (filename);
            } catch (Error e) {
                error ("Could not load UI: %s", e.message);
            }
            
            main_window = builder.get_object ("win_main") as Window;
            main_window.destroy.connect (Gtk.main_quit);
            
            buttons_table = builder.get_object ("buttons_table") as Table;
            
            main_window.show_all ();
        }
        

    
    }

}
