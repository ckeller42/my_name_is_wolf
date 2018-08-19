#!/usr/bin/python
# -*- coding: utf-8; -*-
"""
From the QT ui files create the necessary classes.
"""
__author__ = "Christoph G. Keller"
__copyright__ = "Copyright 2017"
__credits__ = [""]
__license__ = "GPL"
__version__ = "2.0"
__maintainer__ = "Christoph G. Keller"
__email__ = "christoph.g.keller@gmail.com"
__status__ = "Production"

import os
import sys

if __name__ == '__main__':

    gui_folder = os.path.join('my_name_is_wolf','gui')
    # list of gui files to be created
    # noinspection SpellCheckingInspection
    gui_files = ['wolf_gui',
                 'login_gui',
                 'cert_gui',
                 'about_gui',
                 'jira_settings_gui',
                 'project_select_gui',
                 'add_label_gui',
                 'add_assignee_gui']

    for i in gui_files:
        # noinspection SpellCheckingInspection
        if sys.platform.startswith('win'):
            python_executable = 'python'
        else:
            python_executable = sys.executable

        out = os.system(r'%s -m PyQt5.uic.pyuic -x %s -o %s' % (python_executable,
                                                                os.path.join(gui_folder, i + '.ui'),
                                                                os.path.join(gui_folder,i + '_ui.py')))

        print('Created gui: %s' % i)
