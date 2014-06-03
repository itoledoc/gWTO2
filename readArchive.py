__metaclass__ = type

import numpy as np
import pandas as pd
import csv
import cx_Oracle
import os
from lxml import objectify

conx_string = 'almasu/alma4dba@ALMA_ONLINE.OSF.CL'


class DataBase(object):

    def __init__(self, default='/.wto', source=None):

        """

        :param default:
        :param source:
        """
        self.path = os.environ['HOME'] + default
        self.sbxml = self.path + '/sbxml/'
        self.obsxml = self.path + '/obsxml/'
        self.new = False

        try:
            wto_ls = os.listdir(self.path)
            self.preferences = pd.read_csv(self.path + '/preferences.dat',
                                           sep=':', index_col=0).ix[:, 0]
            self.preferences.source = source
        except OSError:
            print self.path + " not found, creating preferences dir"
            os.mkdir(self.path)
            os.mkdir(self.sbxml)
            os.mkdir(self.obsxml)
            self.preferences = pd.Series(
                ['projects.pandas', source, 'not_ready_prj.pandas',
                 'scheduling.pandas', 'special.list', 'pwvdata.pandas'],
                index=[
                    'project_table', 'source', 'not_ready_prj_table',
                    'scheduling_table', 'special', 'pwv_data'])
            self.preferences.to_csv(self.path + '/preferences.dat', sep=':',
                                    header=True)
            self.new = True

        if self.preferences.source is None and self.new:
            self.projects, self.not_ready_prj, self.scheduling = query_archive(
                path=self.obsxml)
        elif self.new:
            self.projects, self.not_ready_prj, self.scheduling = query_archive(
                source, path=self.obsxml)
        else:
            self.projects = pd.read_pickle(
                self.path + '/' + self.preferences.project_table)
            self.not_ready_prj = pd.read_pickle(
                self.path + '/' + self.preferences.not_ready_prj_table)
            self.scheduling = pd.read_pickle(
                self.path + '/' + self.preferences.scheduling_table)

        if self.new:
            self.projects['obsproj'] = pd.Series(
                np.zeros(len(self.projects), dtype=object),
                index=self.projects.index)
            for p in self.projects.index:
                obspro = ObsProject(p + '.xml', path=self.obsxml)
                self.projects.loc[p, 'obsproj'] = obspro
            self.projects.to_pickle(self.path + '/' +
                                    self.preferences.project_table)
            self.not_ready_prj.to_pickle(self.path + '/' +
                                         self.preferences.not_ready_prj_table)
            self.scheduling.to_pickle(self.path + '/' +
                                      self.preferences.scheduling_table)
            self.new = False

    def clean_ready(self):
        # TODO: Check if status has changed (use update_project)
        # TODO: Read cycle1 table, create cycle2 table
        # TODO: Return a table obsproject_r
        pass

    def update_project(self):

        # TODO: Ingest project status changes into self.projects
        # TODO: Remove new projects in self.projects from self.not_ready_prj

        """


        :return:
        """
        states = ["Approved", "Phase1Submitted", "Broken", "Completed",
                  "Canceled"]
        newest = self.projects.timestamp.max()
        sqln = "SELECT ARCHIVE_UID, TIMESTAMP, XMLTYPE.getClobVal(xml) " \
               "FROM ALMA.xml_obsproject_entities " \
               "WHERE TIMESTAMP > to_date('%s', 'YYYY-MM-DD HH24:MI:SS')" % \
               str(newest).split('.')[0]
        connection = cx_Oracle.connect(conx_string)
        cursor = connection.cursor()
        cursor.execute(sqln)
        new_data = cursor.fetchall()
        sql3 = "SELECT * FROM SCHEDULING_AOS.OBSPROJECT " \
               "WHERE regexp_like (CODE, '^201[23]\.1.*\.[AST]')"
        cursor.execute(sql3)
        self.scheduling = pd.DataFrame(
            cursor.fetchall(), columns=[rec[0] for rec in cursor.description])
        for n in new_data:
            update = n[1] > newest

            if not update:
                continue

            puid = n[0]
            index = self.projects.query('PRJ_ARCHIVE_UID == n[0]')
            sql1 = "SELECT PRJ_ARCHIVE_UID,DELETED,PI,PRJ_NAME,ARRAY," \
                   "PRJ_CODE,PRJ_TIME_OF_CREATION," \
                   "PRJ_SCIENTIFIC_RANK,PRJ_VERSION," \
                   "PRJ_ASSIGNED_PRIORITY,PRJ_LETTER_GRADE," \
                   "DOMAIN_ENTITY_STATE,OBS_PROJECT_ID," \
                   "PROJECT_WAS_TIMED_OUT " \
                   "FROM ALMA.BMMV_OBSPROJECT obs1, " \
                   "ALMA.OBS_PROJECT_STATUS obs2  " \
                   "WHERE regexp_like (CODE, '^201[23]\.1.*\.[AST]') " \
                   "AND (PRJ_LETTER_GRADE='A' OR PRJ_LETTER_GRADE='B' " \
                   "OR PRJ_LETTER_GRADE='C') " \
                   "AND OBS2.OBS_PROJECT_ID = OBS1.PRJ_ARCHIVE_UID " \
                   "AND OBS1.PRJ_ARCHIVE_UID = '%s'" % puid
            cursor.execute(sql1)

            try:
                new_row = list(cursor.fetchall()[0])
            except IndexError:
                continue

            code = new_row[5]
            sched_entry = self.scheduling.query(
                'OBSPROJECT_UID == puid')

            # if not in scheduling and status is not near ready, add to
            # not_ready_prj
            if len(sched_entry) == 0 and sched_entry.loc[0, 'STATUS'] in states:
                self.not_ready_prj.ix[code] = new_row
                continue

            # if
            if (code in self.not_ready_prj.CODE.tolist() and
                    new_row[11] not in states):
                self.not_ready_prj = self.not_ready_prj.query('CODE != code')
            new_row.append(n[1])
            xml_content = n[2].read()
            filename = self.obsxml + code + '.xml'
            io_file = open(filename, 'w')
            io_file.write(xml_content)
            io_file.close()
            obspro = ObsProject(code + '.xml', path=self.obsxml)
            new_row.append(obspro)
            self.projects.ix[code] = new_row

        connection.close()
        return 0


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
                                    if array_requested == 'TWELVE-M':
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
                        print ous.base
                        continue
                result[sgid] = [sched_uid_12m, sched_uid_7m, sched_uid_tp]
        except AttributeError:
            print self.code

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
        data = tree.getroot()
        for key in data.__dict__:
            self.__setattr__(key, data.__dict__[key])


