__metaclass__ = type

import numpy as np
import pandas as pd
import csv
import cx_Oracle
from lxml import objectify

conx_strin = 'almasu/alma4dba@ALMA_ONLINE.OSF.CL'


class DataBase(object):

    def __init__(self, source=None, path='./'):
        self.path = path
        if source is None:
            self.projects, self.not_ready_prj, self.scheduling = query_archive()
        else:
            self.projects, self.not_ready_prj, self.scheduling = query_archive(
                source)
        self.projects['obsproj'] = pd.Series(
            np.zeros(len(self.projects), dtype=object),
            index=self.projects.index)
        for p in self.projects.index:
            obspro = ObsProject(path + p + '.xml')
            self.projects.loc[p, 'obsproj'] = obspro

    def update_db(self):
        prj_list = self.projects['proj_code'].tolist()
        pass


class ObsProject(object):

    def __init__(self, xml_file, path='./'):
        io_file = open(path + xml_file)
        tree = objectify.parse(io_file)
        io_file.close()
        data = tree.getroot()
        for key in data.__dict__:
            self.__setattr__(key, data.__dict__[key])

    def assoc_sched_blocks(self):
        sched_uid_12m = []
        sched_uid_7m = []
        sched_uid_tp = []
        for sg in self.ObsProgram.ObsPlan.ObsUnitSet:
            for ous in sg.ObsUnitSet:
                try:
                    for mous in ous.ObsUnitSet:
                        array_requested = mous.ObsUnitControl.attrib[
                            'arrayRequested']
                        try:
                            for sbs in mous.SchedBlockRef:
                                if array_requested == 'TWELVE-M':
                                    sched_uid_12m.append(sbs.attrib['entityId'])
                                elif array_requested == 'SEVEN-M':
                                    sched_uid_7m.append(sbs.attrib['entityId'])
                                elif array_requested == 'TP-Array':
                                    sched_uid_tp.append(sbs.attrib['entityId'])
                        except AttributeError:
                            # Member OUS does not have any SB created yet.
                            continue
                except AttributeError:
                    print ous.attrib
                    continue
        return sched_uid_7m, sched_uid_12m, sched_uid_tp

    def import_sched_blocks(self):
        pass


class SchedBlocK(object):

    def __init__(self, xml_file, path='./'):
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
    connection = cx_Oracle.connect(conx_strin)
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

    connection = cx_Oracle.connect(conx_strin)
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