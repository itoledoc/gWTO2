#!/usr/bin/env python
__author__ = 'itoledo'

import optparse
from PyQt4.QtGui import QApplication
from gwto2BL import BLMainWindow
from gwto2ACA import ACAMainWindow


def main():
    """
    Starts the gWTO2 gui in one of its two flavors: BL or ACA

    :return:
    """
    import sys
    usage = "usage: %prog arg1 [options]\n\targ1 must be BL or ACA"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(
        '-c', '--clean', dest='clean', default=False, action='store_true',
        help="Force clean up of gWTO2 cache")
    parser.add_option('-p', '--path', default='/.wto',
                      help="Path for cache")
    (options, args) = parser.parse_args()
    app = QApplication(args)
    if len(args) == 0:
        print("Please specify ACA or BL")
        return None
    if args[0] == 'ACA':
        wnd = ACAMainWindow(path=options.path + '_aca/', forceup=options.clean)
    elif args[0] == 'BL':
        wnd = BLMainWindow(path=options.path + '/', forceup=options.clean)
    else:
        print("The argument must be ACA or BL")
        return None
    wnd.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()