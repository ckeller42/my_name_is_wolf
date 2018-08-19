#!/usr/bin/python
# -*- coding: utf-8; -*-
"""
Create windows executables
"""
__author__ = "Christoph G. Keller"
__copyright__ = "Copyright 2017"
__credits__ = [""]
__license__ = "GPL"
__version__ = "2.0.1"
__maintainer__ = "Christoph G. Keller"
__email__ = "christoph.g.keller@gmail.com"
__status__ = "Production"



import os
import shutil
import subprocess
import sys
import zipfile
import datetime
#import git

if __name__ == '__main__':

    script_name = 'my_name_is_wolf_for_exe.py'

    if sys.platform.startswith('win'):
        print('Creating exe in windows')

        python_executable = sys.executable
        bindir = os.path.dirname(python_executable)
        full_pyinstaller = os.path.join(bindir, 'Scripts', 'pyinstaller')
        os.system("%s --exclude-module matplotlib  --clean --onefile %s -n my_name_is_wolf" % (full_pyinstaller,script_name))

    else:
        print('No clue what OS you have')
        sys.exit(5)

    # create a zip file of the executable and store it in the specified folder
    if True:
        execfile = 'dist/my_name_is_wolf.exe'
        zipresult = 'dist/my_name_is_wolf_%s.zip' % datetime.datetime.today().strftime('%Y-%m-%d')
        #repo = git.Repo(search_parent_directories=True)
        #sha = repo.head.object.hexsha
        #outfolder = r'%s_%s' % (datetime.datetime.today().strftime('%Y-%m-%d'), sha)
        outfolder = r'%s' % (datetime.datetime.today().strftime('%Y-%m-%d'))

        try:
            os.makedirs(outfolder)
        except OSError:
            pass

        zf = zipfile.ZipFile(zipresult, mode='w')
        try:
            zf.write(execfile,'my_name_is_wolf.exe')
            zf.write('my_name_is_wolf.ini','my_name_is_wolf.ini')
        finally:
            zf.close()
            shutil.copy(zipresult, outfolder)
            subprocess.call('explorer %s' % outfolder, shell=True)
