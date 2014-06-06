__author__ = 'itoledo'
__metaclass__ = type

import numpy as np
import pandas as pd
import csv
import cx_Oracle
import os
from lxml import objectify
from subprocess import call

conx_string = 'almasu/alma4dba@ALMA_ONLINE.OSF.CL'
conx_string_sco = 'almasu/alma4dba@ALMA_ONLINE.SCO.CL'


class WtoDatabase(object):

    def __init__(self, default='/.wto/', source=None, forcenew=False):

        self.path = os.environ['HOME'] + default
        self.wto_path = os.environ['WTO']
        self.sbxml = self.path + 'sbxml/'
        self.obsxml = self.path + 'obsxml/'
        self.preferences = pd.Series(
            ['obsproject.pandas', source, 'sciencegoals.pandas',
             'scheduling.pandas', 'special.list', 'pwvdata.pandas',
             'executive.pandas', 'sbxml_table.pandas'],
            index=['obsproject_table', 'source', 'sciencegoals_table',
                   'scheduling_table', 'special', 'pwv_data',
                   'executive_table', 'sbxml_table'])
        self.sql1 = str(
            "SELECT PRJ_ARCHIVE_UID,DELETED,PI,PRJ_NAME, "
            "CODE,PRJ_TIME_OF_CREATION,PRJ_SCIENTIFIC_RANK,PRJ_VERSION,"
            "PRJ_ASSIGNED_PRIORITY,PRJ_LETTER_GRADE,DOMAIN_ENTITY_STATE,"
            "OBS_PROJECT_ID "
            "FROM ALMA.BMMV_OBSPROJECT obs1, ALMA.OBS_PROJECT_STATUS obs2  "
            "WHERE regexp_like (CODE, '^201[23].*\.[AST]') "
            "AND (PRJ_LETTER_GRADE='A' OR PRJ_LETTER_GRADE='B' "
            "OR PRJ_LETTER_GRADE='C') "
            "AND obs2.OBS_PROJECT_ID = obs1.PRJ_ARCHIVE_UID")
        self.source = source
        self.new = forcenew
        self.states = ["Approved", "Phase1Submitted", "Broken", "Completed",
                       "Canceled", "Rejected"]

        self.connection = cx_Oracle.connect(conx_string)
        self.cursor = self.connection.cursor()

        self.sqlsched_proj = str(
            "SELECT * FROM SCHEDULING_AOS.OBSPROJECT "
            "WHERE regexp_like (CODE, '^201[23].*\.[AST]')")
        self.cursor.execute(self.sqlsched_proj)
        self.scheduling_proj = pd.DataFrame(
            self.cursor.fetchall(),
            columns=[rec[0] for rec in self.cursor.description])

        self.sqlsched_sb = str(
            "SELECT ou.OBSUNIT_UID,sb.NAME,sb.REPR_BAND,"
            "sb.SCHEDBLOCK_CTRL_EXEC_COUNT,sb.SCHEDBLOCK_CTRL_STATE,"
            "sb.MIN_ANG_RESOLUTION,sb.MAX_ANG_RESOLUTION,"
            "ou.OBSUNIT_PROJECT_UID "
            "FROM SCHEDULING_AOS.SCHEDBLOCK sb, SCHEDULING_AOS.OBSUNIT ou "
            "WHERE sb.SCHEDBLOCKID = ou.OBSUNITID AND sb.CSV = 0")
        self.cursor.execute(self.sqlsched_sb)
        self.scheduling_sb = pd.DataFrame(
            self.cursor.fetchall(),
            columns=[rec[0] for rec in self.cursor.description])

        if not self.new:
            try:
                self.obsproject = pd.read_pickle(
                    self.path + self.preferences.obsproject_table)
                self.sciencegoals = pd.read_pickle(
                    self.path + self.preferences.sciencegoals_table)
                self.schedblocks = pd.read_pickle(
                    self.path + self.preferences.sbxml_table)
                self.filter_c1()
                self.update()
            except IOError, e:
                print e
                self.new = True

        if self.new:
            call(['rm', '-rf', self.path])
            print self.path + ": creating preferences dir"
            os.mkdir(self.path)
            os.mkdir(self.sbxml)
            os.mkdir(self.obsxml)
            self.query_obsproject()
            self.populate_sciencegoals_sbxml()
            self.populate_schedblocks()

    def query_obsproject(self):
        states = self.states

        sql2 = str(
            "SELECT PROJECTUID,ASSOCIATEDEXEC "
            "FROM ALMA.BMMV_OBSPROPOSAL "
            "WHERE (CYCLE='2012.1' OR CYCLE='2013.1' OR CYCLE='2013.A' "
            "OR CYCLE='2012.A')")

        self.cursor.execute(sql2)
        self.executive = pd.DataFrame(
            self.cursor.fetchall(), columns=['PRJ_ARCHIVE_UID', 'EXEC'])

        if self.source is None:
            self.cursor.execute(self.sql1)
            df1 = pd.DataFrame(
                self.cursor.fetchall(),
                columns=[rec[0] for rec in self.cursor.description])
            self.obsproject = pd.merge(
                df1.query('DOMAIN_ENTITY_STATE not in states'), self.executive,
                on='PRJ_ARCHIVE_UID').set_index('CODE', drop=False)
        else:
            if type(self.source) is not str and type(self.source) is not list:
                print "The source should be a string or a list"
                return None
            try:
                if type(self.source) is str:
                    fp = open(self.source, 'r')
                    read_csv = csv.reader(fp)
                else:
                    read_csv = self.source

                c = 0
                for l in read_csv:
                    if type(self.source) is str:
                        l = l[0]
                    sql3 = self.sql1 + ' AND OBS1.PRJ_CODE = ' + '\'%s\'' % l
                    self.cursor.execute(sql3)
                    if c == 0:
                        df2 = pd.DataFrame(
                            self.cursor.fetchall(),
                            columns=[rec[0] for rec in self.cursor.description])
                    else:
                        df2.ix[c] = pd.Series(
                            self.cursor.fetchall()[0], index=df2.columns)
                    c += 1

                self.obsproject = pd.merge(
                    df2.query('DOMAIN_ENTITY_STATE not in states'),
                    self.executive,
                    on='PRJ_ARCHIVE_UID').set_index('CODE', drop=False)
            except IOError:
                print "Source filename does not exist"
                return None

        timestamp = pd.Series(
            np.zeros(len(self.obsproject), dtype=object),
            index=self.obsproject.index)
        self.obsproject['timestamp'] = timestamp
        self.obsproject['obsproj'] = pd.Series(
            np.zeros(len(self.obsproject), dtype=object),
            index=self.obsproject.index)
        codes = self.obsproject.CODE.tolist()
        for c in codes:
            self.get_obsproject(c)
        print len(self.obsproject)
        self.filter_c1()
        print len(self.obsproject)
        self.obsproject.to_pickle(
            self.path + self.preferences.obsproject_table)

    def update(self):
        self.cursor.execute(self.sqlsched_proj)
        self.scheduling_proj = pd.DataFrame(
            self.cursor.fetchall(),
            columns=[rec[0] for rec in self.cursor.description])
        self.cursor.execute(self.sqlsched_sb)
        self.scheduling_sb = pd.DataFrame(
            self.cursor.fetchall(),
            columns=[rec[0] for rec in self.cursor.description])
        newest = self.obsproject.timestamp.max()
        changes = []
        sql = str(
            "SELECT ARCHIVE_UID, TIMESTAMP FROM ALMA.XML_OBSPROJECT_ENTITIES "
            "WHERE TIMESTAMP > to_date('%s', 'YYYY-MM-DD HH24:MI:SS')" %
            str(newest).split('.')[0])
        self.cursor.execute(sql)
        new_data = self.cursor.fetchall()
        if len(new_data) == 0:
            return 0
        else:
            for n in new_data:
                if n[1] <= newest:
                    continue
                puid = n[0]
                try:
                    code = self.obsproject.query(
                        'PRJ_ARCHIVE_UID == puid').ix[0, 'CODE']
                    if code in self.checked.CODE.tolist():
                        changes.append(code)
                    else:
                        continue
                except IndexError:
                    self.cursor.execute(
                        self.sql1 + " AND OBS1.PRJ_ARCHIVE_UID = '%s'" % puid)
                    row = list(self.cursor.fetchall()[0])
                    code = row[4]
                    if code not in self.checked.CODE.tolist():
                        continue
                    self.cursor.execute(
                        "SELECT ASSOCIATEDEXEC FROM ALMA.BMMV_OBSPROPOSAL "
                        "WHERE PROJECTUID = '%s'" % puid)
                    row.append(self.cursor.fetchall()[0][0])
                    row.append(n[1])
                    row.append(self.obsproject.ix[0, 'obsproj'])

                    self.obsproject.ix[code] = row
                    changes.append(code)
                self.get_obsproject(code)
            for code in changes:
                print "Project %s updated" % code
                self.row_sciencegoals(code)
                pidlist = self.sciencegoals.query(
                    'CODE == code').partId.tolist()
                for pid in pidlist:
                    sblist = self.sciencegoals.ix[pid].SBS
                    for sb in sblist:
                        print "Updating sb %s of project %s" % (sb, code)
                        self.row_schedblocks(sb, pid)
            self.filter_c1()
            self.schedblocks.to_pickle(
                self.path + self.preferences.sbxml_table)
            self.sciencegoals.to_pickle(
                self.path + self.preferences.sciencegoals_table)
            self.obsproject.to_pickle(
                self.path + self.preferences.obsproject_table)

        newest = self.schedblocks.timestamp.max()
        sql = str(
            "SELECT ARCHIVE_UID, TIMESTAMP FROM ALMA.XML_SCHEDBLOCK_ENTITIES "
            "WHERE TIMESTAMP > to_date('%s', 'YYYY-MM-DD HH24:MI:SS')" %
            str(newest).split('.')[0])
        print newest
        self.cursor.execute(sql)
        new_data = self.cursor.fetchall()
        if len(new_data) == 0:
            return 0
        else:
            for n in new_data:
                if n[1] <= newest:
                    continue
                sbuid = n[0]
                print "Updating sb %s" % sbuid
                try:
                    pid = self.sciencegoals.query(
                        'SB_UID == sbuid').ix[0, 'partId']
                except IndexError:
                    continue
                self.row_schedblocks(sbuid, pid)
            self.schedblocks.to_pickle(
                self.path + self.preferences.sbxml_table)

    def populate_sciencegoals_sbxml(self):
        try:
            type(self.sciencegoals)
            new = False
        except AttributeError:
            new = True
        codes = self.obsproject.CODE.tolist()
        print len(codes)
        for c in codes:
            self.row_sciencegoals(c, new=new)
            new = False
        self.sciencegoals.to_pickle(
            self.path + self.preferences.sciencegoals_table)

    def populate_schedblocks(self):
        new = True
        sbpartid = self.sciencegoals.index.tolist()
        sizel = len(sbpartid)
        c = 1
        for pid in sbpartid:
            sblist = self.sciencegoals.ix[pid].SBS
            for sb in sblist:
                self.row_schedblocks(sb, pid, new=new)
                new = False
            print "%d/%d ScienceGoals SBs ingested" % (c, sizel)
            c += 1

        self.schedblocks.to_pickle(
            self.path + self.preferences.sbxml_table)

    def row_sciencegoals(self, code, new=False):
        proj = self.obsproject.query('CODE == code').ix[0]
        obsproj = ObsProject(proj.obsproj, self.obsxml)
        assoc_sbs = obsproj.assoc_sched_blocks()
        try:
            for sg in range(len(obsproj.ObsProgram.ScienceGoal)):
                code = code
                sciencegoal = obsproj.ObsProgram.ScienceGoal[sg]
                partid = sciencegoal.ObsUnitSetRef.attrib['partId']
                ar = sciencegoal.PerformanceParameters.desiredAngularResolution.pyval
                arunit = sciencegoal.PerformanceParameters.desiredAngularResolution.attrib['unit']
                las = sciencegoal.PerformanceParameters.desiredLargestScale.pyval
                lasunit = sciencegoal.PerformanceParameters.desiredLargestScale.attrib['unit']
                bands = sciencegoal.requiredReceiverBands.pyval
                try:
                    ss = sciencegoal.SpectralSetupParameters.SpectralScan
                    isspectralscan = True
                except AttributeError:
                    isspectralscan = False
                useaca = sciencegoal.PerformanceParameters.useACA.pyval
                usetp = sciencegoal.PerformanceParameters.useTP.pyval

                if new:
                    self.sciencegoals = pd.DataFrame(
                        [(code, partid, ar, las, bands, isspectralscan,
                          useaca, usetp, assoc_sbs[partid])],
                        columns=['CODE', 'partId', 'AR', 'LAS', 'bands',
                                 'isSpectralScan', 'useACA', 'useTP', 'SBS'],
                        index=[partid])
                    new = False
                else:
                    self.sciencegoals.ix[partid] = (
                        code, partid, ar, las, bands, isspectralscan,
                        useaca, usetp, assoc_sbs[partid])

        except AttributeError:
            print "Project %s has not ObsUnitSets" % code
            return 0
        return 0

    def get_obsproject(self, code):
        print "Downloading Project %s obsproject.xml" % code
        self.cursor.execute(
            "SELECT TIMESTAMP, XMLTYPE.getClobVal(xml) "
            "FROM ALMA.XML_OBSPROJECT_ENTITIES "
            "WHERE ARCHIVE_UID = '%s'" % self.obsproject.ix[
                code, 'PRJ_ARCHIVE_UID'])
        data = self.cursor.fetchall()[0]
        xml_content = data[1].read()
        xmlfilename = code + '.xml'
        self.obsproject.loc[code, 'timestamp'] = data[0]
        filename = self.obsxml + xmlfilename
        io_file = open(filename, 'w')
        io_file.write(xml_content)
        io_file.close()
        self.obsproject.loc[code, 'obsproj'] = xmlfilename

    def row_schedblocks(self, sb_uid, partid, new=False):

        sql = "SELECT TIMESTAMP, XMLTYPE.getClobVal(xml) " \
              "FROM ALMA.xml_schedblock_entities " \
              "WHERE archive_uid = '%s'" % sb_uid
        self.cursor.execute(sql)
        data = self.cursor.fetchall()
        xml_content = data[0][1].read()
        filename = sb_uid.replace(':', '_').replace('/', '_') +\
            '.xml'
        io_file = open(self.sbxml + filename, 'w')
        io_file.write(xml_content)
        io_file.close()
        xml = filename
        if new:
            self.schedblocks = pd.DataFrame(
                [(sb_uid, partid, data[0][0], xml)],
                columns=['SB_UID', 'partId', 'timestamp', 'sb_xml'],
                index=[sb_uid])
        else:
            self.schedblocks.ix[sb_uid] = (sb_uid, partid, data[0][0], xml)

    def filter_c1(self):
        c1c2 = pd.read_csv(
            self.wto_path + 'conf/c1c2.csv', sep=',', header=0)
        c1c2.columns = pd.Index([u'CODE', u'Region', u'ARC', u'C2', u'P2G'],
                                dtype='object')
        toc2 = c1c2[c1c2.fillna('no').C2.str.contains('^Yes')]
        check_c1 = pd.merge(
            self.obsproject[self.obsproject.CODE.str.contains('^2012')],
            toc2, on='CODE')[['CODE']]
        check_c2 = self.obsproject[
            self.obsproject.CODE.str.contains('^2013')][['CODE']]
        self.checked = pd.concat([check_c1, check_c2])
        temp = pd.merge(
            self.obsproject, self.checked, on='CODE',
            copy=False).set_index('CODE', drop=False)
        self.obsproject = temp

