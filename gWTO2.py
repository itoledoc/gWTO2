#!/usr/bin/env python
__author__ = 'itoledo'

from PyQt4.QtGui import QApplication
from gwto2BL import BLMainWindow
from gwto2ACA import ACAMainWindow


def main():
    import sys
    app = QApplication(sys.argv)
    if len(sys.argv) == 1:
        print("Please specify ACA or BL")
        return None
    if sys.argv[1] == 'ACA':
        wnd = ACAMainWindow()
    elif sys.argv[1] == 'BL':
        wnd = BLMainWindow()
    else:
        print("The argument must be ACA or BL")
        return None
    wnd.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()