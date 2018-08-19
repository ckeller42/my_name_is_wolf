import copy
import datetime
import getpass
import os
import re
import sys

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QMainWindow, QListWidgetItem, QAction, QDialog
from PyQt5.QtWidgets import QMessageBox

from .add_assignee_imp import AddAssignee
from .add_label_imp import AddLabel
from .cert_gui_imp import CertGui
from .gui.about_gui_ui import Ui_About
from .gui.wolf_gui_ui import Ui_MainWindow
from .jira_settings_imp import JiraSettings
from .login_imp import Login
from .parameter_wrapper import ParameterWrapper
from .project_select_imp import ProjectSelect
from .jira_wrapper import JiraWrapper

# TODO FEATURE add adding additional sub tasks to exiting task
# TODO get rid of the matlab style assignee list
# TODO change code for adding users


def get_url(in_url_str):
    match = re.search("(?P<url>https?://[^\s]+)", in_url_str)
    url_str = None
    if match is not None:
        url_str = match.group("url")
    return url_str


# noinspection SpellCheckingInspection,PyUnresolvedReferences
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent: object = None):
        super(MainWindow, self).__init__(parent)

        self.setupUi(self)
        self.msg = QMessageBox()

        self.params = ParameterWrapper()
        self.labels = None
        self.assignees = None

        have_config = self.params.read()

        if not have_config:
            self.JiraSettings = JiraSettings(self.params)
            self.JiraSettings.setWindowModality(QtCore.Qt.ApplicationModal)
            self.JiraSettings.exec_()

        # create the login window. will be called during connect if the netrc does not exist
        self.login = Login()
        self.login.setWindowModality(QtCore.Qt.ApplicationModal)

        # If cert is set and the files do not exist then open the gui
        if self.params.get_use_cert:
            if not os.path.isfile('mycert-dn.key') or not os.path.isfile('mycert-dn.crt'):
                self.p12gui = CertGui()
                self.p12gui.setWindowModality(QtCore.Qt.ApplicationModal)
                self.p12gui.exec_()

        # create the connnection
        self.jirawrapper = JiraWrapper(self.params)
        self.connect_to_jira()

        # get the available project from the server and show them
        if not self.params.get_project:
            self.ProjectSelect = ProjectSelect(self.jirawrapper, self.params)
            self.ProjectSelect.exec_()

        # get the available priorities and set the values in the gui
        self.update_priorities_from_jira()

        self.update_assignees_from_jira()

        # TODO cleanup
        # self.changed_select_all()

        self.show_hide_reporter()

        self.pushButton.clicked.connect(self.on_create_issue)
        self.calendarWidget.setSelectedDate(datetime.datetime.today())
        self.lineEdit.returnPressed.connect(self.pushButton.click)
        self.lineEdit.setFocus()
        self.selectAll.setCheckState(Qt.Checked)
        self.selectAll.stateChanged.connect(self.changed_select_all)
        self.pushButton_cleartext.clicked.connect(self.clear_text)

        # Menus
        self.aboutAction = QAction('&About', self)
        self.aboutAction.triggered.connect(self.show_about)
        self.menubar_about = self.menubar.addMenu('&Help')
        self.about = About()
        self.menubar_about.addAction(self.aboutAction)

        # Labels
        self.update_labels(self.params)
        self.add_label_gui = AddLabel(self.params)
        self.toolButton_new_label.clicked.connect(self.add_label_gui.show)
        self.add_label_gui.buttonBox.accepted.connect(lambda: self.update_labels(self.params))

        # add user
        self.add_user_gui = AddAssignee(self.jirawrapper, self.params)
        self.toolButton_new_user.clicked.connect(self.new_user)
        # needs to be called after assignes have been checked on server
        self.check_for_components()

    @pyqtSlot()
    def new_user(self):
        self.add_user_gui.exec_()
        new_assignee = self.add_user_gui.assignee
        if new_assignee:
            print(new_assignee)
            self.assignees.append(new_assignee)
            self.update_assigees_gui()

            # store it in the users file
            if self.add_user_gui.checkBox.isChecked():
                self.params.write_users(self.assignees)

    def show_hide_reporter(self):
        if self.params.can_change_reporter:
            # set the default reporter to the curretn user (only if in list)
            self.set_default_reporter()
        else:
            # changing reporter has been disabled, so hide the option
            self.comboBoxReporter.hide()
            self.label_reporter.hide()

    def check_for_components(self):
        """
        Check of the components defined by the user exist in the server.
        Show error pop-up if the component does not exist.
        """
        project_components = self.jirawrapper.get_components
        for val in self.assignees:
            if not val[2]:
                continue
            if val[2] not in project_components:
                # raise Exception('Could not find component %s for user %s' % (val[2], val[0]))
                error_str = 'Could not find component %s for user %s in project %s' % (
                    val[2], val[0], self.params.get_project)
                error_str += '\nMake sure the compontent exists on the server.'
                print(error_str)
                self.msg = QMessageBox()
                self.msg.setIcon(QMessageBox.Critical)
                self.msg.setStandardButtons(QMessageBox.Close)
                self.msg.setText(error_str)
                self.msg.exec_()
                sys.exit(5)

    @pyqtSlot()
    def update_labels(self, params):
        """
        Update the lable list with the labels defined in the params
        :param params:
        """
        self.labels = params.get_labels

        self.labelList.clear()
        # update the labels
        for a in self.labels:
            if a == '':
                # skip empty labels
                continue
            item = QListWidgetItem()
            item.setText(a)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.labelList.addItem(item)

    def update_assignees_from_jira(self):
        """
        Update the assignee list in the gui
        """
        try:
            self.assignees = self.jirawrapper.get_users(self.params.get_assignees)
        except Exception as e:
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.setStandardButtons(QMessageBox.Close)
            self.msg.setText(str(e))
            self.msg.exec_()
            sys.exit(5)

        self.update_assigees_gui()

    def update_assigees_gui(self):
        # update the assignee gui list

        # TODO Cleanup
        self.listWidget.clear()
        self.comboBoxAssignee.clear()
        self.comboBoxReporter.clear()

        for a in self.assignees:
            item = QListWidgetItem()
            item.setText(a[0])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            # TODO need to fix that they get all get checked when a new user is added
            item.setCheckState(Qt.Checked)
            self.listWidget.addItem(item)
            self.comboBoxAssignee.addItem(a[0])
            self.comboBoxReporter.addItem(a[0])

        assert len(self.assignees) == len(self.listWidget)
        # TODO this reuqires cleanup there should not be duplicated reportes and assignees
        assert len(self.assignees) == len(self.comboBoxAssignee)
        assert len(self.assignees) == len(self.comboBoxReporter)

    def update_priorities_from_jira(self):
        """
        Get the priorities from jira and update the combobox
        """
        jira_priorities = self.jirawrapper.jira.priorities()
        # update priority list
        for i in jira_priorities:
            self.comboBox_priority.addItem(i.name)

    @pyqtSlot()
    def show_about(self):
        """
        Show the about dialog
        """
        self.about.exec_()

    @pyqtSlot()
    def changed_select_all(self):
        """
        Trigger the setting or clearing of all the checkboxes
        """
        for index in range(self.listWidget.count()):
            if self.selectAll.checkState() == Qt.Checked:
                self.listWidget.item(index).setCheckState(Qt.Checked)
            else:
                self.listWidget.item(index).setCheckState(Qt.Unchecked)

    @pyqtSlot()
    def on_create_issue(self):
        """
        Trigger the issue creation
        """
        summary = self.lineEdit.text()
        if not summary:
            return False

        selected_users_idx = []
        for index in range(self.listWidget.count()):
            selected_users_idx.append(self.listWidget.item(index).checkState())

        duedate = self.calendarWidget.selectedDate().toString('yyyy-MM-dd')
        assert len(selected_users_idx) == len(self.assignees)
        assignees = []

        # TODO this needs to be cleaned up
        for i, a in enumerate(self.assignees):
            cur_a = copy.deepcopy(a)
            cur_a.append(selected_users_idx[i])
            assert (len(cur_a) == 4)
            assignees.append(cur_a)

        comment = self.commentEdit.toPlainText()

        main_assignee = str(self.comboBoxAssignee.currentText())

        labels = []
        for index in range(self.labelList.count()):
            if self.labelList.item(index).checkState():
                labels.append(self.labelList.item(index).text())
        labels.append('created_by_wolf')
        labels = list(set(labels))

        priority = str(self.comboBox_priority.currentText())
        reporter = str(self.comboBoxReporter.currentText())

        # change the text when pushed
        # TODO figure out why this does not work
        # button_text_orig = self.pushButton.text()
        # self.pushButton.setText('Running')
        # self.pushButton.show()
        print('Creating issue: %s' % summary)
        issue_url, error_msg = self.jirawrapper.create_task_subtask(summary, comment, reporter, main_assignee,
                                                                    assignees, duedate, labels,
                                                                    priority)
        # self.pushButton.setText(button_text_orig)
        # self.pushButton.show()

        if issue_url:
            print('Created issue %s' % issue_url)
            QMessageBox.information(self, 'Message', "<a href='%s'>Created Issue</a>" % issue_url,
                                    QMessageBox.Ok, QMessageBox.Ok)
            self.clear_text()
        else:
            self.msg.setIcon(QMessageBox.Warning)
            self.msg.setStandardButtons(QMessageBox.Close)
            self.msg.setText("Unable to create issue.\nError message:\n\n%s" % error_msg)
            self.msg.show()
        return True

    @pyqtSlot()
    def clear_text(self):
        """
        Clear the text fields
        """
        self.commentEdit.clear()
        self.lineEdit.clear()

    # noinspection PyUnresolvedReferences,PyUnusedLocal
    @pyqtSlot()
    def connect_to_jira(self):
        """
        Open the connection to JIRA
        """

        if not self.login.have_username_password:
            self.login.exec_()

        connection_ok, connection_exception = self.jirawrapper.connect(self.login.username, self.login.password)

        # handle situations with connection error
        if not connection_ok:
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.setStandardButtons(QMessageBox.Close)
            self.msg.setText(
                "Unable to connect. Fix error and restart\nError message:\n\n%s" % str(connection_exception))
            self.msg.exec_()
            sys.exit(5)

    def set_default_reporter(self):
        """
        Check the current username and set it as default assignee
        Shall be called after connection to jira
        """
        user = getpass.getuser()
        tidx = -1
        for idx, val in enumerate(self.assignees):
            if user.lower() == val[1].lower():
                tidx = self.comboBoxReporter.findText(val[0])
                break

        if tidx >= 0:
            # print('Setting default reporter to idx = %d' % tidx)
            self.comboBoxReporter.setCurrentIndex(tidx)


class About(QDialog, Ui_About):
    def __init__(self):
        super(About, self).__init__()
        self.setupUi(self)

