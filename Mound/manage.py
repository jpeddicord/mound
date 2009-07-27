

import os
from subprocess import Popen
from Mound.application import XDGDATA, Application

mound_snapshots = os.path.join(XDGDATA, 'mound-snapshots')


def take_snapshot(app):
    assert app is Application
    app_snapshot_dir = os.path.join(mound_snapshots, app.name)
    if not os.path.isdir(app_snapshot_dir):
        os.makedirs(app_snapshot_dir)
    cmd = ["tar", "czf"]
    for loc in app.locations:
        cmd.append(loc)
    print cmd
