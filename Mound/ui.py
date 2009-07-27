#!/usr/bin/python

import gtk

class MainUI:
    
    def __init__(self, mound_inst):
        self.mound = mound_inst
        self.builder = gtk.Builder()
        try:
            self.builder.add_from_file("mound.ui")
        except:
            self.builder.add_from_file("/usr/share/mound/mound.ui")
        
        self.window = self.builder.get_object("win_main")
        self.window.connect("destroy", gtk.main_quit)
        
        self.lst_applications = self.builder.get_object("lst_applications")
        self.apps_iconview = self.builder.get_object ("apps_iconview")
        self.apps_iconview.connect("selection-changed", self.update_ui)
        
        self.img_appicon = self.builder.get_object ("img_appicon")
        self.lbl_title = self.builder.get_object ("lbl_title")
        self.lbl_app_details = self.builder.get_object ("lbl_app_details")
        self.btn_snapshots = self.builder.get_object ("btn_snapshots")
        self.btn_copy = self.builder.get_object ("btn_copy")
        self.btn_delete = self.builder.get_object ("btn_delete")
        
        self.update_ui ();
        
        self.window.show_all()
    
    def load_applications(self):
        for appname in self.mound.applications:
            self.lst_applications.append((
                self.mound.applications[appname].name,
                self.mound.applications[appname].full_name,
                self.mound.applications[appname].icon
            ))
    
    def update_ui(self, source=None):
        selection = self.apps_iconview.get_selected_items()
        if selection:
            # find the selected application
            selection = selection[0]
            selection_iter = self.lst_applications.get_iter(selection)
            selected = self.lst_applications.get_value(selection_iter, 0)
            app = self.mound.applications[selected]
            # grab the size
            app.calculate_size()
            txt = \
            "<i>This application is using <b>%0.1f MB</b> of space.</i>" % (
                float(app.data_size) / 1024 / 1024
            )
            self.lbl_app_details.props.label = txt
            self.lbl_title.props.label = "<span font='Sans Bold 14'>%s</span>" % app.full_name
            self.img_appicon.set_from_pixbuf(app.icon)
            self.btn_snapshots.props.sensitive = True
            self.btn_copy.props.sensitive = True
            self.btn_delete.props.sensitive = True
        else:
            self.lbl_title.props.label = "<span font=\"Sans Bold 14\">Select an Application</span>";
            self.img_appicon.set_from_stock ("gtk-dialog-question", gtk.ICON_SIZE_DND);
            self.btn_snapshots.props.sensitive = False
            self.btn_copy.props.sensitive = False
            self.btn_delete.props.sensitive = False
