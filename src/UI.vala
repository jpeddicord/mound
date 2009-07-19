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
        private unowned HashTable<string,Application?> applications;
        private ListStore lst_applications;
        private IconView apps_iconview;
        private Button btn_snapshots;
        private Button btn_copy;
        private Button btn_delete;
        
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
            
            lst_applications = builder.get_object ("lst_applications") as ListStore;
            apps_iconview = builder.get_object ("apps_iconview") as IconView;
            apps_iconview.selection_changed.connect((s) => {
                update_ui ();
            });
            
            btn_snapshots = builder.get_object ("btn_snapshots") as Button;
            btn_copy = builder.get_object ("btn_copy") as Button;
            btn_delete = builder.get_object ("btn_delete") as Button;
            
            main_window.show_all ();
        }
        
        public void load_applications (ref HashTable<string,Application?> use_applications) {
            applications = use_applications;
            foreach (string appname in applications.get_keys()) {
                var treeiter = TreeIter ();
                lst_applications.append (out treeiter);
                Application app = applications.lookup (appname);
                lst_applications.set_value (treeiter, 0, app.icon);
                lst_applications.set_value (treeiter, 1, app.full_name);
            }
            // force 4 rows
            apps_iconview.columns = ((int) applications.size ()) / 4;
        }
        
        private void update_ui () {
            TreePath path = null;
            unowned List<TreePath> selection = apps_iconview.get_selected_items ();
            print ("%d\n", (int) selection.length());
            foreach (TreePath selected in selection) {
                path = selected;
            }
            if (path != null) {
                btn_snapshots.sensitive = true;
                btn_copy.sensitive = true;
                btn_delete.sensitive = true;
            } else {
                btn_snapshots.sensitive = false;
                btn_copy.sensitive = false;
                btn_delete.sensitive = false;
            }
        }
    }

}
