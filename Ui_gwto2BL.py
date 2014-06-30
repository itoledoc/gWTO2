# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/itoledo/Work/gWTO2/gwto2BL.ui'
#
# Created: Sun Jun 29 20:02:57 2014
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
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_BLMainWindow(object):
    def setupUi(self, BLMainWindow):
        date = datetime.datetime.now()
        BLMainWindow.setObjectName(_fromUtf8("BLMainWindow"))
        BLMainWindow.resize(1090, 836)
        self.centralwidget = QtGui.QWidget(BLMainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.MainFrame = QtGui.QFrame(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.MainFrame.sizePolicy().hasHeightForWidth())
        self.MainFrame.setSizePolicy(sizePolicy)
        self.MainFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.MainFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.MainFrame.setObjectName(_fromUtf8("MainFrame"))
        self.gridLayout_2 = QtGui.QGridLayout(self.MainFrame)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.OptionsFrame = QtGui.QFrame(self.MainFrame)
        self.OptionsFrame.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.OptionsFrame.sizePolicy().hasHeightForWidth())
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
        self.pwv_spin.setSingleStep(0.05)
        self.pwv_spin.setProperty("value", 1.2)
        self.pwv_spin.setObjectName(_fromUtf8("pwv_spin"))
        self.gridLayout_6.addWidget(self.pwv_spin, 0, 3, 1, 1)
        self.lst_label = QtGui.QLabel(self.OptionsFrame)
        self.lst_label.setObjectName(_fromUtf8("lst_label"))
        self.gridLayout_6.addWidget(self.lst_label, 0, 4, 1, 1)
        spacerItem = QtGui.QSpacerItem(
            40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem, 0, 7, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(
            40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
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
        self.now_button = QtGui.QPushButton(self.OptionsFrame)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.now_button.sizePolicy().hasHeightForWidth())
        self.now_button.setSizePolicy(sizePolicy)
        self.now_button.setMinimumSize(QtCore.QSize(30, 0))
        self.now_button.setObjectName(_fromUtf8("now_button"))
        self.gridLayout_6.addWidget(self.now_button, 0, 6, 1, 1)
        self.ArraysFrame = QtGui.QFrame(self.OptionsFrame)
        self.ArraysFrame.setMinimumSize(QtCore.QSize(400, 0))
        self.ArraysFrame.setAutoFillBackground(True)
        self.ArraysFrame.setFrameShape(QtGui.QFrame.Box)
        self.ArraysFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.ArraysFrame.setObjectName(_fromUtf8("ArraysFrame"))
        self.gridLayout_7 = QtGui.QGridLayout(self.ArraysFrame)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.B04_b = QtGui.QCheckBox(self.ArraysFrame)
        self.B04_b.setChecked(False)
        self.B04_b.setObjectName(_fromUtf8("B04_b"))
        self.gridLayout_7.addWidget(self.B04_b, 2, 2, 1, 1)
        self.array_label = QtGui.QLabel(self.ArraysFrame)
        self.array_label.setObjectName(_fromUtf8("array_label"))
        self.gridLayout_7.addWidget(self.array_label, 0, 0, 1, 1)
        self.stdarrays_combo = QtGui.QComboBox(self.ArraysFrame)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.stdarrays_combo.sizePolicy().hasHeightForWidth())
        self.stdarrays_combo.setSizePolicy(sizePolicy)
        self.stdarrays_combo.setMinimumSize(QtCore.QSize(100, 0))
        self.stdarrays_combo.setObjectName(_fromUtf8("stdarrays_combo"))
        self.stdarrays_combo.addItem(_fromUtf8(""))
        self.stdarrays_combo.addItem(_fromUtf8(""))
        self.stdarrays_combo.addItem(_fromUtf8(""))
        self.stdarrays_combo.addItem(_fromUtf8(""))
        self.stdarrays_combo.addItem(_fromUtf8(""))
        self.stdarrays_combo.addItem(_fromUtf8(""))
        self.stdarrays_combo.addItem(_fromUtf8(""))
        self.stdarrays_combo.addItem(_fromUtf8(""))
        self.gridLayout_7.addWidget(self.stdarrays_combo, 1, 2, 1, 1)
        self.std_conf_label = QtGui.QLabel(self.ArraysFrame)
        self.std_conf_label.setObjectName(_fromUtf8("std_conf_label"))
        self.gridLayout_7.addWidget(self.std_conf_label, 1, 0, 1, 1)
        self.blarrays_combo = QtGui.QComboBox(self.ArraysFrame)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.blarrays_combo.sizePolicy().hasHeightForWidth())
        self.blarrays_combo.setSizePolicy(sizePolicy)
        self.blarrays_combo.setMinimumSize(QtCore.QSize(100, 0))
        self.blarrays_combo.setObjectName(_fromUtf8("blarrays_combo"))
        self.gridLayout_7.addWidget(self.blarrays_combo, 0, 2, 1, 1)
        self.B03_b = QtGui.QCheckBox(self.ArraysFrame)
        self.B03_b.setChecked(True)
        self.B03_b.setObjectName(_fromUtf8("B03_b"))
        self.gridLayout_7.addWidget(self.B03_b, 2, 0, 1, 1)
        self.B06_b = QtGui.QCheckBox(self.ArraysFrame)
        self.B06_b.setChecked(True)
        self.B06_b.setObjectName(_fromUtf8("B06_b"))
        self.gridLayout_7.addWidget(self.B06_b, 2, 3, 1, 1)
        self.B07_b = QtGui.QCheckBox(self.ArraysFrame)
        self.B07_b.setChecked(True)
        self.B07_b.setObjectName(_fromUtf8("B07_b"))
        self.gridLayout_7.addWidget(self.B07_b, 2, 4, 1, 1)
        self.B08_b = QtGui.QCheckBox(self.ArraysFrame)
        self.B08_b.setObjectName(_fromUtf8("B08_b"))
        self.gridLayout_7.addWidget(self.B08_b, 2, 5, 1, 1)
        self.antennas_spin = QtGui.QSpinBox(self.ArraysFrame)
        self.antennas_spin.setMinimum(20)
        self.antennas_spin.setMaximum(54)
        self.antennas_spin.setProperty("value", 34)
        self.antennas_spin.setObjectName(_fromUtf8("antennas_spin"))
        self.gridLayout_7.addWidget(self.antennas_spin, 1, 6, 1, 1)
        self.array_ar_spin = QtGui.QDoubleSpinBox(self.ArraysFrame)
        self.array_ar_spin.setMinimum(0.01)
        self.array_ar_spin.setSingleStep(0.1)
        self.array_ar_spin.setProperty("value", 1.0)
        self.array_ar_spin.setObjectName(_fromUtf8("array_ar_spin"))
        self.gridLayout_7.addWidget(self.array_ar_spin, 0, 6, 1, 1)
        self.arrayAR_label = QtGui.QLabel(self.ArraysFrame)
        self.arrayAR_label.setObjectName(_fromUtf8("arrayAR_label"))
        self.gridLayout_7.addWidget(self.arrayAR_label, 0, 5, 1, 1)
        self.antennas_label = QtGui.QLabel(self.ArraysFrame)
        self.antennas_label.setObjectName(_fromUtf8("antennas_label"))
        self.gridLayout_7.addWidget(self.antennas_label, 1, 5, 1, 1)
        self.B09_b = QtGui.QCheckBox(self.ArraysFrame)
        self.B09_b.setChecked(True)
        self.B09_b.setObjectName(_fromUtf8("B09_b"))
        self.gridLayout_7.addWidget(self.B09_b, 2, 6, 1, 1)
        self.gridLayout_6.addWidget(self.ArraysFrame, 0, 12, 2, 1)
        self.gridLayout_2.addWidget(self.OptionsFrame, 0, 0, 1, 1)
        self.TabFrame = QtGui.QFrame(self.MainFrame)
        self.TabFrame.setFrameShape(QtGui.QFrame.Box)
        self.TabFrame.setObjectName(_fromUtf8("TabFrame"))
        self.gridLayout_3 = QtGui.QGridLayout(self.TabFrame)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.tabWidget = QtGui.QTabWidget(self.TabFrame)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.bl_tab = QtGui.QWidget()
        self.bl_tab.setAccessibleName(_fromUtf8(""))
        self.bl_tab.setObjectName(_fromUtf8("bl_tab"))
        self.gridLayout_4 = QtGui.QGridLayout(self.bl_tab)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.bl_sheet = QtGui.QTableView(self.bl_tab)
        self.bl_sheet.setEditTriggers(QtGui.QAbstractItemView.SelectedClicked)
        self.bl_sheet.setDragEnabled(True)
        self.bl_sheet.setSortingEnabled(True)
        self.bl_sheet.setObjectName(_fromUtf8("bl_sheet"))
        self.gridLayout_4.addWidget(self.bl_sheet, 0, 0, 1, 1)
        self.tabWidget.addTab(self.bl_tab, _fromUtf8(""))
        self.tc_tab = QtGui.QWidget()
        self.tc_tab.setObjectName(_fromUtf8("tc_tab"))
        self.gridLayout_5 = QtGui.QGridLayout(self.tc_tab)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.tc_sheet = QtGui.QTableView(self.tc_tab)
        self.tc_sheet.setObjectName(_fromUtf8("tc_sheet"))
        self.gridLayout_5.addWidget(self.tc_sheet, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tc_tab, _fromUtf8(""))
        self.pol_tab = QtGui.QWidget()
        self.pol_tab.setObjectName(_fromUtf8("pol_tab"))
        self.gridLayout_8 = QtGui.QGridLayout(self.pol_tab)
        self.gridLayout_8.setObjectName(_fromUtf8("gridLayout_8"))
        self.pol_sheet = QtGui.QTableView(self.pol_tab)
        self.pol_sheet.setObjectName(_fromUtf8("pol_sheet"))
        self.gridLayout_8.addWidget(self.pol_sheet, 0, 0, 1, 1)
        self.tabWidget.addTab(self.pol_tab, _fromUtf8(""))
        self.session_tab = QtGui.QWidget()
        self.session_tab.setObjectName(_fromUtf8("session_tab"))
        self.gridLayout_9 = QtGui.QGridLayout(self.session_tab)
        self.gridLayout_9.setObjectName(_fromUtf8("gridLayout_9"))
        self.session_sheet = QtGui.QTableView(self.session_tab)
        self.session_sheet.setObjectName(_fromUtf8("session_sheet"))
        self.gridLayout_9.addWidget(self.session_sheet, 0, 0, 1, 1)
        self.tabWidget.addTab(self.session_tab, _fromUtf8(""))
        self.gridLayout_3.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.TabFrame, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.MainFrame, 0, 0, 1, 1)
        BLMainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(BLMainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1090, 27))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuMenu = QtGui.QMenu(self.menubar)
        self.menuMenu.setObjectName(_fromUtf8("menuMenu"))
        self.menuOutputs = QtGui.QMenu(self.menubar)
        self.menuOutputs.setObjectName(_fromUtf8("menuOutputs"))
        BLMainWindow.setMenuBar(self.menubar)
        self.actionAll_SBs = QtGui.QAction(BLMainWindow)
        self.actionAll_SBs.setObjectName(_fromUtf8("actionAll_SBs"))
        self.actionPlanning = QtGui.QAction(BLMainWindow)
        self.actionPlanning.setObjectName(_fromUtf8("actionPlanning"))
        self.actionQuit = QtGui.QAction(BLMainWindow)
        self.actionQuit.setObjectName(_fromUtf8("actionQuit"))
        self.actionGenerate_all_sbinfo = QtGui.QAction(BLMainWindow)
        self.actionGenerate_all_sbinfo.setObjectName(
            _fromUtf8("actionGenerate_all_sbinfo"))
        self.actionGenerate_excel_stat = QtGui.QAction(BLMainWindow)
        self.actionGenerate_excel_stat.setObjectName(
            _fromUtf8("actionGenerate_excel_stat"))
        self.menuMenu.addAction(self.actionAll_SBs)
        self.menuMenu.addAction(self.actionPlanning)
        self.menuMenu.addSeparator()
        self.menuMenu.addAction(self.actionQuit)
        self.menuOutputs.addAction(self.actionGenerate_all_sbinfo)
        self.menuOutputs.addAction(self.actionGenerate_excel_stat)
        self.menubar.addAction(self.menuMenu.menuAction())
        self.menubar.addAction(self.menuOutputs.menuAction())

        self.retranslateUi(BLMainWindow)
        self.tabWidget.setCurrentIndex(3)
        QtCore.QMetaObject.connectSlotsByName(BLMainWindow)

    def retranslateUi(self, BLMainWindow):
        BLMainWindow.setWindowTitle(
            _translate("BLMainWindow", "gWTO2 - BL", None))
        self.pwv_label.setText(
            _translate("BLMainWindow", "PWV", None))
        self.date_datetime.setDisplayFormat(
            _translate("BLMainWindow", "yyyy/MM/dd HH:mm", None))
        self.horizon_label.setText(
            _translate("BLMainWindow", "Horizon", None))
        self.minha_label.setText(
            _translate("BLMainWindow", "minHA", None))
        self.date_label.setText(
            _translate("BLMainWindow", "Date", None))
        self.maxha_label.setText(
            _translate("BLMainWindow", "maxHA", None))
        self.lst_label.setText(
            _translate("BLMainWindow", "LST", None))
        self.now_button.setText(
            _translate("BLMainWindow", "Now", None))
        self.B04_b.setText(
            _translate("BLMainWindow", "B04", None))
        self.array_label.setText(
            _translate("BLMainWindow", "BL Arrays:", None))
        self.stdarrays_combo.setItemText(
            0, _translate("BLMainWindow", "Current Conf.", None))
        self.stdarrays_combo.setItemText(
            1, _translate("BLMainWindow", "C34-1", None))
        self.stdarrays_combo.setItemText(
            2, _translate("BLMainWindow", "C34-2", None))
        self.stdarrays_combo.setItemText(
            3, _translate("BLMainWindow", "C34-3", None))
        self.stdarrays_combo.setItemText(
            4, _translate("BLMainWindow", "C34-4", None))
        self.stdarrays_combo.setItemText(
            5, _translate("BLMainWindow", "C34-5", None))
        self.stdarrays_combo.setItemText(
            6, _translate("BLMainWindow", "C34-6", None))
        self.stdarrays_combo.setItemText(
            7, _translate("BLMainWindow", "C34-7", None))
        self.std_conf_label.setText(_translate("BLMainWindow", "Std. Conf.:", None))
        self.B03_b.setText(_translate("BLMainWindow", "B03", None))
        self.B06_b.setText(_translate("BLMainWindow", "B06", None))
        self.B07_b.setText(_translate("BLMainWindow", "B07", None))
        self.B08_b.setText(_translate("BLMainWindow", "B08", None))
        self.arrayAR_label.setText(
            _translate("BLMainWindow", "Array AR:", None))
        self.antennas_label.setText(
            _translate("BLMainWindow", "Antennas:", None))
        self.B09_b.setText(_translate("BLMainWindow", "B09", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.bl_tab), _translate(
                "BLMainWindow", "Standard", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tc_tab), _translate(
                "BLMainWindow", "Time Const.", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.pol_tab), _translate(
                "BLMainWindow", "Polarization", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.session_tab), _translate(
                "BLMainWindow", "Sessions", None))
        self.menuMenu.setTitle(_translate("BLMainWindow", "Menu", None))
        self.menuOutputs.setTitle(_translate("BLMainWindow", "Outputs", None))
        self.actionAll_SBs.setText(_translate("BLMainWindow", "All SBs", None))
        self.actionPlanning.setText(_translate(
            "BLMainWindow", "Planning", None))
        self.actionQuit.setText(_translate("BLMainWindow", "Quit", None))
        self.actionGenerate_all_sbinfo.setText(
            _translate("BLMainWindow", "Generate all.sbinfo", None))
        self.actionGenerate_excel_stat.setText(
            _translate("BLMainWindow", "Generate excel stat.", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    BLMainWindow = QtGui.QMainWindow()
    ui = Ui_BLMainWindow()
    ui.setupUi(BLMainWindow)
    BLMainWindow.show()
    sys.exit(app.exec_())

