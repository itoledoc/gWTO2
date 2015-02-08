# -*- coding: utf-8 -*-

"""
Module implementing BLMainWindow.
"""
import operator
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import wtoAlgorithm as Wto

import ephem

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    # noinspection PyPep8Naming
    def _fromUtf8(s):
        return s

try:
    _encoding = QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)

except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)

alma = ephem.Observer()
alma.lat = '-23.0262015'
alma.long = '-67.7551257'
alma.elev = 5060

from Ui_gwto2BL import Ui_BLMainWindow
from arrayCheck2 import ArrayCheck2


# noinspection PyPep8Naming
class BLMainWindow(QMainWindow, Ui_BLMainWindow):
    """
    Class documentation goes here.
    """

    # TODO: Add column with type of observation (Mosaic, multisource, single...)
    # TODO: Add repFreq column
    def __init__(self, parent=None, path='/.wto/', source=None, forceup=False):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.alma = alma
        self.datas = Wto.WtoAlgorithm(path=path, source=source,
                                      forcenew=forceup)
        self.datas.set_pwv(self.pwv_spin.value())
        self.datas.set_minha(self.minha_spin.value())
        self.datas.set_maxha(self.maxha_spin.value())
        self.datas.horizon = self.horizon_spin.value()
        self.datas.date = self.date_datetime.dateTime().toPyDateTime()
        self.changed_date = True
        self.datas.num_ant = self.antennas_spin.value()
        # self.datas.set_bl_prop(array_name=None)
        self.datas.array_ar = None
        self.array_ar_spin.setValue(0.)

        try:
            self.current_pwv = Wto.pd.read_csv(
                self.datas.wto_path + 'conf/pwv_data.txt')
            pwv_n = setpwv(self.current_pwv.tail(1).values[0, 2])
            self.datas.set_pwv(pwv_n)
            self.pwv_spin.setValue(pwv_n)

        except IOError:
            print("No online wvr file, but don't worry")

    @pyqtSignature("int")
    def on_maxha_spin_valueChanged(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.datas.maxha = p0
    
    @pyqtSignature("")
    def on_date_datetime_editingFinished(self):
        """
        Slot documentation goes here.
        """
        pass
    
    @pyqtSignature("QDateTime")
    def on_date_datetime_dateTimeChanged(self, date):
        """
        Slot documentation goes here.
        """
        self.datas.date = date.toPyDateTime()
        self.datas.alma.date = self.datas.date
        lst = self.datas.alma.sidereal_time()
        lst_time = Wto.datetime.strptime(str(lst), '%H:%M:%S.%f').time()
        self.lst_spin.setTime(QTime(
            lst_time.hour, lst_time.minute, lst_time.second))
        self.changed_date = True
    
    @pyqtSignature("int")
    def on_horizon_spin_valueChanged(self, p0):
        """
        Slot documentation goes here.
        """
        self.datas.horizon = p0
    
    @pyqtSignature("int")
    def on_minha_spin_valueChanged(self, p0):
        """
        Slot documentation goes here.
        """
        self.datas.minha = p0
    
    @pyqtSignature("double")
    def on_pwv_spin_valueChanged(self, p0):
        """
        Slot documentation goes here.
        """
        e1 = "%.2f" % Wto.pd.np.around(p0, decimals=2)
        e = e1[-1]
        c = e1[:-1]
        if 0 <= int(e) < 3:
            e = '0'
            p = float(c + e)
        elif 3 <= int(e) < 7:
            e = '5'
            p = float(c + e)
        else:
            p = float(c) + 0.1

        self.datas.pwv = Wto.pd.np.around(p, decimals=2)

    @pyqtSignature("bool")
    def on_B03_b_toggled(self, checked):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError

    @pyqtSignature("bool")
    def on_B04_b_toggled(self, checked):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError

    @pyqtSignature("bool")
    def on_B06_b_toggled(self, checked):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError

    @pyqtSignature("bool")
    def on_B07_b_toggled(self, checked):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("bool")
    def on_B08_b_toggled(self, checked):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError

    @pyqtSignature("bool")
    def on_B09_b_toggled(self, checked):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        pass

    @pyqtSignature("int")
    def on_antennas_spin_valueChanged(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.datas.num_ant = p0
        print(self.datas.array_name, self.datas.array_ar, self.datas.num_ant)
    
    @pyqtSignature("")
    def on_array_ar_spin_editingFinished(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("double")
    def on_array_ar_spin_valueChanged(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.datas.array_ar = p0
    
    @pyqtSignature("bool")
    def on_actionAll_SBs_triggered(self, checked):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("")
    def on_actionAll_SBs_activated(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("bool")
    def on_actionPlanning_triggered(self, checked):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("")
    def on_actionPlanning_activated(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("bool")
    def on_actionQuit_triggered(self, checked):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("")
    def on_actionQuit_activated(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("bool")
    def on_actionGenerate_all_sbinfo_triggered(self, checked):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("")
    def on_actionGenerate_all_sbinfo_activated(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("bool")
    def on_actionGenerate_excel_stat_triggered(self, checked):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("")
    def on_actionGenerate_excel_stat_activated(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet

        raise NotImplementedError
    
    @pyqtSignature("QString")
    def on_stdarrays_combo_activated(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.datas.array_name = self.stdarrays_combo.currentText()
        self.antennas_spin.setReadOnly(True)
        self.blarrays_combo.setCurrentIndex(0)

        if self.datas.array_name == 'Default Conf.':
            self.datas.array_name = None
            self.antennas_spin.setReadOnly(False)
            self.datas.set_bl_prop(array_name=None)
            self.array_ar_spin.setValue(self.datas.array_ar)
            self.antennas_spin.setValue(self.datas.num_ant)
            self.pop = ArrayCheck2(ruv=self.datas.ruv,
                                   num_ant=self.datas.num_ant)
            self.pop.show()
            ret = self.pop.exec_()
            if ret:
                self.datas.array_ar = self.pop.array_ar
                self.datas.num_ant = self.pop.num_ant
                self.array_ar_spin.setValue(self.datas.array_ar)
                self.antennas_spin.setValue(self.datas.num_ant)
        else:
            self.datas.set_bl_prop(array_name=str(self.datas.array_name))
            self.array_ar_spin.setValue(self.datas.array_ar)
            self.antennas_spin.setValue(self.datas.num_ant)
            self.pop = ArrayCheck2(ruv=self.datas.ruv,
                                   num_ant=self.datas.num_ant)
            self.pop.show()
        print(self.datas.array_name, self.datas.array_ar, self.datas.num_ant)

    @pyqtSignature("QString")
    def on_blarrays_combo_activated(self):
        """
        Slot documentation goes here.
        """
        self.datas.array_name = self.blarrays_combo.currentText()
        self.stdarrays_combo.setCurrentIndex(0)
        self.antennas_spin.setReadOnly(True)
        self.datas.set_bl_prop(array_name=self.datas.array_name)
        self.pop = ArrayCheck2(ruv=self.datas.ruv, num_ant=self.datas.num_ant)
        self.pop.show()
        ret = self.pop.exec_()
        if ret:
            self.datas.array_ar = self.pop.array_ar
            self.datas.num_ant = self.pop.num_ant
            self.array_ar_spin.setValue(self.datas.array_ar)
            self.antennas_spin.setValue(self.datas.num_ant)
        else:
            self.datas.array_name = None
            self.stdarrays_combo.setCurrentIndex(1)
            self.on_stdarrays_combo_activated()
        print(self.datas.array_name, self.datas.array_ar, self.datas.num_ant)

    @pyqtSignature("bool")
    def on_now_button_clicked(self):
        """
        Slot documentation goes here.
        """
        date = Wto.datetime.utcnow()
        self.changed_date = True
        self.date_datetime.setDateTime(
            QDateTime(
                QDate(date.date().year, date.date().month, date.date().day),
                QTime(date.time().hour, date.time().minute,
                      date.time().second)))
        self.date_datetime.setTime(
            QTime(date.time().hour, date.time().minute, date.time().second))
        self.datas.date = date
        self.datas.alma.date = self.datas.date
        lst = self.datas.alma.sidereal_time()
        lst_time = Wto.datetime.strptime(str(lst), '%H:%M:%S.%f').time()
        self.lst_spin.setTime(
            QTime(lst_time.hour, lst_time.minute, lst_time.second))

        try:
            self.current_pwv = Wto.pd.read_csv(
                self.datas.wto_path + 'conf/pwv_data.txt')

            pwv_n = setpwv(self.current_pwv.tail(1).values[0, 2])
            self.datas.set_pwv(pwv_n)
            self.pwv_spin.setValue(pwv_n)

        except IOError:
            print('conf/pwv_data.txt')
            print("No online wvr file, but don't worry")

        self.datas.query_arrays()
        arrays = self.datas.bl_arrays.SE_ARRAYNAME.unique()
        c = 1
        self.blarrays_combo.addItem(_fromUtf8(""))
        self.blarrays_combo.setItemText(
            c, _translate("BLMainWindow", " ", None))
        for a in arrays:
            self.blarrays_combo.addItem(_fromUtf8(""))
            self.blarrays_combo.setItemText(
                c, _translate("BLMainWindow", a, None))
            c += 1
        self.blarrays_combo.setCurrentIndex(1)
        self.stdarrays_combo.setCurrentIndex(0)
        self.antennas_spin.setReadOnly(True)
        self.datas.array_name = self.blarrays_combo.currentText()
        self.datas.set_bl_prop(array_name=self.datas.array_name)
        print self.datas.ruv
        self.pop = ArrayCheck2(ruv=self.datas.ruv, num_ant=self.datas.num_ant)
        self.pop.show()
        ret = self.pop.exec_()
        if ret:
            self.datas.array_ar = self.pop.array_ar
            self.datas.num_ant = self.pop.num_ant
            self.array_ar_spin.setValue(self.datas.array_ar)
            self.antennas_spin.setValue(self.datas.num_ant)
            self.stdarrays_combo.setCurrentIndex(0)
        else:
            self.datas.array_name = None
            self.stdarrays_combo.setCurrentIndex(1)
            self.blarrays_combo.setCurrentIndex(0)
            self.on_stdarrays_combo_activated()
        print(self.datas.array_name, self.datas.array_ar, self.datas.num_ant,
              self.datas.pwv)

    # noinspection PyArgumentList
    @pyqtSignature("")
    def on_run_button_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        if self.datas.array_ar is None:
            QMessageBox.about(self, "Please select an Array first!!",
                              "Press OK and then select an array")
            return 0

        if self.changed_date:
            self.datas.update()
            self.changed_date = False
        else:
            QMessageBox.about(self, "Using cache (no status updates)",
                              "It is safe to continue by pressing OK")

        progress = QProgressDialog(self)
        progress.setLabelText('Running WTO2...')
        progress.show()
        progress.setAutoClose(True)
        QCoreApplication.processEvents()
        print(
            self.datas.date, self.datas.pwv, self.datas.minha, self.datas.maxha,
            self.datas.horizon, self.datas.array_name, self.datas.array_ar,
            self.datas.num_ant
        )
        QCoreApplication.processEvents()

        self.datas.selector('12m')
        self.datas.scorer('12m')
        self.datas.all12m.to_excel(self.datas.path + '/all12m.xls')
        self.datas.all12m.to_csv(self.datas.path + '/all12m.csv')
        self.datas.score12m.to_csv(self.datas.path + '/score12m.csv')
        std12 = self.datas.score12m.sort(
            'score', ascending=False).query(
                'isPolarization == False and isTimeConstrained == False')[
                    ['score', 'CODE', 'SB_UID', 'name', 'SB_state', 'band',
                     'RA', 'DEC', 'HA', 'elev', 'etime', 'grade', 'EXEC',
                     'scienceRank', 'execount', 'Total',
                     'tsysfrac', 'blfrac', 'frac', 'sb_array_score',
                     'sb_cond_score', 'maxPWVC', 'arrayMinAR', 'arcorr',
                     'arrayMaxAR', 'integrationTime', 'isPointSource',
                     'PRJ_ARCHIVE_UID']]

        tc12 = self.datas.score12m.sort(
            'score', ascending=False).query(
                'isPolarization == False and isTimeConstrained == True')[
                    ['score', 'CODE', 'SB_UID', 'name', 'SB_state', 'band',
                     'RA', 'DEC', 'HA', 'elev', 'etime', 'grade', 'EXEC',
                     'scienceRank', 'execount', 'Total',
                     'tsysfrac', 'blfrac', 'frac', 'sb_array_score',
                     'sb_cond_score', 'maxPWVC', 'arrayMinAR', 'arcorr',
                     'arrayMaxAR', 'integrationTime',
                     'PRJ_ARCHIVE_UID', 'startTime', 'endTime',
                     'allowedMargin', 'allowedUnits', 'repeats', 'isavoid']]

        pol12 = self.datas.score12m.sort(
            'score', ascending=False).query(
                'isPolarization == True')[
                    ['score', 'CODE', 'SB_UID', 'name', 'SB_state', 'band',
                     'RA', 'DEC', 'HA', 'elev', 'etime', 'grade', 'EXEC',
                     'scienceRank', 'execount', 'Total',
                     'tsysfrac', 'blfrac', 'frac', 'sb_array_score',
                     'sb_cond_score', 'maxPWVC', 'arrayMinAR', 'arcorr',
                     'arrayMaxAR', 'integrationTime', 'isPolarization',
                     'PRJ_ARCHIVE_UID']]

        if not self.B03_b.isChecked():
            std12 = std12.query('band != "ALMA_RB_03"')
            tc12 = tc12.query('band != "ALMA_RB_03"')
            pol12 = pol12.query('band != "ALMA_RB_03"')
        if not self.B04_b.isChecked():
            std12 = std12.query('band != "ALMA_RB_04"')
            tc12 = tc12.query('band != "ALMA_RB_04"')
            pol12 = pol12.query('band != "ALMA_RB_04"')
        if not self.B06_b.isChecked():
            std12 = std12.query('band != "ALMA_RB_06"')
            tc12 = tc12.query('band != "ALMA_RB_06"')
            pol12 = pol12.query('band != "ALMA_RB_06"')
        if not self.B07_b.isChecked():
            std12 = std12.query('band != "ALMA_RB_07"')
            tc12 = tc12.query('band != "ALMA_RB_07"')
            pol12 = pol12.query('band != "ALMA_RB_07"')
        if not self.B08_b.isChecked():
            std12 = std12.query('band != "ALMA_RB_08"')
            tc12 = tc12.query('band != "ALMA_RB_08"')
            pol12 = pol12.query('band != "ALMA_RB_08"')
        if not self.B09_b.isChecked():
            std12 = std12.query('band != "ALMA_RB_09"')
            tc12 = tc12.query('band != "ALMA_RB_09"')
            pol12 = pol12.query('band != "ALMA_RB_09"')

        std12.columns = Wto.pd.Index(
            [u'Score', u'CODE', u'SB UID', u'SB Name', u'SB State', u'Band',
             u'RA', u'DEC', u'HA', u'Elev.', u'Sets in', u'Grade', u'Executive',
             u'Rank', u'Exec. Req.',
             u'Exec. Done', u'TSysFrac', u'BLFrac', u'TotalFrac',
             u'Array Score', u'Cond. Score', u'maxPWVC', u'ArrayMinAR',
             u'ARcorr', u'ArrayMaxAR', u'TimeOnSource', u'Point Source',
             u'PRJ UID'], dtype='object')

        tc12.columns = Wto.pd.Index(
            [u'Score', u'CODE', u'SB UID', u'SB Name', u'SB State', u'Band',
             u'RA', u'DEC', u'HA', u'Elev.', u'Sets in', u'Grade', u'Executive',
             u'Rank', u'Exec. Req.',
             u'Exec. Done', u'TSysFrac', u'BLFrac', u'TotalFrac',
             u'Array Score', u'Cond. Score', u'maxPWVC', u'ArrayMinAR',
             u'ARcorr', u'ArrayMaxAR', u'ToS',
             u'PRJ UID', u'StartTime', u'EndTime', u'AllowedMargin',
             u'AllowedUnits', u'repeats', u'isavoid'], dtype='object')

        pol12.columns = Wto.pd.Index(
            [u'Score', u'CODE', u'SB UID', u'SB Name', u'SB State', u'Band',
             u'RA', u'DEC', u'HA', u'Elev.', u'Sets in', u'Grade', u'Executive',
             u'Rank', u'Exec. Req.',
             u'Exec. Done', u'TSysFrac', u'BLFrac', u'TotalFrac',
             u'Array Score', u'Cond. Score', u'maxPWVC', u'ArrayMinAR',
             u'ARcorr', u'ArrayMaxAR', u'Int. Time', u'isPolarization',
             u'PRJ UID'], dtype='object')

        print(std12.head(10))
        std12n = std12.to_records(index=False)
        header = std12n.dtype.names
        self.tmstd12 = MyStdTableModel(std12n, header, self)
        self.bl_sheet.setModel(self.tmstd12)
        self.bl_sheet.verticalHeader().setStretchLastSection(False)
        self.bl_sheet.setSortingEnabled(True)
        self.bl_sheet.sortByColumn(0, Qt.DescendingOrder)
        self.bl_sheet.resizeRowsToContents()
        self.connect(self.bl_sheet, SIGNAL("doubleClicked(QModelIndex)"),
                     self.hola)
        for column in range(26):
            if column in [1, 2, 3, 4, 5, 6, 7, 25, 26]:
                self.bl_sheet.resizeColumnToContents(column)
            elif column in [14, 15, 19, 20, 22, 24]:
                self.bl_sheet.setColumnWidth(column, 80)
            else:
                self.bl_sheet.setColumnWidth(column, 66)
        QCoreApplication.processEvents()

        tc12n = tc12.to_records(index=False)
        header = tc12n.dtype.names
        self.tmtc12 = MyTcTableModel(tc12n, header, self)
        self.tc_sheet.setModel(self.tmtc12)
        self.tc_sheet.verticalHeader().setStretchLastSection(False)
        self.tc_sheet.setSortingEnabled(True)
        self.tc_sheet.sortByColumn(0, Qt.DescendingOrder)
        self.tc_sheet.resizeRowsToContents()
        for column in range(25):
            if column in [1, 2, 3, 4, 5, 6, 7, 25]:
                self.tc_sheet.resizeColumnToContents(column)
            elif column in [14, 15, 19, 20, 22, 24]:
                self.tc_sheet.setColumnWidth(column, 80)
            else:
                self.tc_sheet.setColumnWidth(column, 66)
        QCoreApplication.processEvents()

        pol12n = pol12.to_records(index=False)
        header = pol12n.dtype.names
        self.tmpol12 = MyPolTableModel(pol12n, header, self)
        self.pol_sheet.setModel(self.tmpol12)
        self.pol_sheet.verticalHeader().setStretchLastSection(False)
        self.pol_sheet.setSortingEnabled(True)
        self.pol_sheet.sortByColumn(0, Qt.DescendingOrder)
        self.pol_sheet.resizeRowsToContents()
        for column in range(25):
            if column in [1, 2, 3, 4, 5, 6, 7, 25]:
                self.pol_sheet.resizeColumnToContents(column)
            elif column in [14, 15, 19, 20, 22, 24]:
                self.pol_sheet.setColumnWidth(column, 80)
            else:
                self.pol_sheet.setColumnWidth(column, 66)
        progress.close()

    def hola(self, x):
        print("hola", x.column(), x.row(), self.tmstd12.arraydata[x.row()][2])


# noinspection PyMethodOverriding
class MyStdTableModel(QAbstractTableModel):
    def __init__(self, datain, headerdata, parent=None):
        """ datain: a list of lists
            headerdata: a list of strings
        """
        QAbstractTableModel.__init__(self, parent)
        self.arraydata = datain
        self.headerdata = headerdata

    def rowCount(self, parent):
        try:
            return len(self.arraydata)
        except IndexError:
            return 0

    def columnCount(self, parent):
        try:
            return len(self.arraydata[0])
        except IndexError:
            print("Table Std is empty")
            return 0

    # noinspection PyTypeChecker
    def data(self, index, role):
        if not index.isValid():
            print("whaat?")
            return QVariant()
        sb = self.arraydata[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            if col in [8, 10]:
                if sb[col] < 0:
                    neg = '-'
                    ha_t = str(ephem.hours(str(abs(sb[col]))))
                    # noinspection PyCallByClass
                    ha = QTime.fromString(ha_t, 'h:m:s.z')
                else:
                    neg = ''
                    ha_t = str(ephem.hours(str(sb[col])))
                    # noinspection PyCallByClass
                    ha = QTime.fromString(ha_t, 'h:m:s.z')
                hastr = QString("%1").arg(neg + ha.toString('h:mm'))
                return QVariant(hastr)
            elif col == 6:
                h = ephem.hours(str(sb[col] / 15.))
                return QVariant(str(h)[:-3])
            elif col == 7:
                d = ephem.degrees(str(sb[col]))
                return QVariant(str(d)[:-2])
            elif col in [0, 16, 17, 18, 21, 22, 23, 24]:
                return QVariant(QString("%1").arg(sb[col], 0, 'f', 2))
            elif col in [9, 19, 20, 25]:
                return QVariant(QString("%1").arg(sb[col], 0, 'f', 1))
            elif col in [14, 15]:
                return QVariant(QString("%1").arg(sb[col], 0, 10))

            return QVariant(str(self.arraydata[index.row()][index.column()]))
        elif role == Qt.TextAlignmentRole:
            if col in [0, 6, 7, 8, 9, 10, 14, 15, 16, 17, 18, 19, 20, 21, 22,
                       22, 24, 25, 26]:
                return QVariant(int(Qt.AlignRight | Qt.AlignVCenter))
            if col in [11, 12, 13]:
                return QVariant(int(Qt.AlignCenter | Qt.AlignVCenter))
            return QVariant(int(Qt.AlignLeft | Qt.AlignVCenter))
        elif role == Qt.BackgroundColorRole:
            if 0 == index.row() % 2:
                c = QVariant(QColor(235, 245, 255))
            else:
                c = QVariant(QColor(250, 250, 250))
            if sb[19] < 8.5 and sb[26] == False:
                c = QVariant(QColor(255, 255, 0))
            if sb[20] == 0:
                c = QVariant(QColor(255, 110, 110))
            return c
        elif role == Qt.FontRole:
            if col in [0, 18, 20]:
                return QVariant(QFont("Cantarel", 10, QFont.Bold))

        return QVariant()

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerdata[col])
        return QVariant()

    # noinspection PyPep8Naming
    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.arraydata = sorted(self.arraydata, key=operator.itemgetter(Ncol))
        if order == Qt.DescendingOrder:
            self.arraydata.reverse()
        self.emit(SIGNAL("layoutChanged()"))


# noinspection PyMethodOverriding
class MyTcTableModel(QAbstractTableModel):
    def __init__(self, datain, headerdata, parent=None):
        """ datain: a list of lists
            headerdata: a list of strings
        """
        QAbstractTableModel.__init__(self, parent)
        self.arraydata = datain
        self.headerdata = headerdata

    def rowCount(self, parent):
        try:
            return len(self.arraydata)
        except IndexError:
            return 0

    def columnCount(self, parent):
        try:
            return len(self.arraydata[0])
        except IndexError:
            print("Table TC is empty")
            return 0

    # noinspection PyTypeChecker
    def data(self, index, role):
        if not index.isValid():
            print("whaat?")
            return QVariant()
        sb = self.arraydata[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            if col in [8, 10]:
                if sb[col] < 0:
                    neg = '-'
                    ha_t = str(ephem.hours(str(abs(sb[col]))))
                    # noinspection PyCallByClass
                    ha = QTime.fromString(ha_t, 'h:m:s.z')
                else:
                    neg = ''
                    ha_t = str(ephem.hours(str(sb[col])))
                    # noinspection PyCallByClass
                    ha = QTime.fromString(ha_t, 'h:m:s.z')
                hastr = QString("%1").arg(neg + ha.toString('h:mm'))
                return QVariant(hastr)
            elif col == 6:
                h = ephem.hours(str(sb[col] / 15.))
                return QVariant(str(h)[:-3])
            elif col == 7:
                d = ephem.degrees(str(sb[col]))
                return QVariant(str(d)[:-2])
            elif col in [0, 16, 17, 18, 21, 22, 23, 24]:
                return QVariant(QString("%1").arg(sb[col], 0, 'f', 2))
            elif col in [9, 19, 20, 25]:
                return QVariant(QString("%1").arg(sb[col], 0, 'f', 1))
            elif col in [14, 15]:
                return QVariant(QString("%1").arg(sb[col], 0, 10))

            return QVariant(str(self.arraydata[index.row()][index.column()]))
        elif role == Qt.TextAlignmentRole:
            if col in [0, 6, 7, 8, 9, 10, 14, 15, 16, 17, 18, 19, 20, 21, 22,
                       23, 24, 25]:
                return QVariant(int(Qt.AlignRight | Qt.AlignVCenter))
            if col in [11, 12, 13]:
                return QVariant(int(Qt.AlignCenter | Qt.AlignVCenter))
            return QVariant(int(Qt.AlignLeft | Qt.AlignVCenter))
        elif role == Qt.BackgroundColorRole:
            if 0 == index.row() % 2:
                c = QVariant(QColor(235, 245, 255))
            else:
                c = QVariant(QColor(250, 250, 250))
            if sb[19] < 9:
                c = QVariant(QColor(255, 255, 0))
            if sb[20] == 0:
                c = QVariant(QColor(255, 110, 110))

            return c
        elif role == Qt.FontRole:
            if col in [0, 18, 20]:
                return QVariant(QFont("Cantarel", 10, QFont.Bold))

        return QVariant()

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerdata[col])
        return QVariant()


# noinspection PyMethodOverriding
class MyPolTableModel(QAbstractTableModel):
    def __init__(self, datain, headerdata, parent=None):
        """ datain: a list of lists
            headerdata: a list of strings
        """
        QAbstractTableModel.__init__(self, parent)
        self.arraydata = datain
        self.headerdata = headerdata

    def rowCount(self, parent):
        try:
            return len(self.arraydata)
        except IndexError:
            return 0

    def columnCount(self, parent):
        try:
            return len(self.arraydata[0])
        except IndexError:
            print("Table Pol is empty")
            return 0

    # noinspection PyTypeChecker
    def data(self, index, role):
        if not index.isValid():
            print("whaat?")
            return QVariant()
        sb = self.arraydata[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            if col in [8, 10]:
                if sb[col] < 0:
                    neg = '-'
                    ha_t = str(ephem.hours(str(abs(sb[col]))))
                    # noinspection PyCallByClass
                    ha = QTime.fromString(ha_t, 'h:m:s.z')
                else:
                    neg = ''
                    ha_t = str(ephem.hours(str(sb[col])))
                    # noinspection PyCallByClass
                    ha = QTime.fromString(ha_t, 'h:m:s.z')
                hastr = QString("%1").arg(neg + ha.toString('h:mm'))
                return QVariant(hastr)
            elif col == 6:
                h = ephem.hours(str(sb[col] / 15.))
                return QVariant(str(h)[:-3])
            elif col == 7:
                d = ephem.degrees(str(sb[col]))
                return QVariant(str(d)[:-2])
            elif col in [0, 16, 17, 18, 21, 22, 23, 24]:
                return QVariant(QString("%1").arg(sb[col], 0, 'f', 2))
            elif col in [9, 19, 20, 25]:
                return QVariant(QString("%1").arg(sb[col], 0, 'f', 1))
            elif col in [14, 15]:
                return QVariant(QString("%1").arg(sb[col], 0, 10))

            return QVariant(str(self.arraydata[index.row()][index.column()]))
        elif role == Qt.TextAlignmentRole:
            if col in [0, 6, 7, 8, 9, 10, 14, 15, 16, 17, 18, 19, 20, 21, 22,
                       23, 23, 24]:
                return QVariant(int(Qt.AlignRight | Qt.AlignVCenter))
            if col in [11, 12, 13]:
                return QVariant(int(Qt.AlignCenter | Qt.AlignVCenter))
            return QVariant(int(Qt.AlignLeft | Qt.AlignVCenter))
        elif role == Qt.BackgroundColorRole:
            if 0 == index.row() % 2:
                c = QVariant(QColor(235, 245, 255))
            else:
                c = QVariant(QColor(250, 250, 250))
            if sb[19] < 9:
                c = QVariant(QColor(255, 255, 0))
            if sb[20] == 0:
                c = QVariant(QColor(255, 110, 110))
            return c
        elif role == Qt.FontRole:
            if col in [0, 18, 20]:
                return QVariant(QFont("Cantarel", 10, QFont.Bold))

        return QVariant()

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerdata[col])
        return QVariant()

    # noinspection PyPep8Naming
    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.arraydata = sorted(self.arraydata, key=operator.itemgetter(Ncol))
        if order == Qt.DescendingOrder:
            self.arraydata.reverse()
        self.emit(SIGNAL("layoutChanged()"))


def setpwv(p0):
    e1 = "%.2f" % Wto.pd.np.around(p0, decimals=2)
    e = e1[-1]
    c = e1[:-1]
    if 0 <= int(e) < 3:
        e = '0'
        p = float(c + e)
    elif 3 <= int(e) < 7:
        e = '5'
        p = float(c + e)
    else:
        p = float(c) + 0.1

    return Wto.pd.np.around(p, decimals=2)