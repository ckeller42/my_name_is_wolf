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
from .gui.jira_settings_gui_ui import Ui_JiraSettings

from  my_name_is_wolf.parameter_wrapper import ParameterWrapper


class JiraSettings(QDialog, Ui_JiraSettings):
    def __init__(self, params: ParameterWrapper):
        super(JiraSettings, self).__init__()
        self.setupUi(self)
        self.params = params

        # TODO improve the parameter stuff
        # if not (params.conf.has_section('jira') and params.conf.has_option('jira_url')):
        #    self.conf.set('jira', 'jira_url', '')

        self.lineEdit.setText(self.params.get_jira_url)
        self.checkBox_use_proxy.setChecked(self.params.get_use_proxy)
        self.lineEdit_http_proxy.setText(self.params.get_http_proxy_url)
        self.lineEdit_https_proxy.setText(self.params.get_https_proxy_url)
        self.buttonBox.accepted.connect(self.on_save)
        self.checkBox_use_proxy.stateChanged.connect(self.update_proxy_view)
        self.update_proxy_view()

    @pyqtSlot()
    def on_save(self):
        """
        Store the selected gui values in the param class and save to file
        """
        self.params.set_jira_url(str(self.lineEdit.text()))
        self.params.set_use_proxy(self.checkBox_use_proxy.checkState() == Qt.Checked)

        if self.checkBox_use_proxy.checkState() == Qt.Checked:
            self.params.set_http_proxy_url(self.lineEdit_http_proxy.text())
            self.params.set_https_proxy_url(self.lineEdit_https_proxy.text())

        self.params.set_use_cert(self.checkBox_p12.checkState() == Qt.Checked)
        self.params.save()

    @pyqtSlot()
    def update_proxy_view(self):
        """
        If the proxy checkbox is not set then hide the gui elements
        """
        if self.checkBox_use_proxy.checkState() == Qt.Checked:
            self.lineEdit_http_proxy.show()
            self.lineEdit_https_proxy.show()
            self.label_http_proxy.show()
            self.label_https_proxy.show()

        else:
            self.lineEdit_http_proxy.hide()
            self.lineEdit_https_proxy.hide()
            self.label_http_proxy.hide()
            self.label_https_proxy.hide()
