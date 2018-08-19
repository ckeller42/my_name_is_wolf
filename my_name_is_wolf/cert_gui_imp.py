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

import OpenSSL
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QFileDialog

from .gui.cert_gui_ui import Ui_CertGui


# noinspection SpellCheckingInspection
class CertGui(QDialog, Ui_CertGui):
    def __init__(self):
        """
        Constructor
        """
        super(CertGui, self).__init__()
        self.setupUi(self)
        self.fname = ''
        self.openButton.clicked.connect(self.open_file_name_dialog)
        self.buttonBox.accepted.connect(self.extract_keys)

    # noinspection SpellCheckingInspection
    @pyqtSlot()
    def open_file_name_dialog(self):
        """
        Open a file name dialog window
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                   "P12 Files (*.p12)", options=options)
        self.fname = str(file_name)

    @pyqtSlot()
    def extract_keys(self):
        """
        Extract the key to the local folder
        """
        # noinspection SpellCheckingInspection
        fname = self.fname
        password = self.lineEdit.text()
        print(fname)
        print(password)

        try:
            p12 = OpenSSL.crypto.load_pkcs12(open(self.fname, 'rb').read(), password)
            # PEM  formatted private key
            f = open('mycert-dn.key', 'wb')
            f.write(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, p12.get_privatekey()))
            f.close()
            f = open('mycert-dn.crt', 'wb')
            f.write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, p12.get_certificate()))
            f.close()
            if (False):
                f = open('cacert-dn.crt', 'wb')
                f.write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, p12.get_ca_certificates()))
                f.close()
        except Exception as e:
            print("Unable to load certificate %s" % self.fname)
            print(str(e))


if __name__ == '__main__':
    pass
