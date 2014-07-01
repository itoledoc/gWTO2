# -*- coding: utf-8 -*-

"""
Module implementing BLMainWindow.
"""

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
from arrayCheck import ArrayCheck

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

        print self.datas.date, self.datas.pwv, self.datas.minha, self.datas.maxha
        self.datas.horizon, type(self.datas.horizon)
    
    @pyqtSignature("int")
    def on_maxha_spin_valueChanged(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
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
        raise NotImplementedError
    
    @pyqtSignature("int")
    def on_minha_spin_valueChanged(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("double")
    def on_pwv_spin_valueChanged(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
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
        print self.datas.array_name
        self.datas.set_bl_prop(array_name=self.datas.array_name)
        self.pop = ArrayCheck(ruv=self.datas.ruv, num_ant=self.datas.num_ant)
        self.pop.show()
    
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
    
    @pyqtSignature("")
    def on_antennas_spin_editingFinished(self):
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
        self.datas.array_name = self.blarrays_combo.currentText()
        print self.datas.array_name
        self.datas.set_bl_prop(array_name=self.datas.array_name)
        self.pop = ArrayCheck(ruv=self.datas.ruv, num_ant=self.datas.num_ant)
        self.pop.show()

    @pyqtSignature("int")
    def on_antennas_spin_valueChanged(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
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
        raise NotImplementedError
    
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
        if self.datas.array_name == 'Current Conf.':
            self.datas.array_name = None
        self.blarrays_combo.setCurrentIndex(0)
        print self.datas.array_name
    
    @pyqtSignature("")
    def on_run_button_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
