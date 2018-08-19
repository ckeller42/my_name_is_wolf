# -*- coding: utf-8; -*-

"""
See https://waleedkhan.name/blog/pyqt-designer/ for the manual
"""

import distutils.cmd
import distutils.log
import os
import shutil
import subprocess
import sys
import zipfile
#import git
import datetime

from pyqt_distutils.build_ui import build_ui
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py

# https://github.com/ColinDuquesnoy/pyqt_distutils
class custom_build_py(build_py):
    def run(self):
        self.run_command('build_ui')
        build_py.run(self)


class PyInstallerCommand(distutils.cmd.Command):
    description = 'run pyinstaller'
    user_options = []

    def initialize_options(self):
        self.user_options.append(tuple())
        pass

    def finalize_options(self):
        pass

    def run(self):
        script_name = 'my_name_is_wolf_for_exe.py'

        
        # create a windows executable
        if sys.platform.startswith('win'):
            self.announce('Creating exe in windows', level=distutils.log.INFO)
            os.system("pyinstaller --exclude-module matplotlib --onefile %s -n my_name_is_wolf" % script_name)
            # create a zip file of the executable and store it in the specified folder

            if True:
                # TODO fix this mess
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
                    zf.write(execfile, 'my_name_is_wolf.exe')
                    zf.write('my_name_is_wolf.ini', 'my_name_is_wolf.ini')
                finally:
                    zf.close()
                    shutil.copy(zipresult, outfolder)
                    subprocess.call('explorer %s' % outfolder, shell=True)


        elif sys.platform.startswith('darwin'):
            # TODO fix this. Not really working due to issues with QT shared libs
            self.announce('Creating on mac ox x', level=distutils.log.INFO)
            os.system(
                "pyinstaller --exclude-module matplotlib --windowed %s -n my_name_is_wolf" % script_name)


#required = ['jira', 'pyOpenSSL', 'pyqt5','pyqt_distutils']
required = ['jira', 'pyOpenSSL','pyqt_distutils','pyqt5']


setup(
    name="my_name_is_wolf",
    author='Christoph G. Keller',
    author_email='christoph.g.keller@gmail.com',
    version="2.0.1",
    packages=find_packages(),
    install_requires = required,
    cmdclass={ "build_ui": build_ui,
               'build_py': custom_build_py,
               "pyinstaller" : PyInstallerCommand,}
)





