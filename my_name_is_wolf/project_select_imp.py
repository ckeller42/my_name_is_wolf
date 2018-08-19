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

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QDialog
from .gui.project_select_gui_ui import Ui_ProjectSelect

from my_name_is_wolf.jira_wrapper import JiraWrapper
from my_name_is_wolf.parameter_wrapper import ParameterWrapper


class ProjectSelect(QDialog, Ui_ProjectSelect):
    def __init__(self, jirawrapper: JiraWrapper, params: ParameterWrapper):
        """
        Constructor
        :param jirawrapper:
        :param params:
        """
        super(ProjectSelect, self).__init__()
        self.setupUi(self)
        self.jirawrapper = jirawrapper
        self.params = params

        # get all the projects and update the combobox
        jira_projects = self.jirawrapper.jira.projects()
        for i in jira_projects:
            self.comboBox_project.addItem(i.key)
        self.buttonBox.accepted.connect(self.on_save)

    @pyqtSlot()
    def on_save(self):
        """
        Store the selected gui values in the param class and save to file
        """
        sel_project = self.comboBox_project.currentText()
        self.params.set_project(sel_project)
        self.params.set_can_change_reporter(self.checkBox_change_reporter.checkState() == Qt.Checked)
        self.params.save()
