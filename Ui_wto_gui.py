# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/ignacio/Work/hplots2/src/gWTO/wto_gui_v2.ui'
#
# Created: Mon Dec  2 15:48:51 2013
#      by: PyQt4 UI code generator 4.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
import datetime
import ephem

alma = ephem.Observer()
alma.lat = '-23.0262015'
alma.long = '-67.7551257'
alma.elev = 5060

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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        date = datetime.datetime.now()
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1100, 600)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(1100, 600))

        self.centralwidget = QtGui.QWidget(MainWindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))

        self.frameTop = QtGui.QFrame(self.centralwidget)
        self.frameTop.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frameTop.setFrameShadow(QtGui.QFrame.Raised)
        self.frameTop.setObjectName(_fromUtf8("frameTop"))
        self.gridLayout_3 = QtGui.QGridLayout(self.frameTop)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.tabWidget = QtGui.QTabWidget(self.frameTop)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab12m = QtGui.QWidget()
        self.tab12m.setObjectName(_fromUtf8("tab12m"))
        self.gridLayout_4 = QtGui.QGridLayout(self.tab12m)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.blc_view = QtGui.QTableView(self.tab12m)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.blc_view.sizePolicy().hasHeightForWidth())
        self.blc_view.setSizePolicy(sizePolicy)
        self.blc_view.setObjectName(_fromUtf8("blc_view"))
        self.gridLayout_4.addWidget(self.blc_view, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab12m, _fromUtf8(""))
        self.tab7m = QtGui.QWidget()
        self.tab7m.setObjectName(_fromUtf8("tab7m"))
        self.gridLayout_5 = QtGui.QGridLayout(self.tab7m)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.aca_view = QtGui.QTableView(self.tab7m)
        self.aca_view.setObjectName(_fromUtf8("aca_view"))
        self.gridLayout_5.addWidget(self.aca_view, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab7m, _fromUtf8(""))
        self.tabTP = QtGui.QWidget()
        self.tabTP.setObjectName(_fromUtf8("tabTP"))
        self.gridLayout_7 = QtGui.QGridLayout(self.tabTP)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.tp_view = QtGui.QTableView(self.tabTP)
        self.tp_view.setObjectName(_fromUtf8("tp_view"))
        self.gridLayout_7.addWidget(self.tp_view, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabTP, _fromUtf8(""))
        self.tabTC = QtGui.QWidget()
        self.tabTC.setObjectName(_fromUtf8("tabTC"))
        self.gridLayout_8 = QtGui.QGridLayout(self.tabTC)
        self.gridLayout_8.setObjectName(_fromUtf8("gridLayout_8"))
        self.tc_view = QtGui.QTableView(self.tabTC)
        self.tc_view.setObjectName(_fromUtf8("tc_view"))
        self.gridLayout_8.addWidget(self.tc_view, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabTC, _fromUtf8(""))
        self.tabALL = QtGui.QWidget()
        self.tabALL.setObjectName(_fromUtf8("tabALL"))
        self.gridLayout_9 = QtGui.QGridLayout(self.tabALL)
        self.gridLayout_9.setObjectName(_fromUtf8("gridLayout_9"))
        self.allsb_view = QtGui.QTableView(self.tabALL)
        self.allsb_view.setObjectName(_fromUtf8("allsb_view"))
        self.gridLayout_9.addWidget(self.allsb_view, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabALL, _fromUtf8(""))
        self.tabPriority = QtGui.QWidget()
        self.tabPriority.setObjectName(_fromUtf8("tabPriority"))
        self.gridLayout_10 = QtGui.QGridLayout(self.tabPriority)
        self.gridLayout_10.setObjectName(_fromUtf8("gridLayout_10"))
        self.priority_view = QtGui.QTableView(self.tabPriority)
        self.priority_view.setObjectName(_fromUtf8("priority_view"))
        self.gridLayout_10.addWidget(self.priority_view, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabPriority, _fromUtf8(""))
        
        self.tabCalQuery = QtGui.QWidget()
        self.tabCalQuery.setObjectName(_fromUtf8("tabCalQuery"))
        self.gridLayout_12 = QtGui.QGridLayout(self.tabCalQuery)
        self.gridLayout_12.setObjectName(_fromUtf8("gridLayout_12"))
        self.treeWidget = QtGui.QTreeWidget(self.tabCalQuery)
        self.treeWidget.setObjectName(_fromUtf8("treeWidget"))

        self.treeWidget.header().setDefaultSectionSize(150)
        self.treeWidget.header().setHighlightSections(True)
        self.gridLayout_12.addWidget(self.treeWidget, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabCalQuery, _fromUtf8(""))
        
        self.gridLayout_3.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.frameTop, 2, 0, 1, 1)
        self.frameOptions = QtGui.QFrame(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frameOptions.sizePolicy().hasHeightForWidth())
        self.frameOptions.setSizePolicy(sizePolicy)
        self.frameOptions.setMinimumSize(QtCore.QSize(0, 32))
        self.frameOptions.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frameOptions.setFrameShadow(QtGui.QFrame.Raised)
        self.frameOptions.setObjectName(_fromUtf8("frameOptions"))

        self.gridLayout_2 = QtGui.QGridLayout(self.frameOptions)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))

        self.label_2 = QtGui.QLabel(self.frameOptions)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 0, 5, 1, 1)

        self.dateTimeBox = QtGui.QDateTimeEdit(self.frameOptions)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dateTimeBox.sizePolicy().hasHeightForWidth())
        self.dateTimeBox.setSizePolicy(sizePolicy)
        self.dateTimeBox.setWrapping(True)
        self.dateTimeBox.setDateTime(QtCore.QDateTime(QtCore.QDate(date.date().year, date.date().month, date.date().day), QtCore.QTime(date.time().hour, date.time().minute, date.time().second)))
        self.dateTimeBox.setTime(QtCore.QTime(date.time().hour, date.time().minute, date.time().second))
        self.dateTimeBox.setTimeSpec(QtCore.Qt.UTC)
        self.dateTimeBox.setObjectName(_fromUtf8("dateTimeBox"))
        self.gridLayout_2.addWidget(self.dateTimeBox, 0, 1, 1, 1)

        self.pushButton = QtGui.QPushButton(self.frameOptions)
        self.pushButton.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setMaximumSize(QtCore.QSize(45, 16777215))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.gridLayout_2.addWidget(self.pushButton, 0, 2, 1, 1)

        self.label_8 = QtGui.QLabel(self.frameOptions)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout_2.addWidget(self.label_8, 0, 3, 1, 1)

        self.timeEdit = QtGui.QTimeEdit(self.frameOptions)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("FreeSans"))
        self.timeEdit.setFrame(False)
        self.timeEdit.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.timeEdit.setReadOnly(True)
        self.timeEdit.setCurrentSection(QtGui.QDateTimeEdit.HourSection)
        self.timeEdit.setTimeSpec(QtCore.Qt.UTC)
        alma.date = self.dateTimeBox.dateTime().toPyDateTime()
        lst = alma.sidereal_time()
        lst_time = datetime.datetime.strptime(str(lst), '%H:%M:%S.%f').time()
        self.timeEdit.setTime(QtCore.QTime(lst_time.hour, lst_time.minute, lst_time.second))
        self.timeEdit.setObjectName(_fromUtf8("timeEdit"))
        self.gridLayout_2.addWidget(self.timeEdit, 0, 4, 1, 1)


        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 0, 9, 1, 1)

        self.runButton = QtGui.QPushButton(self.frameOptions)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.runButton.sizePolicy().hasHeightForWidth())
        self.runButton.setSizePolicy(sizePolicy)
        self.runButton.setObjectName(_fromUtf8("runButton"))
        self.gridLayout_2.addWidget(self.runButton, 0, 10, 1, 1)

        self.label = QtGui.QLabel(self.frameOptions)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.label_3 = QtGui.QLabel(self.frameOptions)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 0, 7, 1, 1)

        self.spinPwv = QtGui.QDoubleSpinBox(self.frameOptions)
        self.spinPwv.setSingleStep(0.1)
        self.spinPwv.setProperty("value", 1.2)
        self.spinPwv.setObjectName(_fromUtf8("spinPwv"))
        self.gridLayout_2.addWidget(self.spinPwv, 0, 6, 1, 1)

        self.confArrayBox = QtGui.QComboBox(self.frameOptions)
        self.confArrayBox.setObjectName(_fromUtf8("confArrayBox"))
        self.confArrayBox.addItem(_fromUtf8(""))
        self.confArrayBox.addItem(_fromUtf8(""))
        self.confArrayBox.addItem(_fromUtf8(""))
        self.confArrayBox.addItem(_fromUtf8(""))
        self.confArrayBox.addItem(_fromUtf8(""))
        self.confArrayBox.addItem(_fromUtf8(""))
        self.confArrayBox.addItem(_fromUtf8(""))
        self.confArrayBox.addItem(_fromUtf8(""))
        self.gridLayout_2.addWidget(self.confArrayBox, 0, 8, 1, 1)

        self.gridLayout.addWidget(self.frameOptions, 0, 0, 1, 1)
        self.frameTabs = QtGui.QFrame(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frameTabs.sizePolicy().hasHeightForWidth())
        self.frameTabs.setSizePolicy(sizePolicy)
        self.frameTabs.setMinimumSize(QtCore.QSize(0, 32))
        self.frameTabs.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frameTabs.setFrameShadow(QtGui.QFrame.Raised)
        self.frameTabs.setObjectName(_fromUtf8("frameTabs"))
        self.gridLayout_6 = QtGui.QGridLayout(self.frameTabs)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.spinTrans = QtGui.QDoubleSpinBox(self.frameTabs)
        self.spinTrans.setMaximum(1.0)
        self.spinTrans.setSingleStep(0.01)
        self.spinTrans.setProperty("value", 0.7)
        self.spinTrans.setObjectName(_fromUtf8("spinTrans"))
        self.gridLayout_6.addWidget(self.spinTrans, 0, 8, 1, 1)
        self.label_5 = QtGui.QLabel(self.frameTabs)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_6.addWidget(self.label_5, 0, 2, 1, 1)
        self.label_7 = QtGui.QLabel(self.frameTabs)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_6.addWidget(self.label_7, 0, 7, 1, 1)
        self.spinMinHA = QtGui.QDoubleSpinBox(self.frameTabs)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinMinHA.sizePolicy().hasHeightForWidth())
        self.spinMinHA.setSizePolicy(sizePolicy)
        self.spinMinHA.setMinimum(-12.0)
        self.spinMinHA.setMaximum(0.0)
        self.spinMinHA.setSingleStep(0.5)
        self.spinMinHA.setProperty("value", -5.0)
        self.spinMinHA.setObjectName(_fromUtf8("spinMinHA"))
        self.gridLayout_6.addWidget(self.spinMinHA, 0, 3, 1, 1)
        self.label_6 = QtGui.QLabel(self.frameTabs)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_6.addWidget(self.label_6, 0, 4, 1, 1)
        self.spinpElev = QtGui.QSpinBox(self.frameTabs)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinpElev.sizePolicy().hasHeightForWidth())
        self.spinpElev.setSizePolicy(sizePolicy)
        self.spinpElev.setMinimum(-90)
        self.spinpElev.setMaximum(90)
        self.spinpElev.setProperty("value", 20)
        self.spinpElev.setObjectName(_fromUtf8("spinpElev"))
        self.gridLayout_6.addWidget(self.spinpElev, 0, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.frameTabs)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_6.addWidget(self.label_4, 0, 0, 1, 1)
        self.spinMaxHA = QtGui.QDoubleSpinBox(self.frameTabs)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinMaxHA.sizePolicy().hasHeightForWidth())
        self.spinMaxHA.setSizePolicy(sizePolicy)
        self.spinMaxHA.setMaximum(12.0)
        self.spinMaxHA.setSingleStep(0.5)
        self.spinMaxHA.setProperty("value", 3.0)
        self.spinMaxHA.setObjectName(_fromUtf8("spinMaxHA"))
        self.gridLayout_6.addWidget(self.spinMaxHA, 0, 5, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem1, 0, 6, 1, 1)
        self.gridLayout.addWidget(self.frameTabs, 1, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1168, 27))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuHelp_About = QtGui.QMenu(self.menubar)
        self.menuHelp_About.setObjectName(_fromUtf8("menuHelp_About"))
        self.menuTools = QtGui.QMenu(self.menubar)
        self.menuTools.setObjectName(_fromUtf8("menuTools"))
        MainWindow.setMenuBar(self.menubar)
        self.actionHelp = QtGui.QAction(MainWindow)
        self.actionHelp.setObjectName(_fromUtf8("actionHelp"))
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionSee_prioriy_weights = QtGui.QAction(MainWindow)
        self.actionSee_prioriy_weights.setEnabled(True)
        self.actionSee_prioriy_weights.setObjectName(_fromUtf8("actionSee_prioriy_weights"))
        self.actionPriority_Weights = QtGui.QAction(MainWindow)
        self.actionPriority_Weights.setObjectName(_fromUtf8("actionPriority_Weights"))
        self.actionSave_All_SBs_output = QtGui.QAction(MainWindow)
        self.actionSave_All_SBs_output.setObjectName(_fromUtf8("actionSave_All_SBs_output"))
        self.menuHelp_About.addAction(self.actionHelp)
        self.menuHelp_About.addAction(self.actionAbout)
        self.menuHelp_About.addAction(self.actionPriority_Weights)
        self.menuTools.addAction(self.actionSave_All_SBs_output)
        self.menubar.addAction(self.menuHelp_About.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        self.confArrayBox.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "WTO (What to Observe)", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab12m), _translate("MainWindow", "12m", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab7m), _translate("MainWindow", "7m", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabTP), _translate("MainWindow", "TP", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabTC), _translate("MainWindow", "TimeCritical", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabALL), _translate("MainWindow", "All SBs", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabPriority), _translate("MainWindow", "Priorities", None))
        self.treeWidget.headerItem().setText(0, _translate("MainWindow", "SB UID", None))
        self.treeWidget.headerItem().setText(1, _translate("MainWindow", "Intent", None))
        self.treeWidget.headerItem().setText(2, _translate("MainWindow", "Query", None))
        self.treeWidget.headerItem().setText(3, _translate("MainWindow", "Name", None))
        self.treeWidget.headerItem().setText(4, _translate("MainWindow", "RA", None))
        self.treeWidget.headerItem().setText(5, _translate("MainWindow", "DEC", None))
        self.treeWidget.headerItem().setText(6, _translate("MainWindow", "Elev", None))
        self.treeWidget.headerItem().setText(7, _translate("MainWindow", "Sets in", None))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabCalQuery), _translate("MainWindow", "Target/Calibrators", None))
        self.label_2.setText(_translate("MainWindow", "pwv (mm)", None))
        self.dateTimeBox.setDisplayFormat(_translate("MainWindow", "MM/dd/yyyy hh:mm", None))
        self.runButton.setText(_translate("MainWindow", "Run", None))
        self.label.setText(_translate("MainWindow", "Date/Time (UTC):", None))
        self.label_3.setText(_translate("MainWindow", "12m Array Conf:", None))
        self.confArrayBox.setItemText(0, _translate("MainWindow", "C32-1", None))
        self.confArrayBox.setItemText(1, _translate("MainWindow", "C32-2", None))
        self.confArrayBox.setItemText(2, _translate("MainWindow", "C32-3", None))
        self.confArrayBox.setItemText(3, _translate("MainWindow", "C32-4", None))
        self.confArrayBox.setItemText(4, _translate("MainWindow", "C32-5", None))
        self.confArrayBox.setItemText(5, _translate("MainWindow", "C32-6", None))
        self.confArrayBox.setItemText(6, _translate("MainWindow", "All C32 allowed", None))
        self.confArrayBox.setItemText(7, _translate("MainWindow", "No filter", None))
        self.label_5.setText(_translate("MainWindow", "Min. HA:", None))
        self.label_7.setText(_translate("MainWindow", "Min. Transmision:", None))
        self.label_6.setText(_translate("MainWindow", "Max. HA", None))
        self.label_4.setText(_translate("MainWindow", "Min. Elevation:", None))
        self.label_8.setText(_translate("MainWindow", "LST ", None))
        self.pushButton.setText(_translate("MainWindow", "Now", None))
        self.timeEdit.setDisplayFormat(_translate("MainWindow", "hh:mm", None))
        self.menuHelp_About.setTitle(_translate("MainWindow", "Help/About", None))
        self.menuTools.setTitle(_translate("MainWindow", "Tools", None))
        self.actionHelp.setText(_translate("MainWindow", "Help", None))
        self.actionAbout.setText(_translate("MainWindow", "About", None))
        self.actionSee_prioriy_weights.setText(_translate("MainWindow", "See prioriy weights", None))
        self.actionPriority_Weights.setText(_translate("MainWindow", "Priority Weights", None))
        self.actionSave_All_SBs_output.setText(_translate("MainWindow", "Save All SBs output", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

