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

const string APPLICATIONS_DIR = "/usr/share/applications";
const string DESKTOP_KEY = "X-UserData";
const string DEFAULTS_FILE = "/etc/userdata";

namespace Mound {

    struct Application {
        public string name;
        public string[] locations;
        public string full_name;
        public string icon_name;
        public Gdk.Pixbuf icon;
        public ulong data_size;
    }

    class Mound : GLib.Object {
        
        public HashTable<string,string> default_apps;
        public HashTable<string,Application?> applications;
        private Gtk.IconTheme icon_theme;
        
        public static int main (string[] args) {
            Gtk.init (ref args);
            var mound = new Mound ();
            mound.load_applications (APPLICATIONS_DIR);
            var ui = new MainUI (mound);
            ui.load_applications ();
            Gtk.main ();
            return 0;
        }
        
        construct {
            default_apps = new HashTable<string,string> (str_hash, str_equal);
            applications = new HashTable<string,Application?> (str_hash, str_equal);
            icon_theme = Gtk.IconTheme.get_default ();
        }
        
        public void load_applications (string appdir) {
            Dir dir;

            try {
                dir = Dir.open (appdir);
            } catch (FileError e) {
                print ("Unable to read the list of available applications.");
                return;
            }
            
            load_defaults (DEFAULTS_FILE);
            
            var desktop_pattern = new PatternSpec ("*.desktop");
            string desktop_filename = null;
            
            // read the applications directory
            while ((desktop_filename = dir.read_name ()) != null) {
                if (! desktop_pattern.match_string (desktop_filename)) {
                    continue;
                }
                
                string desktop_name = desktop_filename.substring (0, desktop_filename.length - ".desktop".length);
                string full_filename = Path.build_filename (appdir, desktop_filename);
                
                var desktop = new KeyFile ();
                try {
                    desktop.load_from_file (full_filename, KeyFileFlags.NONE);
                } catch (FileError e) {
                    warning ("Could not open %s: %s", desktop_filename, e.message);
                    continue;
                } catch (KeyFileError e) {
                    warning ("Error parsing %s: %s", desktop_filename, e.message);
                    continue;
                }
                
                string desktop_locations;
                try {
                    desktop_locations = desktop.get_string ("Desktop Entry", DESKTOP_KEY);
                } catch (KeyFileError e) {
                    if (e is KeyFileError.KEY_NOT_FOUND) {
                        // load the default
                        desktop_locations = default_apps.lookup (desktop_name);
                        if (desktop_locations == null) {
                            continue;
                        }
                    } else {
                        warning ("%s: %s", desktop_filename, e.message);
                        continue;
                    }
                }
                
                // at this point we should have a desktop entry that is valid
                Application app = Application ();
                app.name = desktop_name;
                
                try {
                    app.full_name = desktop.get_string ("Desktop Entry", "Name");
                } catch {
                    app.full_name = app.name;
                }
                try {
                    app.icon_name = desktop.get_string ("Desktop Entry", "Icon");
                    app.icon = icon_theme.load_icon (app.icon_name, 32, Gtk.IconLookupFlags.FORCE_SIZE);
                } catch {
                    app.icon_name = "";
                    app.icon = null;
                }
                
                app.locations = desktop_locations.split (";");
                app.data_size = 0;
                applications.insert (desktop_name, app);
            }
        }
        
        public void load_defaults (string defaults_location) {
            var f = File.new_for_path (defaults_location);
            var stream = new DataInputStream (f.read (null));
            string line;
            while ((line = stream.read_line (null, null)) != null) {
                // FIXME: do some error checking
                string half = line.str (" ");
                string app = line.substring (0, line.length - half.length);
                string locations = half.substring (1);
                default_apps.insert (app, locations);
            }
        }
        
        /** Calculate the total size of a list of locations.
         * Used to find application userdata sizes. This is rather slow,
         * so use sparingly.
         */
        public ulong calculate_app_size (string appname, bool force = false) {
            print ("=== Scanning %s ===\n", appname);
            weak Application app = applications.lookup (appname);
            print ("%p Current size: %lu (%s)\n", &app, app.data_size, app.full_name);
            if (app.data_size > 0 && force == false) {
                return app.data_size;
            }
            app.data_size = 0;
            foreach (string loc in app.locations) {
                print (" -- %s\n", loc);
                app.data_size += file_size (loc);
            }
            print ("%lu\n", app.data_size);
            return app.data_size;
        }
        
        /** Lookup the size of a file or directory recursively. */
        public static ulong file_size (string file) {
            if (FileUtils.test (file, FileTest.IS_DIR)) {
                ulong size = 0;
                string dirfile;
                try {
                    var dir = Dir.open (file);
                    string lookup;
                    while ((dirfile = dir.read_name ()) != null) {
                        lookup = file + "/" + dirfile;
                        size += file_size (lookup);
                    }
                    return size;
                } catch (FileError e) {
                    return 0;
                }
            } else {
                var file_stat = Posix.Stat ();
                Posix.stat (file, out file_stat);
                return file_stat.st_size;
            }
        }
        
    }

}
