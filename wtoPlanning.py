__author__ = 'itoledo'

import numpy as np
import pandas as pd
import csv
import cx_Oracle
import os
import ephem

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

SSO = ['Moon', 'Sun', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn',
       'Uranus', 'Neptune', 'Pluto']
MOON = ['Ganymede', 'Europa', 'Callisto', 'Io', 'Titan']

alma1 = ephem.Observer()
alma1.lat = '-23.0262015'
alma1.long = '-67.7551257'
alma1.elev = 5060

h = 6.6260755e-27
k = 1.380658e-16
c = 2.99792458e10
c_mks = 2.99792458e8


class WtoPlanning(object):

    def __init__(self, path='/.wto_plan/', forcenew=False):

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
            ['obsproject.pandas', 'sciencegoals.pandas',
             'scheduling.pandas', 'special.list', 'pwvdata.pandas',
             'executive.pandas', 'sbxml_table.pandas', 'sbinfo.pandas',
             'newar.pandas', 'fieldsource.pandas', 'target.pandas',
             'spectralconf.pandas'],
            index=['obsproject_table', 'sciencegoals_table',
                   'scheduling_table', 'special', 'pwv_data',
                   'executive_table', 'sbxml_table', 'sbinfo_table',
                   'newar_table', 'fieldsource_table', 'target_table',
                   'spectralconf_table'])

        self.states = ["Approved", "Phase1Submitted", "Broken",
                       "Canceled", "Rejected"]
        self.states2 = ["Broken", "Canceled", "Rejected"]
        # Global SQL search expressions

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
                self.filter_c1()
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

        self.pwv = 1.2
        self.date = ephem.now()
        self.old_date = 0
        self.array_ar = 0.94
        self.transmission = 0.5
        self.minha = -5.0
        self.maxha = 3.0
        self.minfrac = 0.75
        self.maxfrac = 1.2
        self.horizon = 20.
        self.maxblfrac = 1.5
        self.exec_prio = {'EA': 10., 'NA': 10., 'EU': 10., 'CL': 10.,
                          'OTHER': 10.}

        self.num_ant_user = 34
        self.defarrays = ['C34-1', 'C34-2', 'C34-3', 'C34-4', 'C34-5', 'C34-6',
                          'C34-7']
        self.arr_ar_def = {'C34-1': 3.73, 'C34-2': 2.04, 'C34-3': 1.4,
                           'C34-4': 1.11, 'C34-5': 0.75, 'C34-6': 0.57,
                           'C34-7': 0.41}
        self.array_name = None
        self.not_horizon = False

        self.tau = pd.read_csv(
            self.wto_path + 'conf/tau.csv', sep=',', header=0).set_index('freq')
        self.tsky = pd.read_csv(
            self.wto_path + 'conf/tskyR.csv', sep=',', header=0).set_index(
                'freq')
        self.pwvdata = pd.read_pickle(
            self.wto_path + 'conf/' + self.preferences.pwv_data).set_index(
                'freq')
        self.pwvdata.index = pd.Float64Index(
            pd.np.round(self.pwvdata.index, decimals=1), dtype='float64')
        self.alma = alma1
        self.reciever = pd.DataFrame(
            [55., 45., 75., 110., 51., 150.],
            columns=['trx'],
            index=['ALMA_RB_06', 'ALMA_RB_03', 'ALMA_RB_07', 'ALMA_RB_09',
                   'ALMA_RB_04', 'ALMA_RB_08'])
        self.reciever['g'] = [0., 0., 0., 1., 0., 0.]

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

        self.cursor.execute(self.sql1)
        df1 = pd.DataFrame(
            self.cursor.fetchall(),
            columns=[rec[0] for rec in self.cursor.description])

        states2 = self.states2
        print("Planning mode")
        df2 = df1[
            ((df1.CODE.str.startswith('2013')) &
             (~df1.DOMAIN_ENTITY_STATE.isin(states2)) &
             (df1.PRJ_LETTER_GRADE.isin(['A', 'B']))) |
            ((df1.CODE.str.startswith('2012')) &
             (~df1.DOMAIN_ENTITY_STATE.isin(states)) &
             (df1.PRJ_LETTER_GRADE.isin(['A', 'B'])))]
        print(len(df2))
        self.obsproject = pd.merge(
            df2, self.executive,
            on='PRJ_ARCHIVE_UID').set_index('CODE', drop=False)

        timestamp = pd.Series(
            np.zeros(len(self.obsproject), dtype=object),
            index=self.obsproject.index)
        self.obsproject['timestamp'] = timestamp
        self.obsproject['obsproj'] = pd.Series(
            np.zeros(len(self.obsproject), dtype=object),
            index=self.obsproject.index)
        self.obsproject['p2'] = pd.Series(
            np.zeros(len(self.obsproject), dtype=object),
            index=self.obsproject.index)
        codes = self.obsproject.CODE.tolist()
        for code in codes:
            self.get_obsproject(
                code, self.obsproject.ix[code].DOMAIN_ENTITY_STATE,
                self.obsproject.ix[code].PRJ_ARCHIVE_UID)
        self.filter_c1()
        print len(self.obsproject)
        self.obsproject.to_pickle(
            self.path + self.preferences.obsproject_table)

    def get_obsproject(self, code, state, UID):
        """

        :param code:
        """
        if state not in ['Approved', 'Phase1Submitted']:
            print("Downloading Project %s obsproject.xml" % code)
            self.cursor.execute(
                "SELECT TIMESTAMP, XMLTYPE.getClobVal(xml) "
                "FROM ALMA.XML_OBSPROJECT_ENTITIES "
                "WHERE ARCHIVE_UID = '%s'" % UID)
            data = self.cursor.fetchall()[0]
            xml_content = data[1].read()
            xmlfilename = code + '.xml'
            self.obsproject.loc[code, 'timestamp'] = data[0]
            filename = self.obsxml + xmlfilename
            io_file = open(filename, 'w')
            io_file.write(xml_content)
            io_file.close()
            self.obsproject.loc[code, 'obsproj'] = xmlfilename
            self.obsproject.loc[code, 'p2'] = True
        else:
            print("Downloading Project %s obsproposal.xml" % code)
            self.cursor.execute(
                "SELECT ARCHIVE_UID FROM ALMA.BMMV_OBSPROPOSAL WHERE "
                "PROJECTUID = '%s'" % UID
            )
            prop_uid = self.cursor.fetchall()[0][0]
            self.cursor.execute(
                "SELECT TIMESTAMP, XMLTYPE.getClobVal(xml) "
                "FROM ALMA.XML_OBSPROPOSAL_ENTITIES "
                "WHERE ARCHIVE_UID = '%s'" % prop_uid)
            data = self.cursor.fetchall()[0]
            xml_content = data[1].read()
            xmlfilename = code + '.xml'
            self.obsproject.loc[code, 'timestamp'] = data[0]
            filename = self.obsxml + xmlfilename
            io_file = open(filename, 'w')
            io_file.write(xml_content)
            io_file.close()
            self.obsproject.loc[code, 'obsproj'] = xmlfilename
            self.obsproject.loc[code, 'p2'] = False

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
        for code in codes:
            self.row_sciencegoals(code, new=new)
            new = False
        self.sciencegoals.to_pickle(
            self.path + self.preferences.sciencegoals_table)

    def row_sciencegoals(self, code, new=False):
        """

        :param code:
        :param new:
        :return:
        """
        proj = self.obsproject[self.obsproject.CODE == code].ix[0]
        obsproj = ObsProject(proj.obsproj, code, self.obsxml)
        p2 = proj.p2
        assoc_sbs = obsproj.assoc_sched_blocks()
        try:
            if not p2:
                r1 = range(
                    len(obsproj.data.findall('.//' + prj + 'ScienceGoal')))
            else:
                r1 = range(len(obsproj.ObsProgram.ScienceGoal))
            for sg in r1:
                code = code
                if p2:
                    sciencegoal = obsproj.ObsProgram.ScienceGoal[sg]
                else:
                    sciencegoal = obsproj.data.findall(
                        './/' + prj + 'ScienceGoal')[sg]
                try:
                    partid = sciencegoal.ObsUnitSetRef.attrib['partId']
                    asbs = assoc_sbs[partid]
                except AttributeError:
                    partid = sciencegoal.name.pyval
                    asbs = []
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
                specset = sciencegoal.SpectralSetupParameters
                polar = sciencegoal.SpectralSetupParameters.attrib[
                    'polarisation']
                repfreq = specset.representativeFrequency.pyval
                target = specset.TargetParameters
                try:
                    ssystem = target.attrib['solarSystemObject']
                except KeyError:
                    ssystem = None
                typet = target.attrib['type']
                coord = target.sourceCoordinates
                RA = coord.findall(val + 'longitude')[0].pyval
                DEC = coord.findall(val + 'latitude')[0].pyval
                mosaic = target.isMosaic.pyval


                if new:
                    self.sciencegoals = pd.DataFrame(
                        [(code, partid, ar, las, bands, isspectralscan,
                          istimeconst, useaca, usetp, ps, asbs,
                          starttime, endtime, allowedmarg,
                          allowedmarg_unit, repeats, note, isavoid, polar,
                          RA, DEC, repfreq, ssystem, mosaic, typet)],
                        columns=['CODE', 'partId', 'AR', 'LAS', 'bands',
                                 'isSpectralScan', 'isTimeConstrained',
                                 'useACA', 'useTP', 'ps', 'SBS', 'startTime',
                                 'endTime', 'allowedMargin', 'allowedUnits',
                                 'repeats', 'note', 'isavoid', 'polarization',
                                 'RA', 'DEC', 'repFreq', 'solarSystem', 'mosaic',
                                 'obs_type'],
                        index=[partid])
                    new = False
                else:
                    self.sciencegoals.ix[partid] = (
                        code, partid, ar, las, bands, isspectralscan,
                        istimeconst, useaca, usetp, ps, asbs,
                        starttime, endtime, allowedmarg,
                        allowedmarg_unit, repeats, note, isavoid, polar,
                        RA, DEC, repfreq, ssystem, mosaic, typet)

        except AttributeError, e:
            print "Project %s has no ObsUnitSets (%s)" % (code, e)
            return 0
        return 0

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


class ObsProject(object):
    """

    :param xml_file:
    :param path:
    """

    def __init__(self, xml_file, code, path='./'):
        """

        :param xml_file:
        :param path:
        """
        io_file = open(path + xml_file)
        tree = objectify.parse(io_file)
        io_file.close()
        data = tree.getroot()
        self.code1 = code
        self.data = data
        try:
            self.status = data.attrib['status']
        except KeyError:
            self.status = None
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
                              'SG_OUS' % self.code1)
                        continue
                result[sgid] = sched_uid
        except AttributeError:
            print "Project %s has no Science Goal OUS" % self.code1
        return result

    def import_sched_blocks(self):
        pass

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
