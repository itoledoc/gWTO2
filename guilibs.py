# -*- coding: utf-8 -*-

"""
Module implementing MainWindow.
"""

import operator
import datetime
import csv
import numpy as np
import ephem
import subprocess
from observability import observable
from readEPT import read_data
from sb_dat_handler import checkaots, update_sbdata, priority
from QueryUtil import CalibratorCatalog

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from Ui_wto_gui import Ui_MainWindow

alma1 = ephem.Observer()
alma1.lat = '-23.0262015'
alma1.long = '-67.7551257'
alma1.elev = 5060

class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None, alma=alma1):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.lastrun = datetime.datetime.utcnow()
        self.lastrunstr = self.lastrun.strftime('%Y%M%d%H%m%S')
        self.alma = alma
        self.config_array = self.confArrayBox.currentText()
        self.pwv = self.spinPwv.value()
        self.min_trans = self.spinTrans.value()
        self.min_ha = self.spinMinHA.value()
        self.max_ha = self.spinMaxHA.value()
        self.min_elev = self.spinpElev.value()
        self.alma.date = self.dateTimeBox.dateTime().toPyDateTime()
        self.sb_database = read_data()
        self.sb_database, self.target_dat, self.versions = checkaots(
            self.sb_database, self.alma.date)
        # self.catalogue = CalibratorCatalog(self.alma.date.datetime(), self.alma)
        print self.alma.date, self.config_array, self.pwv, self.min_trans
        print self.min_ha, self.max_ha, self.min_elev
    
    @pyqtSignature("QDateTime")
    def on_dateTimeBox_dateTimeChanged(self, date):
        """
        Slot documentation goes here.
        """
        self.alma.date = date.toPyDateTime()
        lst = self.alma.sidereal_time()
        lst_time = datetime.datetime.strptime(str(lst), '%H:%M:%S.%f').time()
        self.timeEdit.setTime(QTime(lst_time.hour, lst_time.minute, lst_time.second))
        # self.catalogue.setdate(self.alma.date.datetime())

    @pyqtSignature("bool")
    def on_pushButton_clicked(self, checked):
        """
        Slot documentation goes here.
        """
        date = datetime.datetime.utcnow()
        self.dateTimeBox.setDateTime(QDateTime(QDate(date.date().year, date.date().month, date.date().day), QTime(date.time().hour, date.time().minute, date.time().second)))
        self.dateTimeBox.setTime(QTime(date.time().hour, date.time().minute, date.time().second))
        self.alma.date = date
        lst = self.alma.sidereal_time()
        lst_time = datetime.datetime.strptime(str(lst), '%H:%M:%S.%f').time()
        self.timeEdit.setTime(QTime(lst_time.hour, lst_time.minute, lst_time.second))
        # self.catalogue.setdate(self.alma.date.datetime())

    @pyqtSignature("")
    def on_actionSave_All_SBs_output_activated(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        fname = QFileDialog.getSaveFileName(
            None,
            QString(),
            self.trUtf8("allsbs.tsv"),
            QString(),
            None)
        csvfile = open(fname, 'w')
        csvwriter = csv.writer(csvfile, delimiter='\t', quotechar='|',
                               quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(self.head_dataall)
        for i in self.dataall:
            csvwriter.writerow(i)
        csvfile.close()

    @pyqtSignature("bool")
    def on_runButton_clicked(self, checked):
        """
        Slot documentation goes here.
        """

        progress = QProgressDialog(self)
        progress.setLabelText('Running WTO...')
        progress.show()
        progress.setAutoClose(True)
        progress.setMaximum(6)
        QCoreApplication.processEvents()

        self.config_array = self.confArrayBox.currentText()
        if 'All' in self.config_array:
            self.config_array = 'all'
        elif 'No filter' in self.config_array:
            self.config_array = ''
        self.pwv = self.spinPwv.value()
        self.min_trans = self.spinTrans.value()
        self.min_ha = self.spinMinHA.value()
        self.max_ha = self.spinMaxHA.value()
        self.min_elev = self.spinpElev.value()
        self.alma.date = self.dateTimeBox.dateTime().toPyDateTime()
        print self.alma.date, self.config_array, self.pwv, self.min_trans
        print self.min_ha, self.max_ha, self.min_elev

        self.sb_database, self.target_dat, self.versions = update_sbdata(self.sb_database, self.target_dat, self.alma.date, self.versions)
        progress.setValue(1)
        QCoreApplication.processEvents()

        self.priority_12m, self.sb_database_12m = priority(self.sb_database, pwv=self.pwv, conf=self.config_array, tran=self.min_trans)
        self.observability_12m = observable(self.target_dat, self.priority_12m, ALMA=self.alma, date=self.alma.date, horizon=str(self.min_elev))

        dataALL = np.copy(self.sb_database_12m)

        self.priority_7m, self.sb_database_7m = priority(self.sb_database, pwv=self.pwv, arr='7m', tran=self.min_trans)
        self.observability_7m = observable(self.target_dat, self.priority_7m, ALMA=self.alma, date=self.alma.date, horizon=str(self.min_elev + 0))

        progress.setValue(2)
        QCoreApplication.processEvents()

        self.priority_tp, self.sb_database_tp = priority(self.sb_database, pwv=self.pwv, arr='TP', tran=self.min_trans)
        self.observability_tp = observable(self.target_dat, self.priority_tp, ALMA=self.alma, date=self.alma.date, horizon=str(self.min_elev))

        progress.setValue(3)
        QCoreApplication.processEvents()

        c = 0
        for sb in dataALL:
            if sb['whynot'] == 'Available' and self.sb_database_7m[c]['whynot'] != 'Available':
                sb['whynot'] = self.sb_database_7m[c]['whynot']
            if sb['whynot'] == 'Available' and self.sb_database_tp[c]['whynot'] != 'Available':
                sb['whynot'] = self.sb_database_tp[c]['whynot']
            if sb['trans'] == 0. and self.sb_database_7m[c]['trans'] != 0:
                sb['trans'] = self.sb_database_7m[c]['trans']
            if sb['trans'] == 0. and self.sb_database_tp[c]['trans'] != 0:
                sb['trans'] = self.sb_database_tp[c]['trans']
            c += 1

        sbtype = [
            ('Priority', 'f4'), ('SB Name', 'a40'), ('projCode', 'a30'), ('uid', 'a25'),
            ('Exec', 'a6'), ('Rank', 'i2'), ('Band', 'a10'), ('Freq', 'f4'),
            ('SB Status', 'a20'), ('RA', 'a10'), ('DEC', 'a10'), ('HA', 'a10'),
            ('Elev', 'a10'), ('Sets in [h]', 'a10'), ('Transmision', 'f4'),
            ('ExEx.', 'i2'), ('QA0 Pass', 'i2'), ('QA0 Wait', 'i2'),
            ('arrayConf', 'a50'), ('Calibrators', 'a40'), ('Mode', 'a40'), ('maxPWV', 'f4')]

        sbtypetc = [
            ('Priority', 'f4'), ('SB Name', 'a40'), ('projCode', 'a30'), ('uid', 'a25'),
            ('Executive', 'a6'), ('Rank', 'i2'), ('Band', 'a10'), ('Freq', 'f4'),
            ('SB Status', 'a20'), ('RA', 'a10'), ('DEC', 'a10'), ('HA', 'a10'),
            ('Elev', 'a10'), ('Sets in [h]', 'a10'), ('Transmision', 'f4'),
            ('ExEx', 'i2'), ('QA0 Pass', 'i2'), ('QA0 Wait', 'i2'),
            ('Why TC', 'a50'), ('arrayConf', 'a50'), ('Calibrators', 'a40'), ('Mode', 'a40'), ('maxPWV', 'f4')]

        table_data_12m = np.zeros(0, dtype=sbtype)
        table_data_7m = np.zeros(0, dtype=sbtype)
        table_data_tp = np.zeros(0, dtype=sbtype)
        table_data_tc = np.zeros(0, dtype=sbtypetc)

        for sb in self.priority_12m:
            if sb['schedUid'] in self.observability_12m.keys():
                sb_dat = self.sb_database_12m[self.sb_database_12m['schedUid'] == sb['schedUid']][0]
                stat = sb_dat['sbStatus']
                sbna = sb_dat['sbname']
                obser = self.observability_12m[sb['schedUid']]
                tc = sb_dat['tc']
                ha = calc_ha(obser[2], obser[3])
                remaining = str(obser[1])
                lstr = str(datetime.time(int(obser[5].split(':')[0]), int(obser[5].split(':')[1]),
                                         int(obser[5].split(':')[2].split('.')[0])))
                lsts = str(datetime.time(int(obser[6].split(':')[0]), int(obser[6].split(':')[1]),
                                         int(obser[6].split(':')[2].split('.')[0])))
                ind = (self.sb_database_12m['schedUid'] == sb['schedUid']).tostring().find('\x01')
                dataALL[ind]['rise_LST'] = lstr
                dataALL[ind]['set_LST'] = lsts
                modeobs = 'Single Source'
                mosaic = False
                offsets = False
                if ((dataALL[ind]['whynot'] == 'Array Configuration not allowed') or
                        (dataALL[ind]['whynot'] == 'Is not array config. independent')):
                    continue
                sciencetar = 0
                for s in self.target_dat[sb['schedUid']]:
                    if s['intent'] == 'Science':
                        sciencetar += 1
                        if s['ismosaic'] == 'true':
                            mosaic = True
                        elif s['pointings'] > 1:
                            offsets = True
                if sciencetar > 1:
                    modeobs = 'Multiple Sources'
                    if mosaic:
                        modeobs = modeobs + ' and mosaic.'
                    elif offsets:
                        modeobs = modeobs + ' and multiple pointings.'
                else:
                    if mosaic:
                        modeobs = 'Mosaic'
                    elif offsets:
                        modeobs = 'Multiple Pointings'

                if obser[1] < datetime.timedelta(0):
                    dataALL[ind]['whynot'] = 'Under minEL'
                    continue
                if obser[1] < datetime.timedelta(hours=1):
                    dataALL[ind]['whynot'] = 'Will set before one hour'
                    continue

                if ha < ephem.hours(str(self.min_ha)):
                    dataALL[ind]['whynot'] = 'Outside HA limits'
                    continue
                if ha > ephem.hours(str(self.max_ha)):
                    dataALL[ind]['whynot'] = 'Outside HA limits'
                    continue

                if dataALL[ind]['whynot'] == 'Transmission low':
                    continue

                if dataALL[ind]['whynot'] == 'PWV is 2 times higher than the pwv used in the SB':
                    continue

                if obser[0] > ephem.degrees(str(self.min_elev)) and tc == 'False':
                    calibrators = ''
                    print str(obser[3])[:-3], str(obser[4])[:-2], ephem.hours(str(sb_dat['RA'])), ephem.degrees(str(sb_dat['DEC']))
                    new_row = np.array(
                        [(sb['priority'], sbna, sb_dat['projCode'], sb_dat['schedUid'],
                          sb_dat['exec'], sb_dat['rank'], sb_dat['band'], sb_dat['repFreq'],
                          stat, str(obser[3])[:-3], str(obser[4])[:-2], str(ha), str(obser[0])[:-5], remaining, sb_dat['trans'],
                          sb_dat['reqExec'], sb_dat['QA0_Pass'], sb_dat['QA0_Wait'],
                          sb_dat['arrayConf'], calibrators, modeobs, sb_dat['pwv'])], dtype=sbtype)
                    table_data_12m = np.concatenate((table_data_12m, new_row))
                elif obser[0] > ephem.degrees(str(self.min_elev)) and tc != 'False':
                    print str(obser[3])[:-3], str(obser[4])[:-2], ephem.hours(str(sb_dat['RA'])), ephem.degrees(str(sb_dat['DEC']))
                    new_row = np.array(
                        [(sb['priority'], sbna, sb_dat['projCode'], sb_dat['schedUid'],
                          sb_dat['exec'], sb_dat['rank'], sb_dat['band'], sb_dat['repFreq'],
                          stat, str(obser[3])[:-3], str(obser[4])[:-2], str(ha), str(obser[0])[:-5], remaining, sb_dat['trans'],
                          sb_dat['reqExec'], sb_dat['QA0_Pass'], sb_dat['QA0_Wait'], tc,
                          sb_dat['arrayConf'], '', modeobs, sb_dat['pwv'])], dtype=sbtypetc)
                    table_data_tc = np.concatenate((table_data_tc, new_row))
                else:
                    dataALL[ind]['whynot'] = 'Under minEl'

        progress.setValue(4)
        QCoreApplication.processEvents()

        for sb in self.priority_7m:
            if sb['schedUid'] in self.observability_7m.keys():
                sb_dat = self.sb_database_7m[self.sb_database_7m['schedUid'] == sb['schedUid']][0]
                stat = sb_dat['sbStatus']
                sbna = sb_dat['sbname']
                obser = self.observability_7m[sb['schedUid']]
                tc = sb_dat['tc']
                ha = calc_ha(obser[2], obser[3])
                remaining = str(obser[1])
                lstr = str(datetime.time(int(obser[5].split(':')[0]), int(obser[5].split(':')[1]),
                                         int(obser[5].split(':')[2].split('.')[0])))
                lsts = str(datetime.time(int(obser[6].split(':')[0]), int(obser[6].split(':')[1]),
                                         int(obser[6].split(':')[2].split('.')[0])))
                ind = (self.sb_database_7m['schedUid'] == sb['schedUid']).tostring().find('\x01')
                dataALL[ind]['rise_LST'] = lstr
                dataALL[ind]['set_LST'] = lsts
                modeobs = 'Single Source'
                mosaic = False
                offsets = False
                sciencetar = 0

                for s in self.target_dat[sb['schedUid']]:
                    if s['intent'] == 'Science':
                        sciencetar += 1
                        if s['ismosaic'] == 'true':
                            mosaic = True
                        elif s['pointings'] > 1:
                            offsets = True
                if sciencetar > 1:
                    modeobs = 'Multiple Sources'
                    if mosaic:
                        modeobs = modeobs + ' and mosaic.'
                    elif offsets:
                        modeobs = modeobs + ' and multiple pointings.'
                else:
                    if mosaic:
                        modeobs = 'Mosaic'
                    elif offsets:
                        modeobs = 'Multiple Pointings'

                if obser[1] < datetime.timedelta(0):
                    dataALL[ind]['whynot'] = 'Under minEL'
                    continue
                if obser[1] < datetime.timedelta(hours=1):
                    dataALL[ind]['whynot'] = 'Will set before one hour'
                    continue

                if ha < ephem.hours(str(self.min_ha)):
                    dataALL[ind]['whynot'] = 'Outside HA limits'
                    continue
                if ha > ephem.hours(str(self.max_ha)):
                    dataALL[ind]['whynot'] = 'Outside HA limits'
                    continue

                if dataALL[ind]['whynot'] == 'Transmission low':
                    continue

                if dataALL[ind]['whynot'] == 'PWV is 2 times higher than the pwv used in the SB':
                    continue

                if obser[0] > ephem.degrees(str(self.min_elev + 0)) and tc == 'False':
                    print str(obser[3])[:-3], str(obser[4])[:-2], ephem.hours(str(sb_dat['RA'])), ephem.degrees(str(sb_dat['DEC']))
                    new_row = np.array(
                        [(sb['priority'], sbna, sb_dat['projCode'], sb_dat['schedUid'],
                          sb_dat['exec'], sb_dat['rank'], sb_dat['band'], sb_dat['repFreq'],
                          stat, str(obser[3])[:-3], str(obser[4])[:-2], str(ha), str(obser[0])[:-5], remaining, sb_dat['trans'],
                          sb_dat['reqExec'], sb_dat['QA0_Pass'], sb_dat['QA0_Wait'],
                          sb_dat['arrayConf'], '', modeobs, sb_dat['pwv'])], dtype=sbtype)
                    table_data_7m = np.concatenate((table_data_7m, new_row))
                else:
                    dataALL[ind]['whynot'] = 'Under minEl'

        progress.setValue(5)
        QCoreApplication.processEvents()

        for sb in self.priority_tp:
            if sb['schedUid'] in self.observability_tp.keys():
                sb_dat = self.sb_database_tp[self.sb_database_tp['schedUid'] == sb['schedUid']][0]
                stat = sb_dat['sbStatus']
                sbna = sb_dat['sbname']
                obser = self.observability_tp[sb['schedUid']]
                tc = sb_dat['tc']
                ha = calc_ha(obser[2], obser[3])
                remaining = str(obser[1])
                lstr = str(datetime.time(int(obser[5].split(':')[0]), int(obser[5].split(':')[1]),
                                         int(obser[5].split(':')[2].split('.')[0])))
                lsts = str(datetime.time(int(obser[6].split(':')[0]), int(obser[6].split(':')[1]),
                                         int(obser[6].split(':')[2].split('.')[0])))
                ind = (self.sb_database_tp['schedUid'] == sb['schedUid']).tostring().find('\x01')
                dataALL[ind]['rise_LST'] = lstr
                dataALL[ind]['set_LST'] = lsts
                modeobs = 'Single Source'
                mosaic = False
                offsets = False

                sciencetar = 0
                for s in self.target_dat[sb['schedUid']]:
                    if s['intent'] == 'Science':
                        sciencetar += 1
                        if s['ismosaic'] == 'true':
                            mosaic = True
                        elif s['pointings'] > 1:
                            offsets = True
                if sciencetar > 1:
                    modeobs = 'Multiple Sources'
                    if mosaic:
                        modeobs = modeobs + ' and mosaic.'
                    elif offsets:
                        modeobs = modeobs + ' and multiple pointings.'
                else:
                    if mosaic:
                        modeobs = 'Mosaic'
                    elif offsets:
                        modeobs = 'Multiple Pointings'

                if obser[1] < datetime.timedelta(0):
                    dataALL[ind]['whynot'] = 'Under minEL'
                    continue
                if obser[1] < datetime.timedelta(hours=1):
                    dataALL[ind]['whynot'] = 'Will set before one hour'
                    continue

                if ha < ephem.hours(str(self.min_ha)):
                    dataALL[ind]['whynot'] = 'Outside HA limits'
                    continue
                if ha > ephem.hours(str(self.max_ha)):
                    dataALL[ind]['whynot'] = 'Outside HA limits'
                    continue

                if dataALL[ind]['whynot'] == 'Transmission low':
                    continue

                if dataALL[ind]['whynot'] == 'PWV is 2 times higher than the pwv used in the SB':
                    continue

                if obser[0] == np.deg2rad(90.):
                    print sb, obser, self.target_dat[sb['schedUid']]
                    dataALL[ind]['whynot'] = 'TP special SB'
                    continue
                if obser[0] > ephem.degrees(str(self.min_elev)) and tc == 'False':
                    print str(obser[3])[:-3], str(obser[4])[:-2], ephem.hours(str(sb_dat['RA'])), ephem.degrees(str(sb_dat['DEC']))
                    new_row = np.array(
                        [(sb['priority'], sbna, sb_dat['projCode'], sb_dat['schedUid'],
                          sb_dat['exec'], sb_dat['rank'], sb_dat['band'], sb_dat['repFreq'],
                          stat, str(obser[3])[:-3], str(obser[4])[:-2], str(ha), str(obser[0])[:-5], remaining, sb_dat['trans'],
                          sb_dat['reqExec'], sb_dat['QA0_Pass'], sb_dat['QA0_Wait'],
                          sb_dat['arrayConf'], '', modeobs, sb_dat['pwv'])], dtype=sbtype)
                    table_data_tp = np.concatenate((table_data_tp, new_row))
                else:
                    dataALL[ind]['whynot'] = 'Under minEl'

        progress.setValue(6)
        QCoreApplication.processEvents()

        header = table_data_12m.dtype.names
        self.tmblc = MyTableModel(table_data_12m.tolist(), header, self)
        self.proxyBLC = QSortFilterProxyModel(self)
        self.proxyBLC.setSourceModel(self.tmblc)
        self.blc_view.setModel(self.proxyBLC)
        self.horizontalHeader = self.blc_view.horizontalHeader()
        self.horizontalHeader.setContextMenuPolicy(Qt.CustomContextMenu)
        self.horizontalHeader.customContextMenuRequested.connect(self.on_blcview_horizontalHeader_sectionClicked)
        self.blc_view.verticalHeader().setStretchLastSection(False)
        self.blc_view.setSortingEnabled(True)
        self.blc_view.sortByColumn(0, Qt.AscendingOrder)
        self.blc_view.resizeRowsToContents()
        for column in range(21):
            if column not in [0, 8, 13, 14, 15, 16, 17, 21]:
                self.blc_view.resizeColumnToContents(column)
            else:
                self.blc_view.setColumnWidth(column, 66)

        header = table_data_7m.dtype.names
        tm = MyTableModel(table_data_7m.tolist(), header, self)
        self.aca_view.setModel(tm)
        self.aca_view.verticalHeader().setStretchLastSection(False)
        self.aca_view.setSortingEnabled(True)
        self.aca_view.sortByColumn(0, Qt.AscendingOrder)
        self.aca_view.resizeRowsToContents()
        for column in range(21):
            if column not in [0, 8, 13, 14, 15, 16, 17, 21]:
                self.aca_view.resizeColumnToContents(column)
            else:
                self.aca_view.setColumnWidth(column, 66)

        header = table_data_tp.dtype.names
        tm = MyTableModel(table_data_tp.tolist(), header, self)
        self.tp_view.setModel(tm)
        self.tp_view.verticalHeader().setStretchLastSection(False)
        self.tp_view.setSortingEnabled(True)
        self.tp_view.sortByColumn(0, Qt.AscendingOrder)
        self.tp_view.resizeRowsToContents()
        for column in range(22):
            if column not in [0, 8, 13, 14, 15, 16, 17, 21]:
                self.tp_view.resizeColumnToContents(column)
            else:
                self.tp_view.setColumnWidth(column, 66)

        header = table_data_tc.dtype.names
        tm = MyTableModel(table_data_tc.tolist(), header, self)
        self.tc_view.setModel(tm)
        self.tc_view.verticalHeader().setStretchLastSection(False)
        self.tc_view.setSortingEnabled(True)
        self.tc_view.sortByColumn(0, Qt.AscendingOrder)
        self.tc_view.resizeRowsToContents()
        for column in range(23):
            if column not in [0, 8, 13, 14, 15, 16, 17, 22]:
                self.tc_view.resizeColumnToContents(column)
            else:
                self.tc_view.setColumnWidth(column, 66)

        header = dataALL.dtype.names
        self.head_dataall = header
        self.dataall = dataALL.tolist()
        tm = MyTableModel2(dataALL.tolist(), header, self)
        self.allsb_view.setModel(tm)
        self.allsb_view.verticalHeader().setStretchLastSection(False)
        self.allsb_view.setSortingEnabled(True)
        self.allsb_view.sortByColumn(2, Qt.AscendingOrder)
        self.allsb_view.resizeColumnsToContents()
        self.allsb_view.resizeRowsToContents()
        progress.close()


    @pyqtSlot(int)
    def on_blcview_horizontalHeader_sectionClicked(self, position):
        self.index = self.horizontalHeader.logicalIndexAt(position)
        self.menuValues = QMenu(self)
        self.signalMapper = QSignalMapper(self)
        valuesUnique = [self.tmblc.arraydata[row][self.index] for row in range(self.tmblc.rowCount(None))]

        actionAll = QAction("All", self)
        actionAll.triggered.connect(self.on_actionAll_triggered)
        self.menuValues.addAction(actionAll)
        self.menuValues.addSeparator()

        for actionNumber, actionName in enumerate(sorted(list(set(valuesUnique)))):
            action = QAction(str(actionName), self)
            self.signalMapper.setMapping(action, actionNumber)
            action.triggered.connect(self.signalMapper.map)
            self.menuValues.addAction(action)

        self.signalMapper.mapped.connect(self.on_signalMapper_mapped)

        headerPos = self.horizontalHeader.mapToGlobal(position)

        posY = headerPos.y()
        posX = headerPos.x()

        self.menuValues.exec_(QPoint(posX, posY))

    @pyqtSlot(int)
    def on_signalMapper_mapped(self, i):
        stringAction = self.signalMapper.mapping(i).text()
        filterColumn = self.index
        filterString = QRegExp(stringAction,
                                        Qt.CaseSensitive,
                                        QRegExp.FixedString
                                        )

        self.proxyBLC.setFilterRegExp(filterString)
        self.proxyBLC.setFilterKeyColumn(filterColumn)

    @pyqtSlot()
    def on_actionAll_triggered(self):
        filterColumn = self.index
        filterString = QRegExp("",
                                        Qt.CaseInsensitive,
                                        QRegExp.RegExp
                                        )
        self.proxyBLC.setFilterRegExp(filterString)
        self.proxyBLC.setFilterKeyColumn(filterColumn)


    @pyqtSignature("")
    def closeEvent(self, event):
        #subprocess.call("rm -rf %s" % self.path, shell=True)
        event.accept()

    @pyqtSignature("double")
    def on_spinPwv_valueChanged(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.pwv = p0
        if self.pwv <= 0.6:
            self.min_trans = 0.5
            self.spinTrans.setValue(0.5)
        else:
            self.min_trans = 0.7
            self.spinTrans.setValue(0.7)
    
    @pyqtSignature("QString")
    def on_confArrayBox_currentIndexChanged(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.config_array = self.confArrayBox.currentText()

    
    @pyqtSignature("double")
    def on_spinTrans_valueChanged(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.min_trans = p0
    
    @pyqtSignature("double")
    def on_spinMinHA_valueChanged(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.min_ha = p0
    
    @pyqtSignature("int")
    def on_spinpElev_valueChanged(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.min_elev = p0
    
    @pyqtSignature("double")
    def on_spinMaxHA_valueChanged(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.max_ha = p0
    
    @pyqtSignature("")
    def on_actionHelp_activated(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("")
    def on_actionAbout_activated(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("")
    def on_actionSee_prioriy_weights_activated(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("")
    def on_actionPriority_Weights_activated(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError


class MyTableModel(QAbstractTableModel):
    def __init__(self, datain, headerdata, parent=None, *args):
        """ datain: a list of lists
            headerdata: a list of strings
        """
        QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = datain
        self.headerdata = headerdata

    def rowCount(self, parent):
        return len(self.arraydata)

    def columnCount(self, parent):
        return len(self.arraydata[0])

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        sb = self.arraydata[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 11 or col == 13:
                if sb[col][0] == '-':
                    neg = '-'
                    ha = QTime.fromString(sb[col][1:], 'h:m:s.z')
                else:
                    neg = ''
                    ha = QTime.fromString(sb[col], 'h:m:s.z')
                hastr = QString("%1").arg(neg + ha.toString('h:mm'))
                return QVariant(hastr)
            elif col == 0 or col == 14:
                return QVariant(QString("%1").arg(sb[col], 0, 'f', 2))
            elif col == 7:
                return QVariant(QString('%1').arg(sb[col], 0, 'f', 0))
            else:
                return QVariant(self.arraydata[index.row()][index.column()])
        elif role == Qt.TextAlignmentRole:
            if col in [7, 9, 10, 11, 12]:
                return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))
            elif col in [0, 4, 5, 6, 8, 13, 15, 16, 17]:
                return QVariant(int(Qt.AlignCenter|Qt.AlignVCenter))
            return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
        elif role == Qt.BackgroundColorRole:
            if sb[0] > 50:
                return QVariant(QColor(255, 215, 0))
            else:
                return QVariant(QColor(250, 250, 250))
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


class MyTableModel2(QAbstractTableModel):
    def __init__(self, datain, headerdata, parent=None, *args):
        """ datain: a list of lists
            headerdata: a list of strings
        """
        QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = datain
        self.headerdata = headerdata

    def rowCount(self, parent):
        return len(self.arraydata)

    def columnCount(self, parent):
        return len(self.arraydata[0])

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        sb = self.arraydata[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            return QVariant(self.arraydata[index.row()][index.column()])
        elif role == Qt.BackgroundColorRole:
            if sb[24] == 'QA0Pass count = ExEx count':
                return QVariant(QColor(153, 204, 255))
            elif sb[24] == 'SB in FullyObserved Status':
                return QVariant(QColor(153, 204, 255))
            elif sb[24] != 'Available':
                return QVariant(QColor(255, 176, 176))
            else:
                return QVariant(QColor(250, 250, 250))
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


def calc_ha(lst, ra):
    ha = lst - ra
    if ephem.hours(ha) > ephem.hours('12'):
        return ephem.hours(ha - ephem.hours('24'))
    elif ephem.hours(ha) < ephem.hours('-12'):
        return ephem.hours(ha + ephem.hours('24'))
    else:
        return ephem.hours(ha)
