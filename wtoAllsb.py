__author__ = 'itoledo'
__metaclass__ = type

import numpy as np
import pandas as pd
import csv
import cx_Oracle
import os
from lxml import objectify
from subprocess import call
import arrayResolution2p as ARes

conx_string = 'almasu/alma4dba@ALMA_ONLINE.OSF.CL'
conx_string_sco = 'almasu/alma4dba@ALMA_ONLINE.SCO.CL'
prj = '{Alma/ObsPrep/ObsProject}'
val = '{Alma/ValueTypes}'
sbl = '{Alma/ObsPrep/SchedBlock}'


pd.options.display.width = 200
pd.options.display.max_columns = 55


# noinspection PyPep8Naming
class WtoDatabase(object):

    """
    WtoDatabase is the class that stores the Projects and SB information in
    dataframes, and it also has the methods to connect and query the OSF
    archive for this info.

    A default instance will use the directory $HOME/.wto as a cache, and by
    default find the approved Cycle 2 projects and carried-over Cycle 1
    projects. If a file name or list are given as 'source' parameter, only the
    information of the projects in that list or filename will be ingested.

    Setting *forcenew* to True will force the cleaning of the cache dir, and
    all information will be processed again.

    :param path: Path for data cache.
    :type path: str, default '$HOME/.wto'
    :param source: File or list of strings with the codes of the projects
        to be ingested by WtoDatabase.
    :type source: list or str
    :param forcenew: Force cache cleaning and reload from archive.
    :type forcenew: boolean, default False
    """

    def __init__(self, path='/.wto_all/', forcenew=False):
        """


        """
        self.new = forcenew
        # Default Paths and Preferences
        if path[-1] != '/':
            path += '/'
        self.path = os.environ['HOME'] + path
        self.wto_path = os.environ['WTO']
        self.sbxml = self.path + 'sbxml/'
        self.obsxml = self.path + 'obsxml/'
        self.preferences = pd.Series(
            ['project.pandas', 'sciencegoals.pandas',
             'scheduling.pandas', 'special.list', 'pwvdata.pandas',
             'executive.pandas', 'sbxml_table.pandas', 'sbinfo.pandas',
             'newar.pandas', 'fieldsource.pandas', 'target.pandas',
             'spectralconf.pandas'],
            index=['project_table', 'sciencegoals_table',
                   'scheduling_table', 'special', 'pwv_data',
                   'executive_table', 'sbxml_table', 'sbinfo_table',
                   'newar_table', 'fieldsource_table', 'target_table',
                   'spectralconf_table'])
        self.status = ["Canceled", "Rejected"]

        # Global Oracle Connection
        self.connection = cx_Oracle.connect(conx_string)
        self.cursor = self.connection.cursor()

        # Global SQL search expressions
        # Search Project's PT information and match with PT Status
        self.sql1 = str(
            "SELECT PRJ_ARCHIVE_UID as OBSPROJECT_UID,PI,PRJ_NAME,"
            "CODE,PRJ_SCIENTIFIC_RANK,PRJ_VERSION,"
            "PRJ_LETTER_GRADE,DOMAIN_ENTITY_STATE as PRJ_STATUS,"
            "ARCHIVE_UID as OBSPROPOSAL_UID "
            "FROM ALMA.BMMV_OBSPROJECT obs1, ALMA.OBS_PROJECT_STATUS obs2,"
            " ALMA.BMMV_OBSPROPOSAL obs3 "
            "WHERE regexp_like (CODE, '^201[23].*\.[AST]') "
            "AND (PRJ_LETTER_GRADE='A' OR PRJ_LETTER_GRADE='B' "
            "OR PRJ_LETTER_GRADE='C') "
            "AND obs2.OBS_PROJECT_ID = obs1.PRJ_ARCHIVE_UID AND "
            "obs1.PRJ_ARCHIVE_UID = obs3.PROJECTUID")

        # Populate different dataframes related to projects and SBs statuses

        # self.scheduling_proj: data frame with projects at SCHEDULING_AOS
        # Query Projects currently on SCHEDULING_AOS
        self.sqlsched_proj = str(
            "SELECT CODE,OBSPROJECT_UID as OBSPROJECT_UID,"
            "VERSION as PRJ_SAOS_VERSION, STATUS as PRJ_SAOS_STATUS "
            "FROM SCHEDULING_AOS.OBSPROJECT "
            "WHERE regexp_like (CODE, '^201[23].*\.[AST]')")
        self.cursor.execute(self.sqlsched_proj)
        self.saos_obsproject = pd.DataFrame(
            self.cursor.fetchall(),
            columns=[rec[0] for rec in self.cursor.description]
        ).set_index('CODE', drop=False)

        # self.scheduling_sb: SBs at SCHEDULING_AOS
        # Query SBs in the SCHEDULING_AOS tables
        self.sqlsched_sb = str(
            "SELECT ou.OBSUNIT_UID as OUS_UID, sb.NAME as SB_NAME,"
            "sb.SCHEDBLOCK_CTRL_EXEC_COUNT,"
            "sb.SCHEDBLOCK_CTRL_STATE as SB_SAOS_STATUS,"
            "ou.OBSUNIT_PROJECT_UID as OBSPROJECT_UID "
            "FROM SCHEDULING_AOS.SCHEDBLOCK sb, SCHEDULING_AOS.OBSUNIT ou "
            "WHERE sb.SCHEDBLOCKID = ou.OBSUNITID AND sb.CSV = 0")
        self.cursor.execute(self.sqlsched_sb)
        self.saos_schedblock = pd.DataFrame(
            self.cursor.fetchall(),
            columns=[rec[0] for rec in self.cursor.description]
        ).set_index('OUS_UID', drop=False)

        # self.sbstates: SBs status (PT?)
        # Query SBs status
        self.sqlstates = str(
            "SELECT DOMAIN_ENTITY_STATE as SB_STATE,"
            "DOMAIN_ENTITY_ID as SB_UID,OBS_PROJECT_ID as OBSPROJECT_UID "
            "FROM ALMA.SCHED_BLOCK_STATUS")
        self.cursor.execute(self.sqlstates)
        self.sb_status = pd.DataFrame(
            self.cursor.fetchall(),
            columns=[rec[0] for rec in self.cursor.description]
        ).set_index('SB_UID', drop=False)

        # self.qa0: QAO flags for observed SBs
        # Query QA0 flaas from AQUA tables
        self.sqlqa0 = str(
            "SELECT SCHEDBLOCKUID as SB_UID,QA0STATUS "
            "FROM ALMA.AQUA_EXECBLOCK "
            "WHERE regexp_like (OBSPROJECTCODE, '^201[23].*\.[AST]')")

        self.cursor.execute(self.sqlqa0)
        self.aqua_execblock = pd.DataFrame(
            self.cursor.fetchall(),
            columns=[rec[0] for rec in self.cursor.description]
        ).set_index('SB_UID', drop=False)

        # Query for Executives
        sql2 = str(
            "SELECT PROJECTUID as OBSPROJECT_UID, ASSOCIATEDEXEC "
            "FROM ALMA.BMMV_OBSPROPOSAL "
            "WHERE regexp_like (CYCLE, '^201[23].[1A]')")
        self.cursor.execute(sql2)
        self.executive = pd.DataFrame(
            self.cursor.fetchall(), columns=['OBSPROJECT_UID', 'EXEC'])

        # Initialize with saved data and update, Default behavior.
        if not self.new:
            try:
                self.projects = pd.read_pickle(
                    self.path + 'projects.pandas')
                self.sg_schedblock = pd.read_pickle(
                    self.path + 'sg_schedblock.pandas')
                self.sciencegoals = pd.read_pickle(
                    self.path + 'sciencegoals.pandas')
                self.aqua_execblock = pd.read_pickle(
                    self.path + 'aqua_execblock.pandas')
                self.executive = pd.read_pickle(
                    self.path + 'executive.pandas')
                self.obsproject = pd.read_pickle(
                    self.path + 'obsproject.pandas')
                self.obsproposal = pd.read_pickle(
                    self.path + 'obsproposal.pandas')
                self.saos_obsproject = pd.read_pickle(
                    self.path + 'saos_obsproject.pands')
                self.saos_schedblock = pd.read_pickle(
                    self.path + 'saos_schedblock.pandas')
                self.targets_proj = pd.read_pickle(
                    self.path + 'targets_proj')
            except IOError, e:
                print e
                self.new = True

        # Create main dataframes
        if self.new:
            call(['rm', '-rf', self.path])
            print(self.path + ": creating preferences dir")
            os.mkdir(self.path)
            os.mkdir(self.sbxml)
            os.mkdir(self.obsxml)
            self.start_wto()

    def start_wto(self):

        """
        Initializes the wtoDatabase dataframes.

        The function queries the archive to look for cycle 1 and cycle 2
        projects, disregarding any projects with status "Approved",
        "Phase1Submitted", "Broken", "Canceled" or "Rejected".

        The archive tables used are ALMA.BMMV_OBSPROPOSAL,
        ALMA.OBS_PROJECT_STATUS, ALMA.BMMV_OBSPROJECT and
        ALMA.XML_OBSPROJECT_ENTITIES.

        :return: None
        """
        # noinspection PyUnusedLocal
        status = self.status

        # Query for Projects, from BMMV.
        self.cursor.execute(self.sql1)
        df1 = pd.DataFrame(
            self.cursor.fetchall(),
            columns=[rec[0] for rec in self.cursor.description])
        print(len(df1.query('PRJ_STATUS not in @status')))
        self.projects = pd.merge(
            df1.query('PRJ_STATUS not in @status'), self.executive,
            on='OBSPROJECT_UID'
        ).set_index('CODE', drop=False)

        timestamp = pd.Series(
            np.zeros(len(self.projects), dtype=object),
            index=self.projects.index)
        self.projects['timestamp'] = timestamp
        self.projects['xmlfile'] = pd.Series(
            np.zeros(len(self.projects), dtype=object),
            index=self.projects.index)
        self.filter_c1()
        # Download and read obsprojects and obsprosal
        number = self.projects.__len__()
        c = 1
        for r in self.projects.iterrows():
            xmlfilename, obsproj = self.get_projectxml(
                r[1].CODE, r[1].PRJ_STATUS, number, c)
            c += 1
            if obsproj:
                self.read_obsproject(xmlfilename)
            else:
                self.read_obsproposal(xmlfilename, r[1].CODE)
        self.projects.to_pickle(
            self.path + 'projects.pandas')
        self.sg_schedblock.to_pickle(
            self.path + 'sg_schedblock.pandas')
        self.sciencegoals.to_pickle(
            self.path + 'sciencegoals.pandas')
        self.aqua_execblock.to_pickle(
            self.path + 'aqua_execblock.pandas')
        self.executive.to_pickle(
            self.path + 'executive.pandas')
        self.obsproject.to_pickle(
            self.path + 'obsproject.pandas')
        self.obsproposal.to_pickle(
            self.path + 'obsproposal.pandas')
        self.saos_obsproject.to_pickle(
            self.path + 'saos_obsproject.pands')
        self.saos_schedblock.to_pickle(
            self.path + 'saos_schedblock.pandas')
        self.targets_proj.to_pickle(
            self.path + 'targets_proj')

    def get_projectxml(self, code, state, n, c):
        """

        :param code:
        """

        if state not in ['Approved', 'PhaseISubmitted']:
            print("Downloading Project %s obsproject.xml, status %s. (%s/%s)" %
                  (code, self.projects.ix[code, 'PRJ_STATUS'], c, n))
            self.cursor.execute(
                "SELECT TIMESTAMP, XMLTYPE.getClobVal(xml) "
                "FROM ALMA.XML_OBSPROJECT_ENTITIES "
                "WHERE ARCHIVE_UID = '%s'" % self.projects.ix[
                    code, 'OBSPROJECT_UID'])
            obsproj = True
        else:
            print("Downloading Project %s obsproposal.xml, status %s. (%s/%s)" %
                  (code, self.projects.ix[code, 'PRJ_STATUS'], c, n))
            self.cursor.execute(
                "SELECT TIMESTAMP, XMLTYPE.getClobVal(xml) "
                "FROM ALMA.XML_OBSPROPOSAL_ENTITIES "
                "WHERE ARCHIVE_UID = '%s'" % self.projects.ix[
                    code, 'OBSPROPOSAL_UID'])
            obsproj = False
        try:
            data = self.cursor.fetchall()[0]
        except IndexError:
            print "Project %s not found on archive?" % self.projects.ix[code]
            return 0
        xml_content = data[1].read()
        xmlfilename = code + '.xml'
        self.projects.loc[code, 'timestamp'] = data[0]
        filename = self.obsxml + xmlfilename
        io_file = open(filename, 'w')
        io_file.write(xml_content)
        io_file.close()
        self.projects.loc[code, 'xmlfile'] = xmlfilename
        return xmlfilename, obsproj

    def read_obsproject(self, xml):

        try:
            obsparse = ObsProject(xml, self.obsxml)
        except KeyError:
            print("Something went wrong while trying to parse %s" % xml)
            return 0

        code = obsparse.code.pyval
        prj_version = obsparse.version.pyval
        staff_note = obsparse.staffProjectNote.pyval
        is_calibration = obsparse.isCalibration.pyval
        obsproject_uid = obsparse.ObsProjectEntity.attrib['entityId']
        try:
            is_ddt = obsparse.isDDT.pyval
        except AttributeError:
            is_ddt = False

        try:
            self.obsprojects.ix[code] = (
                code, obsproject_uid, prj_version, staff_note, is_ddt,
                is_calibration
            )
        except AttributeError:
            self.obsprojects = pd.DataFrame(
                [(code, obsproject_uid, prj_version, staff_note, is_ddt,
                  is_calibration)],
                columns=['CODE', 'OBSPROJECT_UID', 'PRJ_VERSION', 'staffNote',
                         'isDDT', 'isCalibration'],
                index=[code]
            )

        obsprog = obsparse.ObsProgram
        sg_list = obsprog.findall(prj + 'ScienceGoal')
        c = 0
        for sg in sg_list:
            self.read_sciencegoals(sg, obsproject_uid, c + 1)
            c += 1

        oussg_list = obsprog.ObsPlan.findall(prj + 'ObsUnitSet')
        for oussg in oussg_list:
            groupous_list = oussg.findall(prj + 'ObsUnitSet')
            OUS_ID = oussg.attrib['entityPartId']
            oussg_name = oussg.name.pyval
            OBSPROJECT_UID = oussg.ObsProjectRef.attrib['entityId']
            for groupous in groupous_list:
                groupous_id = groupous.attrib['entityPartId']
                memous_list = groupous.findall(prj + 'ObsUnitSet')
                groupous_name = groupous.name.pyval
                for memous in memous_list:
                    memous_id = memous.attrib['entityPartId']
                    memous_name = memous.name.pyval
                    try:
                        SB_UID = memous.SchedBlockRef.attrib['entityId']
                    except AttributeError:
                        continue

                    oucontrol = memous.ObsUnitControl
                    execount = oucontrol.aggregatedExecutionCount.pyval
                    array = memous.ObsUnitControl.attrib['arrayRequested']
                    sql = "SELECT TIMESTAMP, XMLTYPE.getClobVal(xml) " \
                          "FROM ALMA.xml_schedblock_entities " \
                          "WHERE archive_uid = '%s'" % SB_UID
                    self.cursor.execute(sql)
                    data = self.cursor.fetchall()
                    xml_content = data[0][1].read()
                    filename = SB_UID.replace(':', '_').replace('/', '_') +\
                        '.xml'
                    io_file = open(self.sbxml + filename, 'w')
                    io_file.write(xml_content)
                    io_file.close()
                    xml = filename

                    if array == 'ACA':
                        array = 'SEVEN-M'
                    try:
                        self.sg_schedblock.ix[SB_UID] = (
                            OBSPROJECT_UID, OUS_ID, oussg_name, groupous_id,
                            groupous_name, memous_id, memous_name, SB_UID,
                            array, execount, xml)
                    except AttributeError:
                        self.sg_schedblock = pd.DataFrame(
                            [(OBSPROJECT_UID, OUS_ID, oussg_name, groupous_id,
                              groupous_name, memous_id, memous_name, SB_UID,
                              array, execount, xml)],
                            columns=['OBSPROJECT_UID', 'OUS_ID', 'oussg_name',
                                     'groupous_id', 'groupous_name',
                                     'memous_id', 'memous_name', 'SB_UID',
                                     'array', 'execount', 'xmlfile'],
                            index=[SB_UID]
                        )

    def read_obsproposal(self, xml, code):

        try:
            obsparse = ObsProposal(xml, self.obsxml)
        except KeyError:
            print("Something went wrong while trying to parse %s" % xml)
            return 0

        prj_version = None
        staff_note = None
        is_calibration = None
        obsproject_uid = obsparse.data.ObsProjectRef.attrib['entityId']
        is_ddt = None

        try:
            self.obsproposals.ix[code] = (
                code, obsproject_uid, prj_version, staff_note, is_ddt,
                is_calibration
            )
        except AttributeError:
            self.obsproposals = pd.DataFrame(
                [(code, obsproject_uid, prj_version, staff_note, is_ddt,
                  is_calibration)],
                columns=['CODE', 'OBSPROJECT_UID', 'PRJ_VERSION', 'staffNote',
                         'isDDT', 'isCalibration'],
                index=[code]
            )

        sg_list = obsparse.data.findall(prj + 'ScienceGoal')
        c = 0
        for sg in sg_list:
            self.read_sciencegoals(sg, obsproject_uid, c + 1)
            c += 1

    def read_sciencegoals(self, sg, obsproject_uid, idnum):

        sg_id = obsproject_uid + '_' + str(idnum)
        try:
            ous_id = sg.ObsUnitSetRef.attrib['partId']
            hasSB = True
        except AttributeError:
            ous_id = None
            hasSB = False
        sg_name = sg.name.pyval
        bands = sg.findall(prj + 'requiredReceiverBands')[0].pyval
        estimatedTime = convert_tsec(sg.estimatedTotalTime.pyval,
                                     sg.estimatedTotalTime.attrib['unit'])
        e12mTime = 0
        eACATime = 0
        eTPTime = 0

        performance = sg.PerformanceParameters
        AR = convert_sec(
            performance.desiredAngularResolution.pyval,
            performance.desiredAngularResolution.attrib['unit'])
        LAS = convert_sec(
            performance.desiredLargestScale.pyval,
            performance.desiredLargestScale.attrib['unit'])
        sensitivity = convert_jy(
            performance.desiredSensitivity.pyval,
            performance.desiredSensitivity.attrib['unit'])
        useACA = performance.useACA.pyval
        useTP = performance.useTP.pyval
        isPointSource = performance.isPointSource.pyval
        try:
            isTimeConstrained = performance.isTimeConstrained.pyval
        except AttributeError:
            isTimeConstrained = None
        spectral = sg.SpectralSetupParameters
        repFreq = convert_ghz(
            spectral.representativeFrequency.pyval,
            spectral.representativeFrequency.attrib['unit'])
        polarization = spectral.attrib['polarisation']
        type_pol = spectral.attrib['type']
        ARcor = AR * repFreq / 100.
        LAScor = LAS * repFreq / 100.

        two_12m = self.needs2(ARcor, LAScor)
        targets = sg.findall(prj + 'TargetParameters')
        num_targets = len(targets)
        c = 1
        for t in targets:
            self.read_pro_targets(t, sg_id, obsproject_uid, c)
            c += 1

        try:
            self.sciencegoals.ix[sg_id] = (
                obsproject_uid, ous_id, sg_name, bands, estimatedTime, e12mTime,
                eACATime, eTPTime, AR, LAS, ARcor, LAScor, sensitivity, useACA,
                useTP, isTimeConstrained, repFreq, isPointSource, polarization,
                type_pol, hasSB, two_12m, num_targets)
        except AttributeError:
            self.sciencegoals = pd.DataFrame(
                [(obsproject_uid, ous_id, sg_name, bands, estimatedTime,
                  e12mTime, eACATime, eTPTime, AR, LAS, ARcor, LAScor,
                  sensitivity, useACA, useTP, isTimeConstrained, repFreq,
                  isPointSource, polarization, type_pol, hasSB, two_12m,
                  num_targets)],
                columns=['OBSPROJECT_UID', 'OUS_UID', 'sg_name', 'band',
                         'estimatedTime', 'e12mTime', 'eACATime', 'eTPTime',
                         'AR', 'LAS', 'ARcor', 'LAScor', 'sensitivity',
                         'useACA', 'useTP', 'isTimeConstrained', 'repFreq',
                         'isPointSource', 'polarization', 'type', 'hasSB',
                         'two_12m', 'num_targets'],
                index=[sg_id]
            )

    def read_pro_targets(self, target, sgid, obsp_uid, c):

        tid = sgid + '_' + str(c)
        try:
            solarSystem = target.attrib['solarSystemObject']
        except KeyError:
            solarSystem = None

        typetar = target.attrib['type']
        sourceName = target.sourceName.pyval
        coord = target.sourceCoordinates
        ra = convert_deg(coord.findall(val + 'longitude')[0].pyval,
                         coord.findall(val + 'longitude')[0].attrib['unit'])
        dec = convert_deg(coord.findall(val + 'latitude')[0].pyval,
                          coord.findall(val + 'latitude')[0].attrib['unit'])
        try:
            isMosaic = target.isMosaic.pyval
        except AttributeError:
            isMosaic = None

        try:
            self.targets_proj.ix[tid] = (
                obsp_uid, sgid, typetar, solarSystem, sourceName, ra, dec,
                isMosaic)
        except AttributeError:
            print('creating')
            self.targets_proj = pd.DataFrame(
                [(obsp_uid, sgid, typetar, solarSystem, sourceName, ra, dec,
                 isMosaic)],
                columns=['OBSPROJECT_UID', 'SG_ID', 'tartype', 'solarSystem',
                         'sourceName', 'RA', 'DEC', 'isMosaic'],
                index=[tid]
            )

    def needs2(self, AR, LAS):

        if (0.57 > AR >= 0.41) and LAS >= 9.1:
            return True
        elif (0.75 > AR >= 0.57) and LAS >= 9.1:
            return True
        elif (1.11 > AR >= 0.75) and LAS >= 14.4:
            return True
        elif (1.40 > AR >= 1.11) and LAS >= 18.0:
            return True
        else:
            return False

    def filter_c1(self):
        """


        """
        c1c2 = pd.read_csv(
            self.wto_path + 'conf/c1c2.csv', sep=',', header=0,
            usecols=range(5))
        c1c2.columns = pd.Index([u'CODE', u'Region', u'ARC', u'C2', u'P2G'],
                                dtype='object')
        toc2 = c1c2[c1c2.fillna('no').C2.str.startswith('Yes')]
        check_c1 = pd.merge(
            self.projects[self.projects.CODE.str.startswith('2012')],
            toc2, on='CODE', how='right').set_index(
                'CODE', drop=False)[['CODE']]
        check_c2 = self.projects[
            self.projects.CODE.str.startswith('2013')][['CODE']]
        checked = pd.concat([check_c1, check_c2])
        temp = pd.merge(
            self.projects, checked, on='CODE',
            copy=False, how='inner').set_index('CODE', drop=False)
        self.projects = temp


