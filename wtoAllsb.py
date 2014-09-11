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
            "SELECT ou.OBSUNIT_UID as OUS_ID, sb.NAME as SB_NAME,"
            "sb.SCHEDBLOCK_CTRL_EXEC_COUNT,"
            "sb.SCHEDBLOCK_CTRL_STATE as SB_SAOS_STATUS,"
            "ou.OBSUNIT_PROJECT_UID as OBSPROJECT_UID "
            "FROM SCHEDULING_AOS.SCHEDBLOCK sb, SCHEDULING_AOS.OBSUNIT ou "
            "WHERE sb.SCHEDBLOCKID = ou.OBSUNITID AND sb.CSV = 0")
        self.cursor.execute(self.sqlsched_sb)
        self.saos_schedblock = pd.DataFrame(
            self.cursor.fetchall(),
            columns=[rec[0] for rec in self.cursor.description]
        ).set_index('OUS_ID', drop=False)

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
                self.sg_sbs = pd.read_pickle(
                    self.path + 'sg_sbs.pandas')
                self.sciencegoals = pd.read_pickle(
                    self.path + 'sciencegoals.pandas')
                self.aqua_execblock = pd.read_pickle(
                    self.path + 'aqua_execblock.pandas')
                self.executive = pd.read_pickle(
                    self.path + 'executive.pandas')
                self.obsprojects = pd.read_pickle(
                    self.path + 'obsprojects.pandas')
                self.obsproposals = pd.read_pickle(
                    self.path + 'obsproposals.pandas')
                self.saos_obsproject = pd.read_pickle(
                    self.path + 'saos_obsproject.pands')
                self.saos_schedblock = pd.read_pickle(
                    self.path + 'saos_schedblock.pandas')
                self.targets_sg = pd.read_pickle(
                    self.path + 'targets_sg')
            except IOError:
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
        self.sg_sbs.to_pickle(
            self.path + 'sg_sbs.pandas')
        self.sciencegoals.to_pickle(
            self.path + 'sciencegoals.pandas')
        self.aqua_execblock.to_pickle(
            self.path + 'aqua_execblock.pandas')
        self.executive.to_pickle(
            self.path + 'executive.pandas')
        self.obsprojects.to_pickle(
            self.path + 'obsprojects.pandas')
        self.obsproposals.to_pickle(
            self.path + 'obsproposals.pandas')
        self.saos_obsproject.to_pickle(
            self.path + 'saos_obsproject.pands')
        self.saos_schedblock.to_pickle(
            self.path + 'saos_schedblock.pandas')
        self.targets_sg.to_pickle(
            self.path + 'targets_sg')

    def process_wto(self):
        for sg_sb in self.sg_sbs.iterrows():
            self.row_schedblocks(sg_sb[1].SB_UID, sg_sb[1].OBSPROJECT_UID,
                                 sg_sb[1].OUS_ID, new=True)

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
            self.read_sciencegoals(sg, obsproject_uid, c + 1, True, obsprog)
            c += 1

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
            self.read_sciencegoals(sg, obsproject_uid, c + 1, False, None)
            c += 1

    def read_sciencegoals(self, sg, obsproject_uid, idnum, isObsproj, obsprog):

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

        two_12m = needs2(ARcor, LAScor)
        targets = sg.findall(prj + 'TargetParameters')
        num_targets = len(targets)
        c = 1
        for t in targets:
            self.read_pro_targets(t, sg_id, obsproject_uid, c)
            c += 1

        extendedTime, compactTime, sevenTime, TPTime = distributeTime(
            estimatedTime, two_12m, useACA, useTP
        )

        try:
            self.sciencegoals.ix[sg_id] = (
                sg_id, obsproject_uid, ous_id, sg_name, bands, estimatedTime,
                extendedTime, compactTime, sevenTime, TPTime, AR, LAS, ARcor,
                LAScor, sensitivity, useACA, useTP, isTimeConstrained, repFreq,
                isPointSource, polarization, type_pol, hasSB, two_12m,
                num_targets, isObsproj)
        except AttributeError:
            self.sciencegoals = pd.DataFrame(
                [(sg_id, obsproject_uid, ous_id, sg_name, bands, estimatedTime,
                  extendedTime, compactTime, sevenTime, TPTime, AR, LAS, ARcor,
                  LAScor, sensitivity, useACA, useTP, isTimeConstrained,
                  repFreq, isPointSource, polarization, type_pol, hasSB,
                  two_12m, num_targets, isObsproj)],
                columns=['SG_ID', 'OBSPROJECT_UID', 'OUS_ID', 'sg_name', 'band',
                         'estimatedTime', 'eExt12Time', 'eComp12Time',
                         'eACATime', 'eTPTime',
                         'AR', 'LAS', 'ARcor', 'LAScor', 'sensitivity',
                         'useACA', 'useTP', 'isTimeConstrained', 'repFreq',
                         'isPointSource', 'polarization', 'type', 'hasSB',
                         'two_12m', 'num_targets', 'isPhaseII'],
                index=[sg_id]
            )

        if isObsproj:
            oussg_list = obsprog.ObsPlan.findall(prj + 'ObsUnitSet')
            for oussg in oussg_list:
                groupous_list = oussg.findall(prj + 'ObsUnitSet')
                OUS_ID = oussg.attrib['entityPartId']
                if OUS_ID != ous_id:
                    continue
                ous_name = oussg.name.pyval
                OBSPROJECT_UID = oussg.ObsProjectRef.attrib['entityId']
                for groupous in groupous_list:
                    gous_id = groupous.attrib['entityPartId']
                    mous_list = groupous.findall(prj + 'ObsUnitSet')
                    gous_name = groupous.name.pyval
                    for mous in mous_list:
                        mous_id = mous.attrib['entityPartId']
                        mous_name = mous.name.pyval
                        try:
                            SB_UID = mous.SchedBlockRef.attrib['entityId']
                        except AttributeError:
                            continue
                        oucontrol = mous.ObsUnitControl
                        execount = oucontrol.aggregatedExecutionCount.pyval
                        array = mous.ObsUnitControl.attrib['arrayRequested']
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
                            self.sg_sbs.ix[SB_UID] = (
                                SB_UID, OBSPROJECT_UID, sg_id,
                                ous_id, ous_name, gous_id,
                                gous_name, mous_id, mous_name,
                                array, execount, xml)
                        except AttributeError:
                            self.sg_sbs = pd.DataFrame(
                                [(SB_UID, OBSPROJECT_UID, sg_id,
                                  ous_id, ous_name, gous_id,
                                  gous_name, mous_id, mous_name,
                                  array, execount, xml)],
                                columns=[
                                    'SB_UID', 'OBSPROJECT_UID', 'SG_ID',
                                    'OUS_ID', 'ous_name', 'GOUS_ID',
                                    'gous_name', 'MOUS_ID', 'mous_name',
                                    'array', 'execount', 'xmlfile'],
                                index=[SB_UID]
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
            self.targets_sg.ix[tid] = (
                tid, obsp_uid, sgid, typetar, solarSystem, sourceName, ra, dec,
                isMosaic)
        except AttributeError:
            self.targets_sg = pd.DataFrame(
                [(tid, obsp_uid, sgid, typetar, solarSystem, sourceName, ra,
                  dec, isMosaic)],
                columns=['TARG_ID', 'OBSPROJECT_UID', 'SG_ID', 'tarType',
                         'solarSystem', 'sourceName', 'RA', 'DEC', 'isMosaic'],
                index=[tid]
            )

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

    def row_schedblocks(self, sb_uid, obs_uid, ous_id, new=False):

        # Open SB with SB parser class
        """

        :param sb_uid:
        :param new:
        """
        sb = self.sg_sbs.ix[sb_uid]
        sg_id = sb.sg_id
        xml = SchedBlocK(sb.xmlfile, self.sbxml)
        new_orig = new
        # Extract root level data
        array = xml.data.findall(
            './/' + prj + 'ObsUnitControl')[0].attrib['arrayRequested']
        name = xml.data.findall('.//' + prj + 'name')[0].pyval
        status = xml.data.attrib['status']

        schedconstr = xml.data.SchedulingConstraints
        schedcontrol = xml.data.SchedBlockControl
        preconditions = xml.data.Preconditions
        weather = preconditions.findall('.//' + prj + 'WeatherConstraints')[0]

        try:
            polarparam = xml.data.PolarizationCalParameters
            ispolarization = True
        except AttributeError:
            ispolarization = False

        repfreq = schedconstr.representativeFrequency.pyval
        ra = schedconstr.representativeCoordinates.findall(
            val + 'longitude')[0].pyval
        dec = schedconstr.representativeCoordinates.findall(
            val + 'latitude')[0].pyval
        minar_old = schedconstr.minAcceptableAngResolution.pyval
        maxar_old = schedconstr.maxAcceptableAngResolution.pyval
        band = schedconstr.attrib['representativeReceiverBand']

        execount = schedcontrol.executionCount.pyval
        maxpwv = weather.maxPWVC.pyval

        n_fs = len(xml.data.FieldSource)
        n_tg = len(xml.data.Target)
        n_ss = len(xml.data.SpectralSpec)

        for n in range(n_fs):
            if new:
                self.row_fieldsource(xml.data.FieldSource[n], sb_uid, array,
                                     new=new)
                new = False
            else:
                self.row_fieldsource(xml.data.FieldSource[n], sb_uid, array)

        new = new_orig
        for n in range(n_tg):
            if new:
                self.row_target(xml.data.Target[n], sb_uid, new=new)
                new = False
            else:
                self.row_target(xml.data.Target[n], sb_uid)

        new = new_orig
        for n in range(n_ss):
            if new:
                self.row_spectralconf(xml.data.SpectralSpec[n], sb_uid, new=new)
                new = False
            else:
                self.row_spectralconf(xml.data.SpectralSpec[n], sb_uid)

        try:
            self.schedblocks.ix[sb_uid] = (
                sb_uid, obs_uid, sg_id, ous_id,
                name, status, repfreq, band, array,
                ra, dec, minar_old, maxar_old, execount,
                ispolarization, maxpwv)
        except AttributeError:
            self.schedblocks = pd.DataFrame(
                [(sb_uid, obs_uid, sg_id, ous_id,
                  name, status, repfreq, band, array,
                  ra, dec, minar_old, maxar_old, execount,
                  ispolarization, maxpwv)],
                columns=['SB_UID', 'OBSPROJECT_UID', 'SG_ID', 'OUS_ID',
                         'sbName', 'sbStatusXml', 'repfreq', 'band', 'array',
                         'RA', 'DEC', 'minAR_ot', 'maxAR_ot', 'execount',
                         'isPolarization', 'maxPWVC'],
                index=[sb_uid])

    def row_fieldsource(self, fs, sbuid, array, new=False):
        """

        :param fs:
        :param sbuid:
        :param new:
        """
        partid = fs.attrib['entityPartId']
        coord = fs.sourceCoordinates
        solarsystem = fs.attrib['solarSystemObject']
        sourcename = fs.sourceName.pyval
        name = fs.name.pyval
        isquery = fs.isQuery.pyval
        pointings = len(fs.findall(sbl + 'PointingPattern/' + sbl +
                                   'phaseCenterCoordinates'))
        try:
            ismosaic = fs.PointingPattern.isMosaic.pyval
        except AttributeError:
            ismosaic = False
        if isquery:
            querysource = fs.QuerySource
            qc_intendeduse = querysource.attrib['intendedUse']
            qcenter = querysource.queryCenter
            qc_ra = qcenter.findall(val + 'longitude')[0].pyval
            qc_dec = qcenter.findall(val + 'latitude')[0].pyval
            qc_use = querysource.use.pyval
            qc_radius = querysource.searchRadius.pyval
            qc_radius_unit = querysource.searchRadius.attrib['unit']
        else:
            qc_intendeduse, qc_ra, qc_dec, qc_use, qc_radius, qc_radius_unit = (
                None, None, None, None, None, None
            )
        ra = coord.findall(val + 'longitude')[0].pyval
        dec = coord.findall(val + 'latitude')[0].pyval
        if solarsystem == 'Ephemeris':
            ephemeris = fs.sourceEphemeris.pyval
        else:
            ephemeris = None
        if new:
            self.fieldsource = pd.DataFrame(
                [(partid, sbuid, solarsystem, sourcename, name, ra, dec,
                  isquery, qc_intendeduse, qc_ra, qc_dec, qc_use, qc_radius,
                  qc_radius_unit, ephemeris, pointings, ismosaic, array)],
                columns=['fieldRef', 'SB_UID', 'solarSystem', 'sourcename',
                         'name', 'RA', 'DEC', 'isQuery', 'intendedUse', 'qRA',
                         'qDEC', 'use', 'search_radius', 'rad_unit',
                         'ephemeris', 'pointings', 'isMosaic', 'arraySB'],
                index=[partid]
            )
        self.fieldsource.ix[partid] = (
            partid, sbuid, solarsystem, sourcename, name, ra, dec, isquery,
            qc_intendeduse, qc_ra, qc_dec, qc_use, qc_radius, qc_radius_unit,
            ephemeris, pointings, ismosaic, array)

    def row_target(self, tg, sbuid, new=False):
        """

        :param tg:
        :param sbuid:
        :param new:
        """
        partid = tg.attrib['entityPartId']
        specref = tg.AbstractInstrumentSpecRef.attrib['partId']
        fieldref = tg.FieldSourceRef.attrib['partId']
        paramref = tg.ObservingParametersRef.attrib['partId']
        if new:
            self.target = pd.DataFrame(
                [(partid, sbuid, specref, fieldref, paramref)],
                columns=['targetId', 'SB_UID', 'specRef', 'fieldRef',
                         'paramRef'],
                index=[partid])
        else:
            self.target.ix[partid] = (partid, sbuid, specref, fieldref,
                                      paramref)

    def row_spectralconf(self, ss, sbuid, new=False):
        """

        :param ss:
        :param sbuid:
        :param new:
        """
        partid = ss.attrib['entityPartId']
        try:
            corrconf = ss.BLCorrelatorConfiguration
            nbb = len(corrconf.BLBaseBandConfig)
            nspw = 0
            for n in range(nbb):
                bbconf = corrconf.BLBaseBandConfig[n]
                nspw += len(bbconf.BLSpectralWindow)
        except AttributeError:
            corrconf = ss.ACACorrelatorConfiguration
            nbb = len(corrconf.ACABaseBandConfig)
            nspw = 0
            for n in range(nbb):
                bbconf = corrconf.ACABaseBandConfig[n]
                nspw += len(bbconf.ACASpectralWindow)
        if new:
            self.spectralconf = pd.DataFrame(
                [(partid, sbuid, nbb, nspw)],
                columns=['specRef', 'SB_UID', 'BaseBands', 'SPWs'],
                index=[partid])
        else:
            self.spectralconf.ix[partid] = (partid, sbuid, nbb, nspw)


def distributeTime(tiempo, doce, siete, single):

    if single and doce:
        timeU = tiempo / (1 + 0.5 + 2 + 4)
        return timeU, 0.5 * timeU, 2 * timeU, 4 * timeU
    elif single and not doce:
        timeU = tiempo / (1 + 2 + 4.)
        return timeU, 0., 2 * timeU, 4 * timeU
    elif siete and doce:
        timeU = tiempo / (1 + 0.5 + 2.)
        return timeU, 0.5 * timeU, 2 * timeU, 0.
    elif siete and not doce:
        timeU = tiempo / (1 + 2.)
        return timeU, 0., 2 * timeU, 0.
    elif doce:
        timeU = tiempo / 1.5
        return timeU, 0.5 * timeU, 0., 0.
    elif not doce:
        return tiempo, 0., 0., 0.
    else:
        print("couldn't distribute time...")
        return None


def needs2(AR, LAS):

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