def query_archive(source=None, path='./'):

    """

    :param source:
    :param path:
    :return:
    """
    connection = cx_Oracle.connect(conx_string)
    cursor = connection.cursor()
    sql1 = "SELECT PRJ_ARCHIVE_UID,DELETED,PI,PRJ_NAME,ARRAY,PRJ_CODE, " \
           "CODE,PRJ_TIME_OF_CREATION,PRJ_SCIENTIFIC_RANK,PRJ_VERSION," \
           "PRJ_ASSIGNED_PRIORITY,PRJ_LETTER_GRADE,DOMAIN_ENTITY_STATE," \
           "OBS_PROJECT_ID,PROJECT_WAS_TIMED_OUT " \
           "FROM ALMA.BMMV_OBSPROJECT obs1, ALMA.OBS_PROJECT_STATUS obs2  " \
           "WHERE regexp_like (CODE, '^201[23]\.1.*\.[AST]') " \
           "AND (PRJ_LETTER_GRADE='A' OR PRJ_LETTER_GRADE='B' " \
           "OR PRJ_LETTER_GRADE='C') " \
           "AND OBS2.OBS_PROJECT_ID = OBS1.PRJ_ARCHIVE_UID"

    sql3 = "SELECT * FROM SCHEDULING_AOS.OBSPROJECT " \
           "WHERE regexp_like (CODE, '^201[23]\.1.*\.[AST]')"
    cursor.execute(sql3)
    scheduling = pd.DataFrame(cursor.fetchall(),
                              columns=[rec[0] for rec in cursor.description])
    states = ["Approved", "Phase1Submitted", "Broken", "Completed", "Canceled"]

    if source is None:
        cursor.execute(sql1)
        df1 = pd.DataFrame(cursor.fetchall(),
                           columns=[rec[0] for rec in cursor.description])
        projects = df1.query(
            'DOMAIN_ENTITY_STATE not in states').set_index('PRJ_CODE')
        not_ready_projects = df1.query(
            'DOMAIN_ENTITY_STATE in states').set_index('PRJ_CODE')
    else:
        if type(source) is not str and type(source) is not list:
            print "The filename should be a string or a list"
            return None
        try:
            if type(source) is str:
                fp = open(source, 'r')
                read_csv = csv.reader(fp)
            else:
                read_csv = source
            c = 0
            for l in read_csv:
                if type(source) is str:
                    l = l[0]
                sql2 = sql1 + ' AND OBS1.PRJ_CODE = ' + '\'%s\'' % l
                cursor.execute(sql2)
                if c == 0:
                    df2 = pd.DataFrame(
                        cursor.fetchall(),
                        columns=[rec[0] for rec in cursor.description])
                else:
                    df2.ix[c] = pd.Series(cursor.fetchall()[0], index=df2
                                          .columns)
                c += 1
            projects = df2.query(
                'DOMAIN_ENTITY_STATE not in states').set_index('PRJ_CODE')
            not_ready_projects = df2.query(
                'DOMAIN_ENTITY_STATE in states').set_index('PRJ_CODE')
        except IOError:
            print "Filename does not exist"
            return None
    obs_proj_id = projects.OBS_PROJECT_ID
    timestamp = pd.Series(np.zeros(len(obs_proj_id), dtype=object),
                          index=obs_proj_id.index)

    for i1 in obs_proj_id.index:
        cursor.execute("SELECT TIMESTAMP, XMLTYPE.getClobVal(xml) "
                       "from ALMA.xml_obsproject_entities "
                       "where archive_uid = '%s'" % obs_proj_id.ix[i1])
        data = cursor.fetchall()[0]
        xml_content = data[1].read()
        timestamp.ix[i1] = data[0]
        filename = path + i1 + '.xml'
        io_file = open(filename, 'w')
        io_file.write(xml_content)
        io_file.close()

    projects['timestamp'] = timestamp
    cursor.close()
    connection.close()
    return projects, not_ready_projects, scheduling


def get_schedblocks(uid_list, path='./'):

    connection = cx_Oracle.connect(conx_string)
    cursor = connection.cursor()

    for uid in uid_list:
        sql = "SELECT TIMESTAMP, XMLTYPE.getClobVal(xml) " \
              "FROM ALMA.xml_schedblock_entities " \
              "WHERE archive_uid = '%s'" % uid
        cursor.execute(sql)
        data = cursor.fetchall()
        xml_content = data[0][1].read()
        filename = path + uid.replace(':', '_').replace('/', '_') + '.xml'
        io_file = open(filename, 'w')
        io_file.write(xml_content)
        io_file.close()

    cursor.close()
    connection.close()
    return None