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
        self.source = source
        self.new = forcenew
        self.states = ["Approved", "Phase1Submitted", "Broken", "Completed",
                       "Canceled", "Rejected"]

        self.connection = cx_Oracle.connect(conx_string)
        self.cursor = self.connection.cursor()
        if self.new:
            call(['rm', '-rf', self.path])
            print self.path + ": creating preferences dir"
            os.mkdir(self.path)
            os.mkdir(self.sbxml)
            os.mkdir(self.obsxml)

    def update_obsproject(self):
        newest = self.obsprojects.timestamp.max()
        self.cursor.execute(
            "SELECT ARCHIVE_UID, TIMESTAMP FROM ALMA.XML_SCHEDBLOCK_ENTITIES"
            "WHERE TIMESTAMP > to_date('%s', 'YYYY-MM-DD HH24:MI:SS')" %
            str(newest).split('.')[0])
        new_data = self.cursor.fetchall()
        if len(new_data) == 0:
            return 0
        else:
            for n in new_data:
                puid = n[0]
                try:
                    code = self.obsproject.query(
                        'PRJ_ARCHIVE_UID == puid').ix[0, 'CODE']
                except IndexError:
                    self.cursor.execute(
                        "SELECT CODE FROM ALMA.BMMV_OBSPROJECT "
                        "WHERE PRJ_ARCHIVE_UID = '%s'" % puid)
                    code = self.cursor.fetchall()

    def query_obsproject(self):
        states = self.states
        self.sql1 = str(
            "SELECT PRJ_ARCHIVE_UID,DELETED,PI,PRJ_NAME, "
            "CODE,PRJ_TIME_OF_CREATION,PRJ_SCIENTIFIC_RANK,PRJ_VERSION,"
            "PRJ_ASSIGNED_PRIORITY,PRJ_LETTER_GRADE,DOMAIN_ENTITY_STATE,"
            "OBS_PROJECT_ID,PROJECT_WAS_TIMED_OUT "
            "FROM ALMA.BMMV_OBSPROJECT obs1, ALMA.OBS_PROJECT_STATUS obs2  "
            "WHERE regexp_like (CODE, '^201[23].*\.[AST]') "
            "AND (PRJ_LETTER_GRADE='A' OR PRJ_LETTER_GRADE='B' "
            "OR PRJ_LETTER_GRADE='C') "
            "AND obs2.OBS_PROJECT_ID = obs1.PRJ_ARCHIVE_UID")

        sql2 = str(
            "SELECT PROJECTUID,ASSOCIATEDEXEC "
            "FROM ALMA.BMMV_OBSPROPOSAL "
            "WHERE (CYCLE='2012.1' OR CYCLE='2013.1' OR CYCLE='2013.A' "
            "OR CYCLE='2012.A')")

        self.cursor.execute(sql2)
        executive = pd.DataFrame(
            self.cursor.fetchall(), columns=['PRJ_ARCHIVE_UID', 'EXEC'])

        if self.source is None:
            self.cursor.execute(sql1)
            df1 = pd.DataFrame(
                self.cursor.fetchall(),
                columns=[rec[0] for rec in self.cursor.description])
            self.obsproject = pd.merge(
                df1.query('DOMAIN_ENTITY_STATE not in states'), executive,
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
                    sql3 = sql1 + ' AND OBS1.PRJ_CODE = ' + '\'%s\'' % l
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
                    executive,
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

    def get_obsproject(self, code):
        self.cursor.execute(
            "SELECT TIMESTAMP, XMLTYPE.getClobVal(xml) "
            "FROM ALMA.XML_OBSPROJECT_ENTITIES "
            "WHERE ARCHIVE_UID = '%s'" %
            self.obsproject.ix[code, 'PRJ_ARCHIVE_UID'])
        data = self.cursor.fetchall()[0]
        xml_content = data[1].read()
        xmlfilename = code + '.xml'
        self.obsproject.loc[code, 'timestamp'] = data[0]
        filename = self.obsxml + xmlfilename
        io_file = open(filename, 'w')
        io_file.write(xml_content)
        io_file.close()
        self.obsproject.loc[code, 'obsproj'] = ObsProject(
            xmlfilename, path=self.obsxml)


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
                sched_uid_12m = []
                sched_uid_7m = []
                sched_uid_tp = []
                sgid = sg.attrib['entityPartId']
                for ous in sg.ObsUnitSet:
                    try:
                        for mous in ous.ObsUnitSet:
                            array_requested = mous.ObsUnitControl.attrib[
                                'arrayRequested']
                            try:
                                for sbs in mous.SchedBlockRef:
                                    if array_requested in 'TWELVE-M':
                                        sched_uid_12m.append(
                                            sbs.attrib['entityId'])
                                    elif array_requested == 'SEVEN-M':
                                        sched_uid_7m.append(
                                            sbs.attrib['entityId'])
                                    elif array_requested == 'TP-Array':
                                        sched_uid_tp.append(
                                            sbs.attrib['entityId'])
                            except AttributeError:
                                # Member OUS does not have any SB created yet.
                                continue
                    except AttributeError:
                        print('Project %s has no member OUS in at least one '
                              'SG_OUS' % self.code)
                        continue
                result[sgid] = [sched_uid_12m, sched_uid_7m, sched_uid_tp]
        except AttributeError:
            print "Project %s has no Science Goal OUS" % self.code

        return result

    def import_sched_blocks(self):
        pass