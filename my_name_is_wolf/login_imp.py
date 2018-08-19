# -*- coding: utf-8; -*-
"""
Gui implementation for gui created via qt-designer.
"""

__author__ = "Christoph G. Keller"
__copyright__ = "Copyright 2017"
__credits__ = [""]
__license__ = "MIT"
__version__ = "2.0.0"
__maintainer__ = "Christoph G. Keller"
__email__ = "christoph.g.keller@gmail.com"
__status__ = "Production"

import netrc
import os

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog

from .gui.login_gui_ui import Ui_LoginDialog


class Login(QDialog, Ui_LoginDialog):
    def __init__(self):
        super(Login, self).__init__()
        self.setupUi(self)
        self.netrc_fname = 'my_name_is_wolf.netrc'
        self.buttonBox.accepted.connect(self.save)
        self.password = None
        self.username = None
        self.load()

    @property
    def have_username_password(self) -> bool:
        result = False
        if self.password and self.username:
            result = True
        return result

    @pyqtSlot()
    def save(self):
        self.password = str(self.lineEdit_password.text())
        self.username = str(self.lineEdit_username.text())

        if self.checkBox.checkState():
            f = open(self.netrc_fname, 'w')
            f.write('default login %s password %s' % (self.username, self.password))
            f.close()

    def load(self):
        if os.path.isfile(self.netrc_fname):
            info = netrc.netrc(self.netrc_fname)
            self.username, account, self.password = info.authenticators("default")
