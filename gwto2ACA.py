# -*- coding: utf-8 -*-

"""
Module implementing ACAMainWindow.
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


from Ui_gwto2ACA import Ui_ACAMainWindow


class ACAMainWindow(QMainWindow, Ui_ACAMainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None, path='/.wto_aca/', source=None,
                 forceup=False):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.setupUi(self)
        self.alma = alma
        self.datas = Wto.WtoAlgorithm(path=path, source=source,
                                      forcenew=forceup)
        self.datas.set_pwv(self.pwv_spin.value())
        self.datas.set_minha(self.minha_spin.value())
        self.datas.set_maxha(self.maxha_spin.value())
        self.datas.horizon = self.horizon_spin.value()
        self.datas.date = self.date_datetime.dateTime().toPyDateTime()

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
        raise NotImplementedError\

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
        # TODO: not implemented yet
        raise NotImplementedError
    
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

    @pyqtSignature("int")
    def on_antennas_spin_valueChanged(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        # self.datas.num_ant = p0
        print "Implementing this change"


    @pyqtSignature("")
    def on_band9_b_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("bool")
    def on_band9_b_toggled(self, checked):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("int")
    def on_band9_b_stateChanged(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("")
    def on_band7_b_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("bool")
    def on_band7_b_toggled(self, checked):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("int")
    def on_band7_b_stateChanged(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("")
    def on_band8_b_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("bool")
    def on_band8_b_toggled(self, checked):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("int")
    def on_band8_b_stateChanged(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("")
    def on_band4_b_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("bool")
    def on_band4_b_toggled(self, checked):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("int")
    def on_band4_b_stateChanged(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("")
    def on_band6_b_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("bool")
    def on_band6_b_toggled(self, checked):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("int")
    def on_band6_b_stateChanged(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("")
    def on_band3_b_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("bool")
    def on_band3_b_toggled(self, checked):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("int")
    def on_band3_b_stateChanged(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("")
    def on_now_button_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        date = Wto.datetime.utcnow()
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

        progress = QProgressDialog(self)
        progress.setLabelText('Running WTO2...')
        progress.show()
        progress.setAutoClose(True)
        QCoreApplication.processEvents()

        self.datas.update()
        QCoreApplication.processEvents()
        print(
            self.datas.date, self.datas.pwv, self.datas.minha, self.datas.maxha,
            self.datas.horizon, self.datas.array_name, self.datas.array_ar,
            self.datas.num_ant
        )
        QCoreApplication.processEvents()
        self.datas.selector('7m')
        self.datas.scorer('7m')
        std7 = self.datas.score7m.sort(
            'score', ascending=False).query(
                'isPolarization == False and isTimeConstrained == False')[
                    ['score', 'CODE', 'SB_UID', 'name', 'SB_state', 'band',
                     'RA', 'DEC', 'HA', 'elev', 'etime', 'execount', 'Total',
                     'tsysfrac', 'blfrac', 'frac', 'sb_array_score',
                     'sb_cond_score', 'maxPWVC', 'arrayMinAR', 'arcorr',
                     'arrayMaxAR', 'integrationTime',
                     'PRJ_ARCHIVE_UID', 'grade']]

        if not self.B03_b.isChecked():
            std7 = std7.query('band != "ALMA_RB_03"')
        if not self.B04_b.isChecked():
            std7 = std7.query('band != "ALMA_RB_04"')
        if not self.B06_b.isChecked():
            std7 = std7.query('band != "ALMA_RB_06"')
        if not self.B07_b.isChecked():
            std7 = std7.query('band != "ALMA_RB_07"')
        if not self.B08_b.isChecked():
            std7 = std7.query('band != "ALMA_RB_08"')
        if not self.B09_b.isChecked():
            std7 = std7.query('band != "ALMA_RB_09"')

        std7.columns = Wto.pd.Index(
            [u'Score', u'CODE', u'SB UID', u'SB Name', u'SB State', u'Band',
             u'RA', u'DEC', u'HA', u'Elev.', u'Sets in', u'Exec. Req.',
             u'Exec. Done', u'TSysFrac', u'BLFrac', u'TotalFrac',
             u'Array Score', u'Cond. Score', u'maxPWVC', u'ArrayMinAR',
             u'ARcorr', u'ArrayMaxAR', u'TimeOnSource',
             u'PRJ UID', u'Grade'], dtype='object')

        print std7.head(10)
        std7n = std7.to_records(index=False)
        header = std7n.dtype.names
        self.tmstd7 = MyStdTableModel(std7n, header, self)
        self.proxyACA = QSortFilterProxyModel(self)
        self.proxyACA.setSourceModel(self.tmstd7)
        self.seven_sheet.setModel(self.proxyACA)
        self.horizontalHeader = self.seven_sheet.horizontalHeader()
        self.horizontalHeader.setContextMenuPolicy(Qt.CustomContextMenu)
        self.seven_sheet.verticalHeader().setStretchLastSection(False)
        self.seven_sheet.setSortingEnabled(True)
        self.seven_sheet.sortByColumn(0, Qt.DescendingOrder)
        self.seven_sheet.resizeRowsToContents()
        for column in range(25):
            if column in [1, 2, 3, 4, 5, 6, 7, 22]:
                self.seven_sheet.resizeColumnToContents(column)
            elif column in [11, 12, 16, 17, 19, 21]:
                self.seven_sheet.setColumnWidth(column, 80)
            else:
                self.seven_sheet.setColumnWidth(column, 66)

    @pyqtSignature("")
    def on_actionAll_SBs_triggered(self):
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
    
    @pyqtSignature("")
    def on_actionPlanning_triggered(self):
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
    
    @pyqtSignature("")
    def on_actionQuit_triggered(self):
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
    
    @pyqtSignature("")
    def on_run_button_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError


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
        return len(self.arraydata)

    def columnCount(self, parent):
        return len(self.arraydata[0])

    # noinspection PyTypeChecker
    def data(self, index, role):
        if not index.isValid():
            print "whaat?"
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
            elif col in [0, 13, 14, 15, 18, 19, 20, 21]:
                return QVariant(QString("%1").arg(sb[col], 0, 'f', 2))
            elif col in [9, 16, 17, 22]:
                return QVariant(QString("%1").arg(sb[col], 0, 'f', 1))
            elif col in [11, 12]:
                return QVariant(QString("%1").arg(sb[col], 0, 'i', 0))

            return QVariant(str(self.arraydata[index.row()][index.column()]))
        elif role == Qt.TextAlignmentRole:
            if col in [0, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                       20, 21, 22]:
                return QVariant(int(Qt.AlignRight | Qt.AlignVCenter))
            return QVariant(int(Qt.AlignLeft | Qt.AlignVCenter))
        elif role == Qt.BackgroundColorRole:
            if 0 == index.row() % 2:
                c = QVariant(QColor(235, 245, 255))
            else:
                c = QVariant(QColor(250, 250, 250))
            if sb[17] == 0:
                c = QVariant(QColor(255, 110, 110))
            return c
        elif role == Qt.FontRole:
            if col in [0, 15, 17]:
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