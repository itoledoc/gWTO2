#!/usr/bin/env python

from PyQt4.QtGui import QApplication
from guilibs import MainWindow
import datetime


def main():
    import sys
    app = QApplication(sys.argv)
    wnd = MainWindow()
    wnd.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
