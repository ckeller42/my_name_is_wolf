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

from .gui.add_label_gui_ui import Ui_AddLabel


class AddLabel(QDialog, Ui_AddLabel):
    def __init__(self, params):
        super(AddLabel, self).__init__()
        self.setupUi(self)
        self.params = params
        self.buttonBox.accepted.connect(self.add_label)

    @pyqtSlot()
    def add_label(self):
        label_str = str(self.lineEdit.text()).strip()
        if label_str:
            self.params.add_label(label_str)
            self.params.save()


if __name__ == "__main__":
    import sys
    from PyQt5 import QtWidgets
    from my_name_is_wolf.parameter_wrapper import ParameterWrapper

    app = QtWidgets.QApplication(sys.argv)
    param = ParameterWrapper()
    param.read()
    add_label = AddLabel(param)
    add_label.show()
    sys.exit(app.exec_())
