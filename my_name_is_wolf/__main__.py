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


from PyQt5.QtWidgets import QApplication
from .wolf_gui_imp import MainWindow


def main():
    import sys
    app = QApplication(sys.argv)
    frame = MainWindow()
    frame.show()
    app.exec_()


if __name__ == '__main__':
    main()
