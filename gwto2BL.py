# -*- coding: utf-8 -*-

"""
Module implementing BLMainWindow.
"""
import operator
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import wtoAlgorithm as WTO

import ephem

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
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
from arrayCheck2 import arrayCheck2

class BLMainWindow(QMainWindow, Ui_BLMainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None, path='/.wto/', source=None, forcenew=False):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.alma = alma
        self.datas = WTO.WtoAlgorithm(path=path, source=source, forcenew=False)
        self.datas.set_pwv(self.pwv_spin.value())
        self.datas.set_minha(self.minha_spin.value())
        self.datas.set_maxha(self.maxha_spin.value())
        self.datas.horizon = self.horizon_spin.value()
        self.datas.date = self.date_datetime.dateTime().toPyDateTime()
        self.datas.num_ant = self.antennas_spin.value()
        self.datas.set_bl_prop(array_name=None)
        self.array_ar_spin.setValue(self.datas.array_ar)

        print self.datas.date, self.datas.pwv, self.datas.minha, self.datas.maxha
        self.datas.horizon, type(self.datas.horizon)
    
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
        lst_time = WTO.datetime.strptime(str(lst), '%H:%M:%S.%f').time()
        self.lst_spin.setTime(QTime(lst_time.hour, lst_time.minute, lst_time.second))
    
    @pyqtSignature("int")
    def on_horizon_spin_valueChanged(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.datas.horizon = p0
    
    @pyqtSignature("int")
    def on_minha_spin_valueChanged(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.datas.minha = p0
    
    @pyqtSignature("double")
    def on_pwv_spin_valueChanged(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.datas.pwv = p0
    
    @pyqtSignature("")
    def on_B04_b_clicked(self):
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
    
    @pyqtSignature("QString")
    def on_blarrays_combo_activated(self):
        """
        Slot documentation goes here.
        """
        self.datas.array_name = self.blarrays_combo.currentText()
        self.stdarrays_combo.setCurrentIndex(0)
        self.antennas_spin.setReadOnly(True)
        self.datas.set_bl_prop(array_name=self.datas.array_name)
        self.pop = arrayCheck2(ruv=self.datas.ruv, num_ant=self.datas.num_ant)
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
        print self.datas.array_name, self.datas.array_ar, self.datas.num_ant

    
    @pyqtSignature("")
    def on_B03_b_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("bool")
    def on_B03_b_toggled(self, checked):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("")
    def on_B06_b_clicked(self):
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
    
    @pyqtSignature("")
    def on_B07_b_clicked(self):
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
    
    @pyqtSignature("")
    def on_B08_b_clicked(self):
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
    def on_now_button_clicked(self):
        """
        Slot documentation goes here.
        """
        date = WTO.datetime.utcnow()
        self.date_datetime.setDateTime(QDateTime(QDate(date.date().year, date.date().month, date.date().day),
                                               QTime(date.time().hour, date.time().minute, date.time().second)))
        self.date_datetime.setTime(QTime(date.time().hour, date.time().minute, date.time().second))
        self.datas.date = date
        self.datas.alma.date = self.datas.date
        lst = self.datas.alma.sidereal_time()
        lst_time = WTO.datetime.strptime(str(lst), '%H:%M:%S.%f').time()
        self.lst_spin.setTime(QTime(lst_time.hour, lst_time.minute, lst_time.second))
        self.datas.query_arrays()
        arrays = self.datas.bl_arrays.AV1.values
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
        self.pop = arrayCheck2(ruv=self.datas.ruv, num_ant=self.datas.num_ant)
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
        print self.datas.array_name, self.datas.array_ar, self.datas.num_ant

    @pyqtSignature("int")
    def on_antennas_spin_valueChanged(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.datas.num_ant = p0
        print self.datas.array_name, self.datas.array_ar, self.datas.num_ant
    
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
    
    @pyqtSignature("")
    def on_B09_b_clicked(self):
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
        raise NotImplementedError
    
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
        if self.datas.array_name == 'Current Conf.':
            self.datas.array_name = None
            self.antennas_spin.setReadOnly(False)
            self.datas.set_bl_prop(array_name=None)
        else:
            self.datas.set_bl_prop(array_name=str(self.datas.array_name))
        self.array_ar_spin.setValue(self.datas.array_ar)
        self.antennas_spin.setValue(self.datas.num_ant)
        print self.datas.array_name, self.datas.array_ar, self.datas.num_ant


    @pyqtSignature("")
    def on_run_button_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet

        self.datas.update()
        self.datas.selector('12m')
        self.datas.scorer('12m')
        std12 = self.datas.score12m.sort(
            'score', ascending=False).query('isPolarization == False')[
                    ['score', 'CODE', 'SB_UID', 'name', 'SB_state', 'band',
                     'maxPWVC', 'HA', 'elev', 'etime', 'execount', 'Total',
                     'arrayMinAR', 'arcorr', 'arrayMaxAR', 'tsysfrac', 'blfrac',
                     'frac','sb_array_score', 'sb_cond_score', 'RA', 'DEC',
                     'isTimeConstrained','integrationTime',
                     'PRJ_ARCHIVE_UID']]
        if not self.B03_b.isChecked():
            std12 = std12.query('band != "ALMA_RB_03"')
        if not self.B04_b.isChecked():
            std12 = std12.query('band != "ALMA_RB_04"')
        if not self.B06_b.isChecked():
            std12 = std12.query('band != "ALMA_RB_06"')
        if not self.B07_b.isChecked():
            std12 = std12.query('band != "ALMA_RB_07"')
        if not self.B08_b.isChecked():
            std12 = std12.query('band != "ALMA_RB_08"')
        if not self.B09_b.isChecked():
            std12 = std12.query('band != "ALMA_RB_09"')

        print std12.head(10)
        std12n = std12.to_records(index=False)
        header = std12n.dtype.names
        self.tmstd12 = MyTableModel(std12n, header, self)
        self.proxyBLC = QSortFilterProxyModel(self)
        self.proxyBLC.setSourceModel(self.tmstd12)
        self.bl_sheet.setModel(self.proxyBLC)
        self.horizontalHeader = self.bl_sheet.horizontalHeader()
        self.horizontalHeader.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.horizontalHeader.customContextMenuRequested.connect(self.on_bl_sheet_horizontalHeader_sectionClicked)
        self.bl_sheet.verticalHeader().setStretchLastSection(False)
        self.bl_sheet.setSortingEnabled(True)
        self.bl_sheet.sortByColumn(0, Qt.DescendingOrder)
        self.bl_sheet.resizeRowsToContents()
        for column in range(25):
            if column in [1, 2, 3]:
                self.bl_sheet.resizeColumnToContents(column)
            else:
                self.bl_sheet.setColumnWidth(column, 66)


class MyTableModel(QAbstractTableModel):
    def __init__(self, datain, headerdata, parent=None):
        """ datain: a list of lists
            headerdata: a list of strings
        """
        QAbstractTableModel.__init__(self, parent)
        self.arraydata = datain
        self.headerdata = headerdata

    def rowCount(self, parent):
        return len(self.arraydata)

    def columnCount(self, parent):
        return len(self.arraydata[0])

    def data(self, index, role):
        if not index.isValid():
            print "whaat?"
            return QVariant()
        sb = self.arraydata[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            return QVariant(str(self.arraydata[index.row()][index.column()]))
        elif role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
        # elif role == Qt.BackgroundColorRole:
        #     if sb[0] > 50:
        #         return QVariant(QColor(255, 215, 0))
        #     else:
        #         return QVariant(QColor(250, 250, 250))
        return QVariant()

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerdata[col])
        return QVariant()

    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.arraydata = sorted(self.arraydata, key=operator.itemgetter(Ncol))
        if order == Qt.DescendingOrder:
            self.arraydata.reverse()
        self.emit(SIGNAL("layoutChanged()"))
