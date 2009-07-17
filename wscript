import Scripting

APPNAME = 'mound'
VERSION = '0.1.1'
srcdir = '.'
blddir = 'build'

Scripting.excludes += ['debian', '.bzr-builddeb']
Scripting.g_gz = 'gz'

def set_options(opt):
    opt.tool_options('compiler_cc')

def configure(conf):
    conf.check_tool('compiler_cc cc vala misc')
    conf.check_cfg(package='gtk+-2.0', uselib_store='GTK', atleast_version='2.10.0', mandatory=1, args='--cflags --libs')
    # no need to define GLIB or GIO, GTK pulls it in
    
    conf.define('PACKAGE', APPNAME)
    conf.define('VERSION', VERSION)
    conf.define('PREFIX', conf.env['PREFIX'])
    conf.define('DATADIR', conf.env['PREFIX'] + '/share/' + APPNAME)
    conf.write_config_header('config.h')

def build(bld):
    bld.add_subdirs('src')

