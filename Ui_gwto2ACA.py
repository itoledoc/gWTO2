# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/itoledo/Work/gWTO2/gwto2ACA.ui'
#
# Created: Mon Jun 30 16:24:14 2014
#      by: PyQt4 UI code generator 4.10.4
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
    # noinspection PyPep8Naming
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


# noinspection PyArgumentList,PyPep8Naming,PyShadowingNames
class Ui_ACAMainWindow(object):
    def setupUi(self, ACAMainWindow):
        # Set date
        date = datetime.datetime.now()
        ACAMainWindow.setObjectName(_fromUtf8("ACAMainWindow"))
        ACAMainWindow.resize(1200, 800)

        self.centralwidget = QtGui.QWidget(ACAMainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))

        self.MainFrame = QtGui.QFrame(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.MainFrame.sizePolicy().hasHeightForWidth())
        self.MainFrame.setSizePolicy(sizePolicy)
        self.MainFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.MainFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.MainFrame.setObjectName(_fromUtf8("MainFrame"))
        self.gridLayout_2 = QtGui.QGridLayout(self.MainFrame)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))

        self.OptionsFrame = QtGui.QFrame(self.MainFrame)
        self.OptionsFrame.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.OptionsFrame.sizePolicy().hasHeightForWidth())
        self.OptionsFrame.setSizePolicy(sizePolicy)
        self.OptionsFrame.setMinimumSize(QtCore.QSize(0, 30))
        self.OptionsFrame.setFrameShape(QtGui.QFrame.Box)
        self.OptionsFrame.setObjectName(_fromUtf8("OptionsFrame"))
        self.gridLayout_6 = QtGui.QGridLayout(self.OptionsFrame)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))

        self.pwv_label = QtGui.QLabel(self.OptionsFrame)
        self.pwv_label.setObjectName(_fromUtf8("pwv_label"))
        self.gridLayout_6.addWidget(self.pwv_label, 0, 2, 1, 1)

        self.maxha_spin = QtGui.QSpinBox(self.OptionsFrame)
        self.maxha_spin.setMinimum(-12)
        self.maxha_spin.setMaximum(12)
        self.maxha_spin.setProperty("value", 3)
        self.maxha_spin.setObjectName(_fromUtf8("maxha_spin"))
        self.gridLayout_6.addWidget(self.maxha_spin, 1, 5, 1, 1)

        self.date_datetime = QtGui.QDateTimeEdit(self.OptionsFrame)
        self.date_datetime.setCurrentSection(QtGui.QDateTimeEdit.YearSection)
        self.date_datetime.setWrapping(True)
        self.date_datetime.setDateTime(
            QtCore.QDateTime(
                QtCore.QDate(date.date().year, date.date().month,
                             date.date().day),
                QtCore.QTime(date.time().hour, date.time().minute,
                             date.time().second)))
        self.date_datetime.setTime(
            QtCore.QTime(
                date.time().hour, date.time().minute, date.time().second))
        self.date_datetime.setTimeSpec(QtCore.Qt.UTC)
        self.date_datetime.setObjectName(_fromUtf8("date_datetime"))
        self.gridLayout_6.addWidget(self.date_datetime, 0, 1, 1, 1)

        self.horizon_spin = QtGui.QSpinBox(self.OptionsFrame)
        self.horizon_spin.setMaximum(90)
        self.horizon_spin.setProperty("value", 20)
        self.horizon_spin.setObjectName(_fromUtf8("horizon_spin"))
        self.gridLayout_6.addWidget(self.horizon_spin, 1, 1, 1, 1)

        self.minha_spin = QtGui.QSpinBox(self.OptionsFrame)
        self.minha_spin.setMinimum(-12)
        self.minha_spin.setMaximum(12)
        self.minha_spin.setProperty("value", -5)
        self.minha_spin.setObjectName(_fromUtf8("minha_spin"))
        self.gridLayout_6.addWidget(self.minha_spin, 1, 3, 1, 1)

        self.horizon_label = QtGui.QLabel(self.OptionsFrame)
        self.horizon_label.setObjectName(_fromUtf8("horizon_label"))
        self.gridLayout_6.addWidget(self.horizon_label, 1, 0, 1, 1)

        self.minha_label = QtGui.QLabel(self.OptionsFrame)
        self.minha_label.setObjectName(_fromUtf8("minha_label"))
        self.gridLayout_6.addWidget(self.minha_label, 1, 2, 1, 1)

        self.date_label = QtGui.QLabel(self.OptionsFrame)
        self.date_label.setObjectName(_fromUtf8("date_label"))
        self.gridLayout_6.addWidget(self.date_label, 0, 0, 1, 1)

        self.maxha_label = QtGui.QLabel(self.OptionsFrame)
        self.maxha_label.setObjectName(_fromUtf8("maxha_label"))
        self.gridLayout_6.addWidget(self.maxha_label, 1, 4, 1, 1)

        self.pwv_spin = QtGui.QDoubleSpinBox(self.OptionsFrame)
        self.pwv_spin.setReadOnly(False)
        self.pwv_spin.setMaximum(20.0)
        self.pwv_spin.setMinimum(0.0)
        self.pwv_spin.setSingleStep(0.05)
        self.pwv_spin.setProperty("value", 1.2)
        self.pwv_spin.setObjectName(_fromUtf8("pwv_spin"))
        self.gridLayout_6.addWidget(self.pwv_spin, 0, 3, 1, 1)
        self.lst_label = QtGui.QLabel(self.OptionsFrame)
        self.lst_label.setObjectName(_fromUtf8("lst_label"))
        self.gridLayout_6.addWidget(self.lst_label, 0, 4, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem, 0, 7, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem1, 1, 7, 1, 1)

        self.lst_spin = QtGui.QTimeEdit(self.OptionsFrame)
        self.lst_spin.setEnabled(True)
        self.lst_spin.setReadOnly(True)
        self.lst_spin.setCurrentSection(QtGui.QDateTimeEdit.HourSection)
        self.lst_spin.setTimeSpec(QtCore.Qt.UTC)
        alma.date = self.date_datetime.dateTime().toPyDateTime()
        lst = alma.sidereal_time()
        lst_time = datetime.datetime.strptime(str(lst), '%H:%M:%S.%f').time()
        self.lst_spin.setTime(
            QtCore.QTime(lst_time.hour, lst_time.minute, lst_time.second))
        self.lst_spin.setObjectName(_fromUtf8("lst_spin"))
        self.gridLayout_6.addWidget(self.lst_spin, 0, 5, 1, 1)

        self.ArraysFrame = QtGui.QFrame(self.OptionsFrame)
        self.ArraysFrame.setMinimumSize(QtCore.QSize(200, 0))
        self.ArraysFrame.setAutoFillBackground(True)
        self.ArraysFrame.setFrameShape(QtGui.QFrame.Box)
        self.ArraysFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.ArraysFrame.setObjectName(_fromUtf8("ArraysFrame"))
        self.gridLayout_7 = QtGui.QGridLayout(self.ArraysFrame)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.widget = QtGui.QWidget(self.ArraysFrame)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.gridLayout_9 = QtGui.QGridLayout(self.widget)
        self.gridLayout_9.setMargin(0)
        self.gridLayout_9.setObjectName(_fromUtf8("gridLayout_9"))
        self.band9_b = QtGui.QCheckBox(self.widget)
        self.band9_b.setChecked(True)
        self.band9_b.setObjectName(_fromUtf8("band9_b"))
        self.gridLayout_9.addWidget(self.band9_b, 0, 5, 1, 1)
        self.band7_b = QtGui.QCheckBox(self.widget)
        self.band7_b.setChecked(True)
        self.band7_b.setObjectName(_fromUtf8("band7_b"))
        self.gridLayout_9.addWidget(self.band7_b, 0, 3, 1, 1)
        self.band8_b = QtGui.QCheckBox(self.widget)
        self.band8_b.setObjectName(_fromUtf8("band8_b"))
        self.gridLayout_9.addWidget(self.band8_b, 0, 4, 1, 1)
        self.band4_b = QtGui.QCheckBox(self.widget)
        self.band4_b.setObjectName(_fromUtf8("band4_b"))
        self.gridLayout_9.addWidget(self.band4_b, 0, 1, 1, 1)
        self.band6_b = QtGui.QCheckBox(self.widget)
        self.band6_b.setChecked(True)
        self.band6_b.setObjectName(_fromUtf8("band6_b"))
        self.gridLayout_9.addWidget(self.band6_b, 0, 2, 1, 1)
        self.band3_b = QtGui.QCheckBox(self.widget)
        self.band3_b.setChecked(True)
        self.band3_b.setObjectName(_fromUtf8("band3_b"))
        self.gridLayout_9.addWidget(self.band3_b, 0, 0, 1, 1)
        self.gridLayout_7.addWidget(self.widget, 1, 1, 1, 2)
        self.antennas_spin = QtGui.QSpinBox(self.ArraysFrame)
        self.antennas_spin.setMinimum(5)
        self.antennas_spin.setMaximum(12)
        self.antennas_spin.setProperty("value", 9)
        self.antennas_spin.setObjectName(_fromUtf8("antennas_spin"))
        self.gridLayout_7.addWidget(self.antennas_spin, 0, 2, 1, 1)
        self.antennas_label = QtGui.QLabel(self.ArraysFrame)
        self.antennas_label.setObjectName(_fromUtf8("antennas_label"))
        self.gridLayout_7.addWidget(self.antennas_label, 0, 1, 1, 1)
        self.gridLayout_6.addWidget(self.ArraysFrame, 0, 12, 2, 1)

        self.now_button = QtGui.QPushButton(self.OptionsFrame)
        self.now_button.setObjectName(_fromUtf8("now_button"))
        self.gridLayout_6.addWidget(self.now_button, 0, 6, 1, 1)
        self.run_button = QtGui.QPushButton(self.OptionsFrame)
        self.run_button.setObjectName(_fromUtf8("run_button"))
        self.gridLayout_6.addWidget(self.run_button, 1, 6, 1, 1)
        self.gridLayout_2.addWidget(self.OptionsFrame, 0, 0, 1, 1)
        self.TabFrame = QtGui.QFrame(self.MainFrame)
        self.TabFrame.setFrameShape(QtGui.QFrame.Box)
        self.TabFrame.setObjectName(_fromUtf8("TabFrame"))
        self.gridLayout_3 = QtGui.QGridLayout(self.TabFrame)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.tabWidget = QtGui.QTabWidget(self.TabFrame)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.seven_tab = QtGui.QWidget()
        self.seven_tab.setAccessibleName(_fromUtf8(""))
        self.seven_tab.setObjectName(_fromUtf8("seven_tab"))
        self.gridLayout_4 = QtGui.QGridLayout(self.seven_tab)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.seven_sheet = QtGui.QTableView(self.seven_tab)
        self.seven_sheet.setEditTriggers(QtGui.QAbstractItemView.SelectedClicked)
        self.seven_sheet.setDragEnabled(True)
        self.seven_sheet.setSortingEnabled(True)
        self.seven_sheet.setObjectName(_fromUtf8("seven_sheet"))
        self.gridLayout_4.addWidget(self.seven_sheet, 0, 0, 1, 1)
        self.tabWidget.addTab(self.seven_tab, _fromUtf8(""))
        self.tp_tab = QtGui.QWidget()
        self.tp_tab.setObjectName(_fromUtf8("tp_tab"))
        self.gridLayout_5 = QtGui.QGridLayout(self.tp_tab)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.tp_sheet = QtGui.QTableView(self.tp_tab)
        self.tp_sheet.setObjectName(_fromUtf8("tp_sheet"))
        self.gridLayout_5.addWidget(self.tp_sheet, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tp_tab, _fromUtf8(""))
        self.tc_tab = QtGui.QWidget()
        self.tc_tab.setObjectName(_fromUtf8("tc_tab"))
        self.gridLayout_8 = QtGui.QGridLayout(self.tc_tab)
        self.gridLayout_8.setObjectName(_fromUtf8("gridLayout_8"))
        self.tc_sheet = QtGui.QTableView(self.tc_tab)
        self.tc_sheet.setObjectName(_fromUtf8("tc_sheet"))
        self.gridLayout_8.addWidget(self.tc_sheet, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tc_tab, _fromUtf8(""))
        self.pol_tab = QtGui.QWidget()
        self.pol_tab.setObjectName(_fromUtf8("pol_tab"))
        self.gridLayout_11 = QtGui.QGridLayout(self.pol_tab)
        self.gridLayout_11.setObjectName(_fromUtf8("gridLayout_11"))
        self.pol_sheet = QtGui.QTableView(self.pol_tab)
        self.pol_sheet.setObjectName(_fromUtf8("pol_sheet"))
        self.gridLayout_11.addWidget(self.pol_sheet, 0, 0, 1, 1)
        self.tabWidget.addTab(self.pol_tab, _fromUtf8(""))
        self.session_tab = QtGui.QWidget()
        self.session_tab.setObjectName(_fromUtf8("session_tab"))
        self.gridLayout_10 = QtGui.QGridLayout(self.session_tab)
        self.gridLayout_10.setObjectName(_fromUtf8("gridLayout_10"))
        self.session_sheet = QtGui.QTableView(self.session_tab)
        self.session_sheet.setObjectName(_fromUtf8("session_sheet"))
        self.gridLayout_10.addWidget(self.session_sheet, 0, 0, 1, 1)
        self.tabWidget.addTab(self.session_tab, _fromUtf8(""))
        self.gridLayout_3.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.TabFrame, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.MainFrame, 0, 0, 1, 1)
        ACAMainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(ACAMainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1090, 27))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuMenu = QtGui.QMenu(self.menubar)
        self.menuMenu.setObjectName(_fromUtf8("menuMenu"))
        ACAMainWindow.setMenuBar(self.menubar)
        self.actionAll_SBs = QtGui.QAction(ACAMainWindow)
        self.actionAll_SBs.setObjectName(_fromUtf8("actionAll_SBs"))
        self.actionPlanning = QtGui.QAction(ACAMainWindow)
        self.actionPlanning.setObjectName(_fromUtf8("actionPlanning"))
        self.actionQuit = QtGui.QAction(ACAMainWindow)
        self.actionQuit.setObjectName(_fromUtf8("actionQuit"))
        self.menuMenu.addAction(self.actionAll_SBs)
        self.menuMenu.addAction(self.actionPlanning)
        self.menuMenu.addSeparator()
        self.menuMenu.addAction(self.actionQuit)
        self.menubar.addAction(self.menuMenu.menuAction())

        self.retranslateUi(ACAMainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(ACAMainWindow)

    def retranslateUi(self, ACAMainWindow):
        ACAMainWindow.setWindowTitle(_translate("ACAMainWindow", "gWTO2 - ACA", None))
        self.pwv_label.setText(_translate("ACAMainWindow", "PWV", None))
        self.date_datetime.setDisplayFormat(_translate("ACAMainWindow", "yyyy/MM/dd HH:mm", None))
        self.horizon_label.setText(_translate("ACAMainWindow", "Horizon", None))
        self.minha_label.setText(_translate("ACAMainWindow", "minHA", None))
        self.date_label.setText(_translate("ACAMainWindow", "Date", None))
        self.maxha_label.setText(_translate("ACAMainWindow", "maxHA", None))
        self.lst_label.setText(_translate("ACAMainWindow", "LST", None))
        self.band9_b.setText(_translate("ACAMainWindow", "B09", None))
        self.band7_b.setText(_translate("ACAMainWindow", "B07", None))
        self.band8_b.setText(_translate("ACAMainWindow", "B08", None))
        self.band4_b.setText(_translate("ACAMainWindow", "B04", None))
        self.band6_b.setText(_translate("ACAMainWindow", "B06", None))
        self.band3_b.setText(_translate("ACAMainWindow", "B03", None))
        self.antennas_label.setText(_translate("ACAMainWindow", "Antennas", None))
        self.now_button.setText(_translate("ACAMainWindow", "Now", None))
        self.run_button.setText(_translate("ACAMainWindow", "Run", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.seven_tab), _translate("ACAMainWindow", "ACA", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tp_tab), _translate("ACAMainWindow", "TP", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tc_tab), _translate("ACAMainWindow", "Time Constr.", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.pol_tab), _translate("ACAMainWindow", "Polarization", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.session_tab), _translate("ACAMainWindow", "Sessions", None))
        self.menuMenu.setTitle(_translate("ACAMainWindow", "Menu", None))
        self.actionAll_SBs.setText(_translate("ACAMainWindow", "All SBs", None))
        self.actionPlanning.setText(_translate("ACAMainWindow", "Planning", None))
        self.actionQuit.setText(_translate("ACAMainWindow", "Quit", None))
        self.lst_spin.setDisplayFormat(
            _translate("MainWindow", "hh:mm", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ACAMainWindow = QtGui.QMainWindow()
    ui = Ui_ACAMainWindow()
    ui.setupUi(ACAMainWindow)
    ACAMainWindow.show()
    sys.exit(app.exec_())

