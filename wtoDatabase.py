"""
wtoDatabase.py: the gWTO database library.
==========================================
This library contains the classes and functions required to query, parse and
organize the Projects and SchedBlock information stored at the OSF archive in
different tables.
"""

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

    def __init__(self, path='/.wto/', source=None, forcenew=False):
        """


        """
        self.source = source
        self.new = forcenew
        # Default Paths and Preferences
        if path[-1] != '/':
            path += '/'
        self.path = os.environ['HOME'] + path
        self.wto_path = os.environ['WTO']
        self.sbxml = self.path + 'sbxml/'
        self.obsxml = self.path + 'obsxml/'
        self.preferences = pd.Series(
            ['obsproject.pandas', source, 'sciencegoals.pandas',
             'scheduling.pandas', 'special.list', 'pwvdata.pandas',
             'executive.pandas', 'sbxml_table.pandas', 'sbinfo.pandas',
             'newar.pandas', 'fieldsource.pandas', 'target.pandas',
             'spectralconf.pandas'],
            index=['obsproject_table', 'source', 'sciencegoals_table',
                   'scheduling_table', 'special', 'pwv_data',
                   'executive_table', 'sbxml_table', 'sbinfo_table',
                   'newar_table', 'fieldsource_table', 'target_table',
                   'spectralconf_table'])
        self.states = ["Approved", "Phase1Submitted", "Broken",
                       "Canceled", "Rejected"]

        # Global SQL search expressions
        self.sql1 = str(
            "SELECT PRJ_ARCHIVE_UID,DELETED,PI,PRJ_NAME,"
            "CODE,PRJ_TIME_OF_CREATION,PRJ_SCIENTIFIC_RANK,PRJ_VERSION,"
            "PRJ_LETTER_GRADE,DOMAIN_ENTITY_STATE,"
            "OBS_PROJECT_ID "
            "FROM ALMA.BMMV_OBSPROJECT obs1, ALMA.OBS_PROJECT_STATUS obs2 "
            "WHERE regexp_like (CODE, '^201[23].*\.[AST]') "
            "AND (PRJ_LETTER_GRADE='A' OR PRJ_LETTER_GRADE='B' "
            "OR PRJ_LETTER_GRADE='C') "
            "AND obs2.OBS_PROJECT_ID = obs1.PRJ_ARCHIVE_UID")
        self.sqlsched_proj = str(
            "SELECT * FROM SCHEDULING_AOS.OBSPROJECT "
            "WHERE regexp_like (CODE, '^201[23].*\.[AST]')")
        self.sqlstates = str(
            "SELECT DOMAIN_ENTITY_STATE,DOMAIN_ENTITY_ID,OBS_PROJECT_ID "
            "FROM ALMA.SCHED_BLOCK_STATUS")
        self.sqlqa0 = str(
            "SELECT SCHEDBLOCKUID,QA0STATUS FROM ALMA.AQUA_EXECBLOCK "
            "WHERE regexp_like (OBSPROJECTCODE, '^201[23].*\.[AST]')")
        self.sqlsched_sb = str(
            "SELECT ou.OBSUNIT_UID,sb.NAME,sb.REPR_BAND,"
            "sb.SCHEDBLOCK_CTRL_EXEC_COUNT,sb.SCHEDBLOCK_CTRL_STATE,"
            "sb.MIN_ANG_RESOLUTION,sb.MAX_ANG_RESOLUTION,"
            "ou.OBSUNIT_PROJECT_UID "
            "FROM SCHEDULING_AOS.SCHEDBLOCK sb, SCHEDULING_AOS.OBSUNIT ou "
            "WHERE sb.SCHEDBLOCKID = ou.OBSUNITID AND sb.CSV = 0")

        # Global Oracle Connection
        self.connection = cx_Oracle.connect(conx_string)
        self.cursor = self.connection.cursor()

        # Populate different dataframes related to projects and SBs statuses
        self.cursor.execute(self.sqlsched_proj)
        self.scheduling_proj = pd.DataFrame(
            self.cursor.fetchall(),
            columns=[rec[0] for rec in self.cursor.description]
        ).set_index('CODE', drop=False)

        self.cursor.execute(self.sqlstates)
        self.sbstates = pd.DataFrame(
            self.cursor.fetchall(),
            columns=[rec[0] for rec in self.cursor.description]
        ).set_index('DOMAIN_ENTITY_ID')

        self.cursor.execute(self.sqlqa0)
        self.qa0 = pd.DataFrame(
            self.cursor.fetchall(),
            columns=[rec[0] for rec in self.cursor.description]
        ).set_index('SCHEDBLOCKUID', drop=False)

        self.cursor.execute(self.sqlsched_sb)
        self.scheduling_sb = pd.DataFrame(
            self.cursor.fetchall(),
            columns=[rec[0] for rec in self.cursor.description]
        ).set_index('OBSUNIT_UID', drop=False)

        # Initialize with saved data and update, Default behavior.
        if not self.new:
            try:
                self.obsproject = pd.read_pickle(
                    self.path + self.preferences.obsproject_table)
                self.sciencegoals = pd.read_pickle(
                    self.path + self.preferences.sciencegoals_table)
                self.schedblocks = pd.read_pickle(
                    self.path + self.preferences.sbxml_table)
                self.schedblock_info = pd.read_pickle(
                    self.path + self.preferences.sbinfo_table)
                self.newar = pd.read_pickle(
                    self.path + self.preferences.newar_table)
                self.fieldsource = pd.read_pickle(
                    self.path + self.preferences.fieldsource_table)
                self.target = pd.read_pickle(
                    self.path + self.preferences.target_table)
                self.spectralconf = pd.read_pickle(
                    self.path + self.preferences.spectralconf_table)
                self.filter_c1()
                self.update()
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
            self.populate_sciencegoals_sbxml()
            self.populate_schedblocks()
            self.populate_schedblock_info()
            self.populate_newar()
            self.create_summary()

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
            print(len(df1.query('DOMAIN_ENTITY_STATE not in @states')))
            self.obsproject = pd.merge(
                df1.query('DOMAIN_ENTITY_STATE not in @states'), self.executive,
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
                    df2.query('DOMAIN_ENTITY_STATE not in @states'),
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
        self.filter_c1()
        print len(self.obsproject)
        self.obsproject.to_pickle(
            self.path + self.preferences.obsproject_table)

    def update(self, connect=True):

        """

        :param connect:
        :return:
        """
        self.cursor.execute(self.sqlsched_proj)
        self.scheduling_proj = pd.DataFrame(
            self.cursor.fetchall(),
            columns=[rec[0] for rec in self.cursor.description]
        ).set_index('CODE', drop=False)
        self.cursor.execute(self.sqlsched_sb)
        self.scheduling_sb = pd.DataFrame(
            self.cursor.fetchall(),
            columns=[rec[0] for rec in self.cursor.description]
        ).set_index('OBSUNIT_UID', drop=False)
        self.cursor.execute(self.sqlstates)
        self.sbstates = pd.DataFrame(
            self.cursor.fetchall(),
            columns=[rec[0] for rec in self.cursor.description]
        ).set_index('DOMAIN_ENTITY_ID')
        self.cursor.execute(self.sqlqa0)
        self.qa0 = pd.DataFrame(
            self.cursor.fetchall(),
            columns=[rec[0] for rec in self.cursor.description]
        ).set_index('SCHEDBLOCKUID', drop=False)

        if not connect:
            self.create_summary()
            return None

        newest = self.obsproject.timestamp.max()
        changes = []
        sql = str(
            "SELECT ARCHIVE_UID, TIMESTAMP FROM ALMA.XML_OBSPROJECT_ENTITIES "
            "WHERE TIMESTAMP > to_date('%s', 'YYYY-MM-DD HH24:MI:SS')" %
            str(newest).split('.')[0])
        self.cursor.execute(sql)
        new_data = self.cursor.fetchall()

        if len(new_data) > 0:
            for n in new_data:
                print "Changes? %s, %s, newest %s" % (n[0], n[1], newest)
                if n[1] <= newest:
                    print "\t Not Changes to apply (1)"
                    continue
                puid = n[0]
                try:
                    code = self.obsproject[
                        self.obsproject.PRJ_ARCHIVE_UID == puid].ix[0, 'CODE']
                    if code in self.checked.CODE.tolist():
                        changes.append(code)
                    else:
                        print "\t Not Changes to apply (2)"
                        continue
                except IndexError:
                    try:
                        self.cursor.execute(
                            self.sql1 + " AND OBS1.PRJ_ARCHIVE_UID = '%s'" %
                            puid)
                        row = list(self.cursor.fetchall()[0])
                    except IndexError:
                        print("\t %s must be a CSV project. Not ingesting" %
                              puid)
                        continue
                    code = row[4]
                    if (code not in self.checked.CODE.tolist() and
                            code.startswith('2012')):
                        print("\t %s didn't pass filter C1" % code)
                        continue
                    self.cursor.execute(
                        "SELECT ASSOCIATEDEXEC FROM ALMA.BMMV_OBSPROPOSAL "
                        "WHERE PROJECTUID = '%s'" % puid)
                    row.append(self.cursor.fetchall()[0][0])
                    row.append(n[1])
                    row.append(self.obsproject.ix[0, 'obsproj'])
                    self.obsproject.ix[code] = row
                    changes.append(code)

            for code in changes:
                print "Updating Project %s" % code
                self.get_obsproject(code)
                self.row_sciencegoals(code)
                pidlist = self.sciencegoals[
                    self.sciencegoals.CODE == code].partId.tolist()
                for pid in pidlist:
                    sblist = self.sciencegoals.ix[pid].SBS
                    for sb in sblist:
                        print "\tUpdating sb %s of project %s" % (sb, code)
                        self.row_schedblocks(sb, pid)
                        self.row_schedblock_info(sb)
                        self.row_newar(sb)
            self.filter_c1()
            self.schedblocks.to_pickle(
                self.path + self.preferences.sbxml_table)
            self.sciencegoals.to_pickle(
                self.path + self.preferences.sciencegoals_table)
            self.schedblock_info.to_pickle(
                self.path + self.preferences.sbinfo_table)
            self.newar.to_pickle(
                self.path + self.preferences.newar_table)
            self.fieldsource.to_pickle(
                self.path + self.preferences.fieldsource_table)
            self.target.to_pickle(
                self.path + self.preferences.target_table)
            self.spectralconf.to_pickle(
                self.path + self.preferences.spectralconf_table)
        newest = self.schedblocks.timestamp.max()
        sql = str(
            "SELECT ARCHIVE_UID, TIMESTAMP FROM ALMA.XML_SCHEDBLOCK_ENTITIES "
            "WHERE TIMESTAMP > to_date('%s', 'YYYY-MM-DD HH24:MI:SS')" %
            str(newest).split('.')[0])
        self.cursor.execute(sql)
        new_data = self.cursor.fetchall()

        if len(new_data) > 0:
            for n in new_data:
                if n[1] <= newest:
                    continue
                sbuid = n[0]
                try:
                    pid = self.schedblocks[
                        self.schedblocks.SB_UID == sbuid].ix[0, 'partId']
                except IndexError:
                    continue
                print "Updating SB %s" % sbuid
                self.row_schedblocks(sbuid, pid)
                self.row_schedblock_info(sbuid)
                self.row_newar(sbuid)
            self.schedblocks.to_pickle(
                self.path + self.preferences.sbxml_table)
            self.schedblock_info.to_pickle(
                self.path + self.preferences.sbinfo_table)
            self.newar.to_pickle(
                self.path + self.preferences.newar_table)
            self.fieldsource.to_pickle(
                self.path + self.preferences.fieldsource_table)
            self.target.to_pickle(
                self.path + self.preferences.target_table)
            self.spectralconf.to_pickle(
                self.path + self.preferences.spectralconf_table)
        self.cursor.execute("SELECT OBS_PROJECT_ID, DOMAIN_ENTITY_STATE "
                            "FROM ALMA.OBS_PROJECT_STATUS")
        newprstate = pd.DataFrame(
            self.cursor.fetchall(),
            columns=[rec[0] for rec in self.cursor.description]
        ).set_index('OBS_PROJECT_ID', drop=False)
        ori = self.obsproject[['DOMAIN_ENTITY_STATE']]
        self.obsproject.loc[:, 'DOMAIN_ENTITY_STATE'] = self.obsproject.apply(
            lambda r: newprstate.loc[r['PRJ_ARCHIVE_UID'],
                                     'DOMAIN_ENTITY_STATE'],
            axis=1)
        self.obsproject.to_pickle(
            self.path + self.preferences.obsproject_table)
        new = self.obsproject[['DOMAIN_ENTITY_STATE']]
        i = ori != new
        if len(new[i.values]) > 0:
            print("Detected PRJ state changes: ")
            print(new[i.values])
        else:
            print("No PRJ states changes.")
        self.create_summary()

    def populate_sciencegoals_sbxml(self):
        """


        """
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

    def populate_schedblock_info(self):
        """


        """
        new = True
        sb_uid_list = self.schedblocks.SB_UID.tolist()
        numsb = len(sb_uid_list)
        cou = 1
        for s in sb_uid_list:
            self.row_schedblock_info(s, new=new)
            print("SB %s processed (%d/%d)" % (s, cou, numsb))
            new = False
            cou += 1
        self.schedblock_info.to_pickle(
            self.path + self.preferences.sbinfo_table)
        self.fieldsource.to_pickle(
            self.path + self.preferences.fieldsource_table)
        self.target.to_pickle(
            self.path + self.preferences.target_table)
        self.spectralconf.to_pickle(
            self.path + self.preferences.spectralconf_table)

    def populate_schedblocks(self):
        """


        """
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

    def populate_newar(self):
        """


        """
        new = True
        sblist = self.schedblock_info.SB_UID.tolist()
        for sbuid in sblist:
            self.row_newar(sbuid, new=new)
            new = False

        self.newar.to_pickle(
            self.path + self.preferences.newar_table)

    def get_obsproject(self, code):
        """

        :param code:
        """
        print("Downloading Project %s obsproject.xml" % code)
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

    def row_sciencegoals(self, code, new=False):
        """

        :param code:
        :param new:
        :return:
        """
        c = code
        proj = self.obsproject[self.obsproject.CODE == c].ix[0]
        obsproj = ObsProject(proj.obsproj, self.obsxml)
        assoc_sbs = obsproj.assoc_sched_blocks()
        try:
            for sg in range(len(obsproj.ObsProgram.ScienceGoal)):
                code = code
                sciencegoal = obsproj.ObsProgram.ScienceGoal[sg]
                try:
                    partid = sciencegoal.ObsUnitSetRef.attrib['partId']
                except AttributeError:
                    continue
                perfparam = sciencegoal.PerformanceParameters
                ar = perfparam.desiredAngularResolution.pyval
                arunit = perfparam.desiredAngularResolution.attrib['unit']
                ar = convert_sec(ar, arunit)
                las = perfparam.desiredLargestScale.pyval
                lasunit = perfparam.desiredLargestScale.attrib['unit']
                las = convert_sec(las, lasunit)
                bands = sciencegoal.requiredReceiverBands.pyval
                istimeconst = perfparam.isTimeConstrained.pyval
                if istimeconst:
                    try:
                        temppar = perfparam.TemporalParameters
                        starttime = temppar.startTime.pyval
                        endtime = temppar.endTime.pyval
                        try:
                            allowedmarg = temppar.allowedMargin.pyval
                            allowedmarg_unit = temppar.allowedMargin.attrib[
                                'unit']
                        except AttributeError:
                            allowedmarg = None
                            allowedmarg_unit = None
                        repeats = temppar.repeats.pyval
                        note = temppar.note.pyval
                        try:
                            isavoid = temppar.isAvoidConstraint.pyval
                        except AttributeError:
                            isavoid = None
                    except AttributeError, e:
                        print("Project %s is timeconstrain but no parameters?"
                              "(%s)" % (code, e))
                        temppar, starttime, endtime, allowedmarg = (
                            None, None, None, None)
                        allowedmarg_unit, repeats, note, isavoid = (
                            None, None, None, None)
                else:
                    temppar, starttime, endtime, allowedmarg = (
                        None, None, None, None)
                    allowedmarg_unit, repeats, note, isavoid = (
                        None, None, None, None)

                try:
                    # noinspection PyUnusedLocal
                    ss = sciencegoal.SpectralSetupParameters.SpectralScan
                    isspectralscan = True
                except AttributeError:
                    isspectralscan = False
                useaca = sciencegoal.PerformanceParameters.useACA.pyval
                usetp = sciencegoal.PerformanceParameters.useTP.pyval
                ps = sciencegoal.PerformanceParameters.isPointSource.pyval

                if new:
                    self.sciencegoals = pd.DataFrame(
                        [(code, partid, ar, las, bands, isspectralscan,
                          istimeconst, useaca, usetp, ps, assoc_sbs[partid],
                          starttime, endtime, allowedmarg,
                          allowedmarg_unit, repeats, note, isavoid)],
                        columns=['CODE', 'partId', 'AR', 'LAS', 'bands',
                                 'isSpectralScan', 'isTimeConstrained',
                                 'useACA', 'useTP', 'ps', 'SBS', 'startTime',
                                 'endTime', 'allowedMargin', 'allowedUnits',
                                 'repeats', 'note', 'isavoid'],
                        index=[partid])
                    new = False
                else:
                    df = pd.DataFrame(
                        [(code, partid, ar, las, bands, isspectralscan,
                          istimeconst, useaca, usetp, ps, assoc_sbs[partid],
                          starttime, endtime, allowedmarg,
                          allowedmarg_unit, repeats, note, isavoid)],
                        columns=['CODE', 'partId', 'AR', 'LAS', 'bands',
                                 'isSpectralScan', 'isTimeConstrained',
                                 'useACA', 'useTP', 'ps', 'SBS', 'startTime',
                                 'endTime', 'allowedMargin', 'allowedUnits',
                                 'repeats', 'note', 'isavoid'],
                        index=[partid])
                    self.sciencegoals = pd.concat([self.sciencegoals, df])

        except AttributeError, e:
            print "Project %s has no ObsUnitSets (%s)" % (code, e)
            return 0
        return 0

    def row_schedblock_info(self, sb_uid, new=False):

        # Open SB with SB parser class
        """

        :param sb_uid:
        :param new:
        """
        sb = self.schedblocks.ix[sb_uid]
        pid = sb.partId
        xml = SchedBlocK(sb.sb_xml, self.sbxml)
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
            ampliparam = xml.data.AmplitudeCalParameters
            amplitude = str(ampliparam.attrib['entityPartId'])
        except AttributeError:
            amplitude = None

        try:
            phaseparam = xml.data.PhaseCalParameters
            phase = str(phaseparam.attrib['entityPartId'])
        except AttributeError:
            phase = None

        try:
            bandpassparam = xml.data.BandpassCalParameters
            bandpass = str(bandpassparam.attrib['entityPartId'])
        except AttributeError:
            bandpass = None
        try:
            polarparam = xml.data.PolarizationCalParameters
            polarization = str(polarparam.attrib['entityPartId'])
            ispolarization = True
        except AttributeError:
            ispolarization = False
            polarization = None
        try:
            delayparam = xml.data.DelayCalParameters
            delay = str(delayparam.attrib['entityPartId'])
        except AttributeError:
            delay = None
        scienceparam = xml.data.ScienceParameters
        science = str(scienceparam.attrib['entityPartId'])
        integrationtime = scienceparam.integrationTime.pyval
        integrationtime_unit = scienceparam.integrationTime.attrib['unit']
        integrationtime = convert_tsec(integrationtime, integrationtime_unit)
        subscandur = scienceparam.subScanDuration.pyval
        subscandur_unit = scienceparam.subScanDuration.attrib['unit']
        subscandur = convert_tsec(subscandur, subscandur_unit)

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

        new = new_orig
        if new:
            self.schedblock_info = pd.DataFrame(
                [(sb_uid, pid, name, status,
                  repfreq, band, array, ra, dec, minar_old,
                  maxar_old, execount, ispolarization, amplitude,
                  bandpass, polarization, phase, delay,
                  science, integrationtime, subscandur, maxpwv)],
                columns=['SB_UID', 'partId', 'name', 'status_xml',
                         'repfreq', 'band', 'array', 'RA', 'DEC', 'minAR_old',
                         'maxAR_old', 'execount', 'isPolarization', 'amplitude',
                         'bandpass', 'polarization', 'phase', 'delay',
                         'science', 'integrationTime', 'subScandur', 'maxPWVC'],
                index=[sb_uid])
        else:
            self.schedblock_info.ix[sb_uid] = (
                sb_uid, pid, name, status, repfreq, band, array, ra, dec,
                minar_old, maxar_old, execount, ispolarization,
                amplitude, bandpass, polarization, phase, delay, science,
                integrationtime, subscandur, maxpwv)

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
                         'name', 'RA',
                         'DEC', 'isQuery', 'intendedUse', 'qRA', 'qDEC', 'use',
                         'search_radius', 'rad_unit', 'ephemeris',
                         'pointings', 'isMosaic', 'arraySB'],
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
                [(sbuid, specref, fieldref, paramref)],
                columns=['SB_UID', 'specRef', 'fieldRef', 'paramRef'],
                index=[partid])
        else:
            self.target.ix[partid] = (sbuid, specref, fieldref, paramref)

    def row_spectralconf(self, ss, sbuid, new=False):
        """

        :param ss:
        :param sbuid:
        :param new:
        """
        partid = ss.attrib['entityPartId']
        lspw_res = []
        try:
            corrconf = ss.BLCorrelatorConfiguration
            nbb = len(corrconf.BLBaseBandConfig)
            nspw = 0
            for n in range(nbb):
                bbconf = corrconf.BLBaseBandConfig[n]
                nspw += len(bbconf.BLSpectralWindow)
                for spw in range(len(bbconf.BLSpectralWindow)):
                    tspw = bbconf.BLSpectralWindow
                    bandw = tspw.effectiveBandwidth.pyval
                    bandwun = tspw.effectiveBandwidth.attrib['unit']
                    numchan = tspw.effectiveNumberOfChannels.pyval
                    lspw_res.append(1000. * convert_ghz(bandw, bandwun) /
                                    numchan)
        except AttributeError:
            corrconf = ss.ACACorrelatorConfiguration
            nbb = len(corrconf.ACABaseBandConfig)
            nspw = 0
            for n in range(nbb):
                bbconf = corrconf.ACABaseBandConfig[n]
                nspw += len(bbconf.ACASpectralWindow)
                for spw in range(len(bbconf.ACASpectralWindow)):
                    tspw = bbconf.ACASpectralWindow
                    bandw = tspw.effectiveBandwidth.pyval
                    bandwun = tspw.effectiveBandwidth.attrib['unit']
                    numchan = tspw.effectiveNumberOfChannels.pyval
                    lspw_res.append(1000. * convert_ghz(bandw, bandwun) /
                                    numchan)
        if new:
            self.spectralconf = pd.DataFrame(
                [(partid, sbuid, nbb, nspw, lspw_res)],
                columns=['specRef', 'SB_UID', 'BaseBands', 'SPWs', 'spw_res'],
                index=[partid])
        else:
            df = pd.DataFrame(
                [(partid, sbuid, nbb, nspw, lspw_res)],
                columns=['specRef', 'SB_UID', 'BaseBands', 'SPWs', 'spw_res'],
                index=[partid])
            self.spectralconf = pd.concat([self.spectralconf, df])

    def row_schedblocks(self, sb_uid, partid, new=False):

        """

        :param sb_uid:
        :param partid:
        :param new:
        """
        sql = str(
            "SELECT TIMESTAMP, XMLTYPE.getClobVal(xml) "
            "FROM ALMA.xml_schedblock_entities "
            "WHERE archive_uid = '%s'" % sb_uid)
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

    # noinspection PyUnboundLocalVariable
    def row_newar(self, sbuid, new=False):
        """

        :param sbuid:
        :param new:
        """
        sbinfo = self.schedblock_info.ix[sbuid]
        sb = self.schedblocks.ix[sbuid]
        pid = sb.partId
        sg = self.sciencegoals.ix[pid]
        repfreq = sbinfo.repfreq
        dec = sbinfo.DEC
        c_bmax = 0.4001 / pd.np.cos(pd.np.radians(-23.0262015) -
                                    pd.np.radians(dec)) + 0.6103
        c_freq = repfreq / 100.
        corr = c_freq / c_bmax
        useaca = sg.useACA
        if useaca:
            useaca = 'Y'
        else:
            useaca = 'N'
        ar = sg.AR
        las = sg.LAS
        name = sbinfo['name']
        sbnum = 1
        sbuidE = sbuid
        if name.endswith('TC'):
            name_e = name[:-2] + 'TE'
            try:
                sbinfoE = self.schedblock_info[
                    (self.schedblock_info.name == name_e) &
                    (self.schedblock_info.partId == pid)].ix[0]
                sbnum = 2
                sbuidE = sbinfoE.SB_UID
                sbuidC = sbuid
                print name, name_e
            except IndexError:
                print "Can't find TE for sb %s" % name
                sbnum = 1
        if name.endswith('TE'):
            name_e = name[:-2] + 'TC'
            try:
                sbinfoC = self.schedblock_info[
                    (self.schedblock_info.name == name_e) &
                    (self.schedblock_info.partId == pid)].ix[0]
                sbnum = 2
                sbuidC = sbinfoC.SB_UID
                print name, name_e
            except IndexError:
                sbnum = 1

        newAR = ARes.arrayRes([self.wto_path, ar, las, repfreq, useaca, sbnum])
        newAR.silentRun()
        minarE, maxarE, minarC, maxarC = newAR.run()

        if new and sbnum == 1:
            self.newar = pd.DataFrame(
                [(minarE, maxarE, minarE * corr, maxarE * corr)],
                columns=['minAR', 'maxAR', 'arrayMinAR', 'arrayMaxAR'],
                index=[sbuidE])
        elif new and sbnum == 2:
            self.newar = pd.DataFrame(
                [(minarE, maxarE, minarE * corr, maxarE * corr)],
                columns=['minAR', 'maxAR', 'arrayMinAR', 'arrayMaxAR'],
                index=[sbuidE])
            self.newar.ix[sbuidC] = (minarC, maxarC, minarC * corr,
                                     maxarC * corr)
        else:
            if sbnum == 1:
                self.newar.ix[sbuidE] = (minarE, maxarE, minarE * corr,
                                         maxarE * corr)
            if sbnum == 2:
                self.newar.ix[sbuidE] = (minarE, maxarE, minarE * corr,
                                         maxarE * corr)
                self.newar.ix[sbuidC] = (minarC, maxarC, minarC * corr,
                                         maxarC * corr)

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
            self.obsproject[self.obsproject.CODE.str.startswith('2012')],
            toc2, on='CODE', how='right').set_index(
                'CODE', drop=False)[['CODE']]
        check_c2 = self.obsproject[
            self.obsproject.CODE.str.startswith('2013')][['CODE']]
        self.checked = pd.concat([check_c1, check_c2])
        temp = pd.merge(
            self.obsproject, self.checked, on='CODE',
            copy=False).set_index('CODE', drop=False)
        self.obsproject = temp

    def create_summary(self):
        """


        """
        df1 = pd.merge(
            self.schedblock_info, self.sbstates, left_on='SB_UID',
            right_index=True)[
                ['SB_UID', 'partId', 'name', 'repfreq', 'band', 'array', 'RA',
                 'DEC', 'execount', 'isPolarization', 'amplitude', 'bandpass',
                 'polarization', 'phase', 'delay', 'science', 'integrationTime',
                 'subScandur', 'maxPWVC', 'DOMAIN_ENTITY_STATE']]

        df2 = pd.merge(df1, self.newar, left_on='SB_UID', right_index=True)
        df3 = pd.merge(
            df2, self.sciencegoals[
                ['CODE', 'isSpectralScan', 'isTimeConstrained', 'startTime',
                 'endTime', 'allowedMargin', 'allowedUnits', 'repeats',
                 'isavoid', 'AR', 'LAS', 'ps']], left_on='partId',
            right_index=True)

        qa0group = self.qa0.groupby(['SCHEDBLOCKUID', 'QA0STATUS'])
        qa0count = qa0group.QA0STATUS.count().unstack()
        qpass = qa0count[["Pass"]]
        qunset = qa0count[["Unset"]]

        df4 = pd.merge(
            df3, qpass, left_index=True, right_index=True, how='left',
            copy=False)
        df5 = pd.merge(
            df4, qunset, left_index=True, right_index=True, how='left',
            copy=False)
        i = df5.index
        df5.loc[i, 'Pass'] = df5.Pass.fillna(0)
        df5.loc[i, 'Unset'] = df5.Unset.fillna(0)
        df5['Total'] = df5.Pass + df5.Unset
        self.sb_summary = pd.merge(
            df5, self.obsproject[['PRJ_ARCHIVE_UID', 'EXEC',
                                  'DOMAIN_ENTITY_STATE', 'PRJ_LETTER_GRADE',
                                  'PRJ_SCIENTIFIC_RANK']],
            left_on='CODE', right_index=True, how='left')
        self.sb_summary.columns = pd.Index(
            [u'SB_UID', u'partId', u'name', u'repfreq', u'band', u'array',
             u'RA', u'DEC', u'execount', u'isPolarization', u'amplitude',
             u'bandpass', u'polarization', u'phase', u'delay', u'science',
             u'integrationTime', u'subScandur', u'maxPWVC',
             u'SB_state', u'minAR', u'maxAR', u'arrayMinAR', u'arrayMaxAR',
             u'CODE', u'isSpectralScan', u'isTimeConstrained', u'startTime',
             u'endTime', u'allowedMargin', u'allowedUnits', u'repeats',
             u'isavoid', u'AR', u'LAS', u'isPointSource', u'Pass', u'Unset',
             u'Total', u'PRJ_ARCHIVE_UID', u'EXEC', u'PRJ_state', u'grade',
             u'scienceRank'], dtype='object')
        self.sb_summary.repfreq = pd.np.around(
            self.sb_summary.repfreq, decimals=1)

    def create_allsb(self, split=False, path=None):
        """

        :param split:
        :param path:
        """
        if path is None:
            path = self.path
        allsb = self.sb_summary.copy()[
            ['CODE', 'PRJ_ARCHIVE_UID', 'name', 'SB_UID', 'band', 'repfreq',
             'array', 'EXEC', 'RA', 'DEC']]
        allsb['conf'] = pd.Series(pd.np.zeros(len(allsb)), index=allsb.index)
        allsb.loc[allsb.array == 'TWELVE-M', 'conf'] = 'C34'
        allsb.loc[allsb.array != 'TWELVE-M', 'conf'] = ''
        if split:
            allsb1 = allsb[allsb.CODE.str.startswith('2012')]
            allsb2 = allsb[allsb.CODE.str.startswith('2013')]
            allsb1.sort('CODE').to_csv(
                path + 'allC1.sbinfo', sep='\t', header=False, index=False)
            allsb2.sort('CODE').to_csv(
                path + 'allC2.sbinfo', sep='\t', header=False, index=False)
        else:
            allsb.sort('CODE').to_csv(
                path + 'all.sbinfo', sep='\t', header=False, index=False)

    def forcenew(self):
        """


        """
        call(['rm', '-rf', self.path])
        print self.path + ": creating preferences dir"
        os.mkdir(self.path)
        os.mkdir(self.sbxml)
        os.mkdir(self.obsxml)
        self.start_wto()
        self.populate_sciencegoals_sbxml()
        self.populate_schedblocks()
        self.populate_schedblock_info()
        self.populate_newar()
        self.create_summary()


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