class ObsProject(object):

    def __init__(self, xml_file, path='./'):
        """

        :param xml_file:
        :param path:
        """
        io_file = open(path + xml_file)
        tree = objectify.parse(io_file)
        io_file.close()
        data = tree.getroot()
        self.status = data.attrib['status']
        for key in data.__dict__:
            self.__setattr__(key, data.__dict__[key])

    def assoc_sched_blocks(self):
        """


        :return:
        """
        result = {}

        try:
            for sg in self.ObsProgram.ObsPlan.ObsUnitSet:
                sched_uid = []
                sgid = sg.attrib['entityPartId']
                for ous in sg.ObsUnitSet:
                    try:
                        for mous in ous.ObsUnitSet:
                            array_requested = mous.ObsUnitControl.attrib[
                                'arrayRequested']
                            try:
                                for sbs in mous.SchedBlockRef:
                                    if array_requested in 'TWELVE-M':
                                        sched_uid.append(
                                            sbs.attrib['entityId'])
                                    elif array_requested == 'SEVEN-M':
                                        sched_uid.append(
                                            sbs.attrib['entityId'])
                                    elif array_requested == 'TP-Array':
                                        sched_uid.append(
                                            sbs.attrib['entityId'])
                            except AttributeError:
                                # Member OUS does not have any SB created yet.
                                continue
                    except AttributeError:
                        print('Project %s has no member OUS in at least one '
                              'SG_OUS' % self.code)
                        continue
                result[sgid] = sched_uid
        except AttributeError:
            print "Project %s has no Science Goal OUS" % self.code
        return result

    def import_sched_blocks(self):
        pass


class SchedBlocK(object):

    def __init__(self, xml_file, path='./'):
        """

        :param xml_file:
        :param path:
        """
        io_file = open(path + xml_file)
        tree = objectify.parse(io_file)
        io_file.close()
        self.data = tree.getroot()