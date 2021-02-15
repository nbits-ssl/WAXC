from distutils.core import setup
import py2exe

option = {
    'dist_dir': 'win32',
    'excludes': ['readline'],
}

setup(
    console = ['waxc.py'],
    zipfile = None,
    options = {
        'py2exe': option
    }
)
