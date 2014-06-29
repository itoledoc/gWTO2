# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/itoledo/Work/gWTO2/arrayCheck.ui'
#
# Created: Sun Jun 29 14:17:17 2014
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ArrayCheck(object):
    def setupUi(self, ArrayCheck):
        ArrayCheck.setObjectName(_fromUtf8("ArrayCheck"))
        ArrayCheck.resize(615, 497)
        self.centralwidget = QtGui.QWidget(ArrayCheck)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.frame = QtGui.QFrame(self.centralwidget)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.gridLayout_2 = QtGui.QGridLayout(self.frame)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.frame_2 = QtGui.QFrame(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.gridLayout_3 = QtGui.QGridLayout(self.frame_2)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.cancel_button = QtGui.QPushButton(self.frame_2)
        self.cancel_button.setObjectName(_fromUtf8("cancel_button"))
        self.gridLayout_3.addWidget(self.cancel_button, 0, 6, 1, 1)
        self.antennas_line = QtGui.QLineEdit(self.frame_2)
        self.antennas_line.setReadOnly(True)
        self.antennas_line.setObjectName(_fromUtf8("antennas_line"))
        self.gridLayout_3.addWidget(self.antennas_line, 0, 3, 1, 1)
        self.arrayar_label = QtGui.QLabel(self.frame_2)
        self.arrayar_label.setObjectName(_fromUtf8("arrayar_label"))
        self.gridLayout_3.addWidget(self.arrayar_label, 0, 0, 1, 1)
        self.arrayar_line = QtGui.QLineEdit(self.frame_2)
        self.arrayar_line.setReadOnly(True)
        self.arrayar_line.setObjectName(_fromUtf8("arrayar_line"))
        self.gridLayout_3.addWidget(self.arrayar_line, 0, 1, 1, 1)
        self.antennas_label = QtGui.QLabel(self.frame_2)
        self.antennas_label.setObjectName(_fromUtf8("antennas_label"))
        self.gridLayout_3.addWidget(self.antennas_label, 0, 2, 1, 1)
        self.ok_button = QtGui.QPushButton(self.frame_2)
        self.ok_button.setObjectName(_fromUtf8("ok_button"))
        self.gridLayout_3.addWidget(self.ok_button, 0, 5, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem, 0, 4, 1, 1)
        self.gridLayout_2.addWidget(self.frame_2, 2, 0, 1, 1)
        self.graphicsView = QtGui.QGraphicsView(self.frame)
        self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
        self.gridLayout_2.addWidget(self.graphicsView, 1, 0, 1, 1)
        self.title = QtGui.QLabel(self.frame)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setObjectName(_fromUtf8("title"))
        self.gridLayout_2.addWidget(self.title, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)
        ArrayCheck.setCentralWidget(self.centralwidget)

        self.retranslateUi(ArrayCheck)
        QtCore.QMetaObject.connectSlotsByName(ArrayCheck)

    def retranslateUi(self, ArrayCheck):
        ArrayCheck.setWindowTitle(_translate("ArrayCheck", "Check Array", None))
        self.cancel_button.setText(_translate("ArrayCheck", "Cancel", None))
        self.arrayar_label.setText(_translate("ArrayCheck", "Array AR", None))
        self.antennas_label.setText(_translate("ArrayCheck", "Antennas", None))
        self.ok_button.setText(_translate("ArrayCheck", "OK", None))
        self.title.setText(_translate("ArrayCheck", "BL Array Assesment", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ArrayCheck = QtGui.QMainWindow()
    ui = Ui_ArrayCheck()
    ui.setupUi(ArrayCheck)
    ArrayCheck.show()
    sys.exit(app.exec_())