class ObsProposal(object):
    """

    :param xml_file:
    :param path:
    """

    def __init__(self, xml_file, path='./'):
        """

        :param xml_file:
        :param path:
        """
        io_file = open(path + xml_file)
        tree = objectify.parse(io_file)
        io_file.close()
        self.data = tree.getroot()


class ObsProject(object):
    """

    :param xml_file:
    :param path:
    """

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


def convert_deg(angle, unit):
    """

    :param angle:
    :param unit:
    :return:
    """
    value = angle
    if unit == 'mas':
        value /= 3600000.
    elif unit == 'arcsec':
        value /= 3600.
    elif unit == 'arcmin':
        value /= 60.
    elif unit == 'rad':
        value = value * pd.np.pi / 180.
    elif unit == 'hours':
        value *= 15.
    return value


def convert_sec(angle, unit):
    """

    :param angle:
    :param unit:
    :return:
    """
    value = angle
    if unit == 'mas':
        value /= 1000.
    elif unit == 'arcsec':
        value /= 1.
    elif unit == 'arcmin':
        value *= 60.
    elif unit == 'rad':
        value = (value * pd.np.pi / 180.) * 3600.
    elif unit == 'hours':
        value *= 15. * 3600.
    elif unit == 'deg':
        value *= 3600.
    else:
        return None
    return value


def convert_jy(flux, unit):
    """

    :param flux:
    :param unit:
    :return:
    """
    value = flux
    if unit == 'Jy':
        value = value
    elif unit == 'mJy':
        value /= 1000.
    else:
        return None
    return value


def convert_mjy(flux, unit):
    """

    :param flux:
    :param unit:
    :return:
    """
    value = flux
    if unit == 'Jy':
        value *= 1e3
    elif unit == 'mJy':
        value = value
    else:
        return None
    return value


def convert_ghz(freq, unit):
    """

    :param freq:
    :param unit:
    :return:
    """
    value = freq
    if unit == 'GHz':
        value = value
    elif unit == 'MHz':
        value *= 1e-3
    elif unit == 'kHz':
        value *= 1e-6
    elif unit == 'Hz':
        value *= 1e-9
    else:
        return None
    return value


def convert_tsec(time, unit):

    """

    :param time:
    :param unit:
    :return:
    """
    value = time
    if unit == 's':
        return value
    elif unit == 'min':
        return value * 60.
    elif unit == 'h':
        return value * 3600.
    else:
        return None