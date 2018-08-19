#!/usr/bin/python
# -*- coding: utf-8; -*-
"""
Executable to be used with pyinstaller
"""

import PyQt5
from PyQt5.QtWidgets import QApplication

from my_name_is_wolf.wolf_gui_imp import *


# TODO figure out how to fix this with pyinstaller and __main__ see https://github.com/pyinstaller/pyinstaller/issues/2560


def main():
    import sys
    app = QApplication(sys.argv)
    frame = MainWindow()
    frame.show()
    app.exec_()


if __name__ == '__main__':
    main()
