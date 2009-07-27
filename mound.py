
import gtk
import Mound
from Mound.ui import MainUI

m = Mound.Mound()
m.load_applications("/usr/share/applications")
ui = MainUI(m)
ui.load_applications()
gtk.main()
