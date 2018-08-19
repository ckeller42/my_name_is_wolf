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

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QMessageBox, QDialogButtonBox

from .gui.add_assignee_gui_ui import Ui_AddAssignee


class AddAssignee(QDialog, Ui_AddAssignee):
    def __init__(self, jirawrapper, params):
        super(AddAssignee, self).__init__()
        self.setupUi(self)
        self.jirawrapper = jirawrapper
        self.params = params
        self.pushButton.clicked.connect(self.check_data)

        self.msg = QMessageBox()
        self.data_is_ok = False
        self.assignee = []
        ok_button = self.buttonBox.button(QDialogButtonBox.Ok)
        ok_button.setEnabled(False)

    def check_user(self):
        """
        Check JIRA for the username of the entered display name
        :return:
        """
        name = str(self.lineEdit_name.text())
        userid = self.jirawrapper.jira.search_assignable_users_for_projects(name, self.params.get_project)
        return userid

    def check_component(self):

        component = str(self.lineEdit_component.text())

        project_components = self.jirawrapper.get_components

        if not component in project_components:
            component = None

        return component

    @pyqtSlot()
    def check_data(self):

        self.data_is_ok = True
        userid = self.check_user()
        component = str(self.lineEdit_component.text())
        name = str(self.lineEdit_name.text())

        if not userid:
            self.data_is_ok = False
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.setStandardButtons(QMessageBox.Close)
            self.msg.setText('Could not find user')
            self.msg.exec_()

        if component and not self.check_component():
            self.data_is_ok = False
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.setStandardButtons(QMessageBox.Close)
            self.msg.setText('Could not find component')
            self.msg.exec_()

        if name and self.data_is_ok:
            assert userid
            assert name
            assert len(userid) > 0

            self.assignee = [name, userid[0].name, component]
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
