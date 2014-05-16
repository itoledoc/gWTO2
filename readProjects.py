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
            self.projects, self.not_ready_prj = get_projects()
        else:
            self.projects, self.not_ready_prj = get_projects(source)
        self.projects['obsproj'] = pd.Series(np.zeros(len(self.projects), dtype=object),
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
            # science_goal_uid = sg.attrib['entityPartId']
            for ous in sg.ObsUnitSet:
                for mous in ous.ObsUnitSet:
                    array_requested = mous.ObsUnitControl.attrib['arrayRequested']
                    try:
                        for sbs in mous.SchedBlockRef:
                            if array_requested == 'TWELVE-M':
                                sched_uid_12m.append(sbs.attrib['entityId'])
                            elif array_requested == 'SEVEN-M':
                                sched_uid_7m.append(sbs.attrib['entityId'])
                            elif array_requested == 'TP-Array':
                                sched_uid_tp.append(sbs.attrib['entityId'])
                    except AttributeError, e:
                        # Member OUS does not have any SB created yet.
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


def get_projects(source=None, path='./'):

    """

    :param source:
    :param path:
    :return:
    """

    connection = cx_Oracle.connect(conx_strin)
    cursor = connection.cursor()
    sql1 = "SELECT obs1.PRJ_CODE, obs1.PRJ_ARCHIVE_UID, obs1.PRJ_SCIENTIFIC_RANK, " \
           "obs1.PRJ_LETTER_GRADE, obs2.DOMAIN_ENTITY_STATE, obs1.PRJ_VERSION, obs1.PRJ_TIME_OF_CREATION " \
           "FROM ALMA.BMMV_OBSPROJECT obs1, ALMA.OBS_PROJECT_STATUS obs2  " \
           "WHERE (PRJ_CODE LIKE '2013%A' OR PRJ_CODE LIKE '2013%S' OR PRJ_CODE LIKE '2013%T') " \
           "AND (PRJ_LETTER_GRADE='A' OR PRJ_LETTER_GRADE='B' OR PRJ_LETTER_GRADE='C') " \
           "AND OBS2.OBS_PROJECT_ID = OBS1.PRJ_ARCHIVE_UID"
    ltype = [('prj_code', 'a30'), ('prj_uid', 'a30'), ('rank', 'i4'), ('grade', 'a4'), ('status', 'a20'),
             ('version', 'a6'), ('timestamp', 'datetime64[us]')]

    if source is None:
        cursor.execute(sql1)
        temp_projects = np.array(cursor.fetchall(), dtype=ltype)
    else:
        if type(source) is not str and type(source) is not list:
            print "The filename shoud be a string or a list"
            return None
        try:
            if type(source) is str:
                fp = open(source, 'r')
                read_csv = csv.reader(fp)
            else:
                read_csv = source
            projects_tuple = []
            for l in read_csv:
                if type(source) is str:
                    l = l[0]
                sql2 = sql1 + ' AND OBS1.PRJ_CODE = ' + '\'%s\'' % l
                cursor.execute(sql2)
                projects_tuple.append(cursor.fetchall()[0])
            temp_projects = np.array(projects_tuple, dtype=ltype)
        except IOError:
            print "Filename does not exist"
            return None

    projects = np.zeros(0, dtype=ltype)
    not_ready_prj = np.zeros(0, dtype=ltype)
    for p in temp_projects:
        if p['status'] in ['Approved', 'Phase1Submitted', 'Broken', 'Completed', 'Canceled']:
            # print "Project %s is in %s state. ObsProject.xml not downloaded" % (p['prj_code'], p['status'])
            not_ready_prj = np.concatenate((not_ready_prj, np.array([p], dtype=ltype)))
            continue

        cursor.execute("SELECT TIMESTAMP, XMLTYPE.getClobVal(xml) "
                       "from ALMA.xml_obsproject_entities "
                       "where archive_uid = '%s'" % p['prj_uid'])
        data = cursor.fetchall()[0]
        xml_content = data[1].read()
        p['timestamp'] = data[0]
        projects = np.concatenate((projects, np.array([p], dtype=ltype)))
        filename = path + p['prj_code'] + '.xml'
        io_file = open(filename, 'w')
        io_file.write(xml_content)
        io_file.close()

    cursor.close()
    connection.close()
    return pd.DataFrame.from_records(projects, index='prj_code'), pd.DataFrame.from_records(not_ready_prj,
                                                                                            index='prj_code')


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