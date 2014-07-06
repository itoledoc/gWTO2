"""
wtoAlgorithm.py: the gWTO selector and scorer library.
------------------------------------------------------
This library contains the classes and functions required to select and rank
SBs from the information that is stored in a WtoDatabse object.
"""

__author__ = 'itoledo'

from datetime import datetime
from datetime import timedelta

import pandas as pd
import ephem
from lxml import objectify

from wtoDatabase import WtoDatabase
import ruvTest as rUV


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
# J = hvkT / (np.exp(hvkT) - 1)

# TebbSky = TebbSkyZenith*(1-np.exp(-airmass*(tau)))/(1-np.exp(-tau))
# TebbSky_Planck = TebbSky*J
# tsys = (1+g)*(t_rx + t_sky*0.95 + 0.05*270) / (0.95 * np.exp(-tau*airmass))


class WtoAlgorithm(WtoDatabase):
    """

    :param path:
    :param source:
    :param forcenew:
    :return:
    """
    def __init__(self, path='/.wto/', source=None, forcenew=False):
        """

        :param path:
        :param source:
        :param forcenew:
        :return:
        """
        super(WtoAlgorithm, self).__init__(path, source, forcenew)
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
        io_file = open(self.wto_path + 'conf/ArrayConfiguration.xml')
        tree = objectify.parse(io_file)
        antfile = tree.getroot()
        io_file.close()
        self.antpad = pd.DataFrame(columns=['pad', 'antenna'])
        for n in range(len(antfile.AntennaOnPad)):
            p = antfile.AntennaOnPad[n].attrib['pad']
            a = antfile.AntennaOnPad[n].attrib['antenna']
            self.antpad.loc[n] = (p, a)
        self.query_arrays()

    # noinspection PyAugmentAssignment
    def selector(self, array):

        """
        Selects SBs that can be observed given the current weather conditions,
        HA range, array type and array configuration (in the case of 12m array
        type) and SB/Project Status. To limit the calculation of pyephem, the
        selection based on current position in the sky is done afterwards.

        Selector get stored in either twelvem, sevenm or totalp tables. These
        tables contain all the data needed for the calculations to be
        done with WtoAlgorith.observable and to assign a score

        :param array: '12m', '7m', 'tp'
        :type array: str
        """
        # TODO: add a 5% padding to fraction selection.
        # TODO: check with Jorge Garcia the rms fraction against reality.

        self.check_observability(array)

        if array not in ['12m', '7m', 'tp']:
            print("Use 12m, 7m or tp for array selection.")
            return None

        else:
            if array == '12m':
                array1 = ['TWELVE-M']
            elif array == '7m':
                array1 = ['SEVEN-M', 'ACA']
            else:
                array1 = ['TP-Array']

        pwvcol = self.pwvdata[[str(self.pwv)]]
        sum2 = pd.merge(
            self.sb_summary, pwvcol, left_on='repfreq', right_index=True)
        sum2 = sum2.rename(
            columns={str(self.pwv): 'transmission'})
        ind1 = sum2.repfreq
        ind2 = pd.np.around(sum2.maxPWVC, decimals=1).astype(str)
        sum2['tau_org'] = self.tau.lookup(ind1, ind2)
        sum2['tsky_org'] = self.tsky.lookup(ind1, ind2)
        sum2['airmass'] = 1 / pd.np.cos(pd.np.radians(-23.0262015 - sum2.DEC))
        sum2 = pd.merge(sum2, self.reciever, left_on='band', right_index=True,
                        how='left')
        tskycol = self.tsky[[str(self.pwv)]]
        sum2 = pd.merge(sum2, tskycol, left_on='repfreq', right_index=True)
        taucol = self.tau[[str(self.pwv)]]
        sum2 = sum2.rename(
            columns={str(self.pwv): 'tsky'})
        sum2 = pd.merge(sum2, taucol, left_on='repfreq', right_index=True)
        sum2 = sum2.rename(
            columns={str(self.pwv): 'tau'})
        print("SBs in sb_summary: %d. SBs merged with tau/tsky info: %d." %
              (len(self.sb_summary), len(sum2)))

        sum2['tsys'] = (
            1 + sum2['g']) * \
            (sum2['trx'] + sum2['tsky'] *
             ((1 - pd.np.exp(-1 * sum2['airmass'] * sum2['tau'])) /
              (1 - pd.np.exp(-1. * sum2['tau']))) * 0.95 + 0.05 * 270.) / \
            (0.95 * pd.np.exp(-1 * sum2['tau'] * sum2['airmass']))
        sum2['tsys_org'] = (
            1 + sum2['g']) * \
            (sum2['trx'] + sum2['tsky_org'] *
             ((1 - pd.np.exp(-1 * sum2['airmass'] * sum2['tau_org'])) /
              (1 - pd.np.exp(-1. * sum2['tau_org']))) * 0.95 + 0.05 * 270.) / \
            (0.95 * pd.np.exp(-1 * sum2['tau_org'] * sum2['airmass']))

        sel1 = sum2[sum2.transmission > self.transmission]

        print("SBs with a transmission higher than %2.1f: %d" %
              (self.transmission, len(sel1)))

        if array == '7m':
            sel2 = sel1[
                (sel1.array == array1[0]) |
                (sel1.array == array1[1])]
        else:
            sel2 = sel1[sel1.array == array1[0]]

        print("SBs for %s array: %d" % (array, len(sel2)))

        self.alma.date = self.date
        lst = pd.np.degrees(self.alma.sidereal_time())
        print self.alma.date, lst
        ha = (lst - sel2.RA) / 15.
        ha.loc[ha > 12] = ha.loc[ha > 12] - 24.
        ha.loc[ha < -12] = 24. + ha.loc[ha < -12]
        sel2['HA'] = ha
        sel2 = sel2
        sel3 = sel2[((sel2.HA > self.minha) & (sel2.HA < self.maxha)) |
                    (sel2.RA == 0.)]
        sel3['tsysfrac'] = (sel3.tsys / sel3.tsys_org) ** 2.
        print("SBs within current HA limits (or RA=0): %d" % len(sel3))
        sel4 = pd.merge(sel3, self.obser_prop, left_on='SB_UID',
                        right_index=True)
        if self.not_horizon is False:
            sel4 = sel4.query('up == 1 and etime > 1.5')
            print("SBs over %d degrees, 1.5 hours: %d" %
                  (self.horizon, len(sel4)))
        sel4 = sel4.query(
            'SB_state != "Phase2Submitted"'
            ' and SB_state != "FullyObserved"'
            ' and SB_state != "Deleted"'
            ' and PRJ_state != "Phase2Submitted"'
            ' and PRJ_state != "Completed"')
        sel4 = sel4[sel4.name.str.contains('not', case=False) == False]
        print("SBs with Ok state: %d" % len(sel4))
        sel4 = sel4.query('execount > Total')
        print("SBs with missing exec: %d" % len(sel4))

        fg = self.fieldsource.query(
            'isQuery == False and name == "Primary:"'
        ).groupby('SB_UID')
        p = pd.DataFrame(
            [fg.pointings.mean(), fg.pointings.count()],
            index=['mpointings', 'sources']).transpose()

        sel4 = pd.merge(sel4, p, left_on='SB_UID', right_index=True, how='left')

        if array == '12m':
            sel4 = sel4.query(
                '(arrayMinAR < %f and %f < arrayMaxAR) ' %
                (self.array_ar, self.array_ar))
            print("SBs for current 12m Array AR: %d. "
                  "(AR=%.2f, #bl=%d, #ant=%d)" %
                  (len(sel4), self.array_ar, self.num_bl, self.num_ant))
            sel4['blmax'] = sel4.apply(
                lambda row: rUV.computeBL(row['AR'], row['repfreq']), axis=1)
            if self.array_name is not None:
                sel4['blfrac'] = sel4.apply(
                    lambda row: (33. * 17) / (1. * len(
                        self.ruv[self.ruv < row['blmax']]))
                    if (row['LAS'] != 0)
                    else (33. * 17) /
                         (self.num_ant * (self.num_ant - 1) / 2.),
                    axis=1)
            else:
                sel4['blfrac'] = sel4.apply(
                    lambda row: (33. * 17) / (1. * len(
                        self.ruv[self.ruv < row['blmax']]))
                    if (row['LAS'] != 0)
                    else (33. * 17) /
                         (34. * (34. - 1) / 2.),
                    axis=1)
                if self.num_ant != 34:
                    sel4['blfrac'] = sel4.blfrac * (
                        33 * 17 / (self.num_ant * (
                            self.num_ant - 1) / 2.))
            sel4['frac'] = sel4.tsysfrac * sel4.blfrac
            self.select12m = sel4

        elif array == '7m':
            sel4['blfrac'] = sel4.RA * 0. + 1.
            print self.num_ant
            if self.num_ant != 9:
                sel4['blfrac'] = sel4.blfrac * (
                    9 * 4 / (self.num_ant * (
                        self.num_ant - 1) / 2.))
            sel4['frac'] = sel4.tsysfrac * sel4.blfrac
            self.select7m = sel4
        else:
            self.selecttp = sel4

    def scorer(self, array):

        """

        :param array:
        """
        if array == '12m':
            df = self.select12m
        elif array == '7m':
            df = self.select7m
        else:
            df = self.selecttp
        self.max_scirank = df.scienceRank.max()
        scores = df.apply(
            lambda r: self.calculate_score(
                r['execount'], r['Total'], r['scienceRank'], r['AR'],
                r['arrayMinAR'], r['arrayMaxAR'], r['LAS'],
                r['grade'], r['repfreq'], r['DEC'], r['EXEC'], array,
                r['frac'], r['maxPWVC'], r['CODE']),
            axis=1)
        scores = pd.DataFrame(scores.values.tolist(), index=scores.index)
        scores.columns = pd.Index(
            [u'sb_cond_score', u'sb_array_score', u'sb_completion_score',
             u'sb_exec_score', u'sb_science_score', u'sb_grade_score',
             u'arcorr', u'score'])
        if array == '12m':
            self.score12m = pd.merge(
                self.select12m, scores, left_on='SB_UID', right_index=True)
        elif array == '7m':
            self.score7m = pd.merge(
                self.select7m, scores, left_on='SB_UID', right_index=True)
        else:
            self.scoretp = pd.merge(
                self.selecttp, scores, left_on='SB_UID', right_index=True)

    def calculate_score(self, ecount, tcount, srank, ar, aminar, amaxar,
                        las, grade, repfreq, dec, execu, array,
                        frac, maxpwvc, code):

        """

        :param ecount:
        :param tcount:
        :param srank:
        :param ar:
        :param aminar:
        :param amaxar:
        :param las:
        :param grade:
        :param repfreq:
        :param dec:
        :param execu:
        :param array:
        :param frac:
        :param maxpwvc:
        :param code:
        :return:
        """
        sb_completion = tcount / ecount
        sb_completion_score = 6. * sb_completion + 4.

        # set sb priority score

        if grade == 'A':
            sb_grade_score = 10.
        elif str(code).startswith('2012'):
            sb_grade_score = 7.
        elif grade == 'B':
            sb_grade_score = 6.
        else:
            sb_grade_score = -100.

        # set science score
        sb_science_score = 10. * srank / self.max_scirank

        # set array score
        if array == '7m' or array == 'tp':
            sb_array_score = 10.
            arcorr = 0.
        else:
            c_bmax = 0.862 / pd.np.cos(pd.np.radians(-23.0262015) -
                                       pd.np.radians(dec)) + 0.138
            c_freq = repfreq / 100.
            corr = c_freq / c_bmax
            arcorr = ar * corr
            if self.array_ar < arcorr:
                l = arcorr - aminar
                s = 10.

                if las == 0:
                    sb_array_score = (
                        ((self.array_ar - aminar) / l) ** (1 / 8.)) * 8. + 2.
                else:
                    sb_array_score = (
                        ((self.array_ar - aminar) / l) ** (1 / 3.)) * s
            elif self.array_ar == arcorr:
                sb_array_score = 10.
            else:
                l = arcorr - amaxar
                s = 10. / l
                sb_array_score = (self.array_ar - amaxar) * s
        # set exec score:
        sb_exec_score = self.exec_prio[execu]

        # set condition score:
        pwv_corr = 1 - (abs(self.pwv - maxpwvc) / 6.)
        if pwv_corr > 6:
            pwv_corr = 0.

        if frac < 1:
            x = frac - 1.
            sb_cond_score = 10 * (1 - (x ** 2.)) * pwv_corr
        elif frac == 1:
            sb_cond_score = 10.
        else:
            x = frac - 1
            if frac <= 1.4:
                sb_cond_score = (1. - (x / 0.4) ** 3.) * 10. * pwv_corr
            else:
                sb_cond_score = 0.

        score = (0.35 * sb_cond_score +
                 0.20 * sb_array_score +
                 0.15 * sb_completion_score +
                 0.10 * sb_exec_score +
                 0.05 * sb_science_score +
                 0.15 * sb_grade_score)
        return (sb_cond_score, sb_array_score, sb_completion_score,
                sb_exec_score, sb_science_score, sb_grade_score, arcorr, score)

    def check_observability(self, array):

        """

        :param array:
        :return:
        """
        if self.date == self.old_date:
            return None
        alma1.date = self.date
        print alma1.date
        if array == '12m':
            fs_arr = self.fieldsource.query('arraySB == "TWELVE-M"')
        elif array == '7m':
            fs_arr = self.fieldsource.query('arraySB == "ACA" or '
                                            'arraySB == "SEVEN-M"')
        else:
            fs_arr = self.fieldsource.query('arraySB == "TP-Array"')

        print("Calculating observability for %d sources..." %
              len(fs_arr))
        fs = fs_arr.apply(
            lambda r: observable(
                r['solarSystem'], r['sourcename'], r['RA'], r['DEC'],
                self.horizon, r['isQuery'], r['ephemeris'], alma=alma1),
            axis=1)
        df_fs = pd.DataFrame(
            fs.values.tolist(),
            index=fs.index,
            columns=['RA', 'DEC', 'elev', 'remaining', 'rise', 'sets', 'lstr',
                     'lsts', 'observable'])
        fs_1 = pd.merge(
            fs_arr[['fieldRef', 'SB_UID', 'isQuery']],
            df_fs, left_index=True, right_index=True,
            how='left')
        fs_1g = fs_1.query('isQuery == False').groupby('SB_UID')
        allup = pd.DataFrame(
            fs_1g.observable.mean())
        allup.columns = pd.Index([u'up'])
        fs_2 = pd.merge(fs_1, allup, left_on='SB_UID', right_index=True,
                        how='left')
        fs_2g = fs_2.query('isQuery == False').groupby('SB_UID')
        etime = pd.DataFrame(
            fs_2g.remaining.min()[fs_2g.remaining.min() > 1.5])
        etime.columns = pd.Index([u'etime'])

        elevation = pd.DataFrame(
            fs_2g.elev.mean())
        elevation.columns = pd.Index([u'elev'])

        lstr = pd.DataFrame(
            fs_2g.lstr.max())
        lstr.columns = pd.Index([u'lstr'])

        lsts = pd.DataFrame(
            fs_2g.lsts.max())
        lsts.columns = pd.Index([u'lsts'])

        dec = pd.DataFrame(
            fs_2g.DEC.mean())
        dec.columns = pd.Index([u'DEC'])

        fs_3 = pd.merge(allup, etime, right_index=True, left_index=True,
                        how='left')
        fs_4 = pd.merge(fs_3, elevation, right_index=True,
                        left_index=True, how='left')
        fs_5 = pd.merge(fs_4, lstr, right_index=True,
                        left_index=True, how='left')

        self.sb_summary.loc[dec.index, 'DEC'] = dec.loc[dec.index, 'DEC']
        self.obser_prop = pd.merge(fs_5, lsts, right_index=True,
                                   left_index=True, how='left')
        self.old_date = self.date
        print self.old_date, self.date

    def set_trans(self, transmission):
        """

        :param transmission:
        """
        self.transmission = transmission

    def set_pwv(self, pwv):
        """

        :param pwv:
        """
        self.pwv = pwv

    def set_date(self, date):
        """

        :param date:
        """
        self.date = date

    def set_arrayar(self, ar):
        """

        :param ar:
        """
        self.array_ar = ar

    def set_minha(self, ha):
        """

        :param ha:
        """
        self.minha = ha

    def set_maxha(self, ha):
        """

        :param ha:
        """
        self.maxha = ha

    def set_array_ar(self, ar):
        """

        :param ar:
        """
        self.array_ar = ar

    def query_arrays(self):
        """


        """
        a = str(
            "with t1 as ( "
            "select se.SE_TIMESTAMP ts1, sa.SLOG_ATTR_VALUE av1, se.SE_ID se1 "
            "from ALMA.SHIFTLOG_ENTRIES se, ALMA.SLOG_ENTRY_ATTR sa "
            "WHERE se.SE_TYPE=7 and se.SE_TIMESTAMP > SYSDATE - 1/1. "
            "and sa.SLOG_SE_ID = se.SE_ID and sa.SLOG_ATTR_TYPE = 32 "
            "and se.SE_LOCATION='OSF-AOS'), "
            "t2 as ( "
            "select sa.SLOG_ATTR_VALUE av2, se.SE_ID se2 "
            "from ALMA.SHIFTLOG_ENTRIES se, ALMA.SLOG_ENTRY_ATTR sa "
            "WHERE se.SE_TYPE=7 and se.SE_TIMESTAMP > SYSDATE - 1/1. "
            "and sa.SLOG_SE_ID = se.SE_ID and sa.SLOG_ATTR_TYPE = 39 "
            "and se.SE_LOCATION='OSF-AOS' "
            ") "
            "select t1.*, t2.av2 from t1,t2 where t1.se1 = t2.se2 "
            "and av2 = 'BL'"
        )
        try:
            self.cursor.execute(a)
            self.bl_arrays = pd.DataFrame(
                self.cursor.fetchall(),
                columns=[rec[0] for rec in self.cursor.description]
            ).sort('TS1', ascending=False)
        except ValueError:
            self.bl_arrays = pd.DataFrame(
                columns=pd.Index(
                    [u'TS1', u'AV1', u'SE1', u'AV2'], dtype='object'))
            print "No BL arrays have been created in the last 6 hours."
        b = str(
            "WITH t1 AS ( "
            "select se.SE_TIMESTAMP ts1, sa.SLOG_ATTR_VALUE av1, se.SE_ID se1 "
            "from ALMA.SHIFTLOG_ENTRIES se, ALMA.SLOG_ENTRY_ATTR sa "
            "WHERE se.SE_TYPE=7 and se.SE_TIMESTAMP > SYSDATE - 1/1. "
            "and sa.SLOG_SE_ID = se.SE_ID and sa.SLOG_ATTR_TYPE = 32 "
            "and se.SE_LOCATION='OSF-AOS'), "
            "t2 as ( "
            "select sa.SLOG_ATTR_VALUE av2, se.SE_ID se2 "
            "from ALMA.SHIFTLOG_ENTRIES se, ALMA.SLOG_ENTRY_ATTR sa "
            "WHERE se.SE_TYPE=7 and se.SE_TIMESTAMP > SYSDATE - 1/1. "
            "and sa.SLOG_SE_ID = se.SE_ID and sa.SLOG_ATTR_TYPE = 39 "
            "and se.SE_LOCATION='OSF-AOS' "
            ") "
            "select t1.*, t2.av2 from t1,t2 where t1.se1 = t2.se2 "
            "and av2 = 'ACA'"
        )
        try:
            self.cursor.execute(b)
            self.aca_arrays = pd.DataFrame(
                self.cursor.fetchall(),
                columns=[rec[0] for rec in self.cursor.description]
            ).sort('TS1', ascending=False)
        except ValueError:
            self.aca_arrays = pd.DataFrame(
                columns=pd.Index(
                    [u'TS1', u'AV1', u'SE1', u'AV2'], dtype='object'))
            print "No ACA arrays have been created in the last 6 hours."

    def set_bl_prop(self, array_name):
        # TODO: check uv coverage to remove baselines that are outliers
        """

        :param array_name:
        """
        # In case a bl_array is selected
        if (array_name is not None and len(self.bl_arrays) != 0
                and array_name not in self.defarrays):
            id1 = self.bl_arrays.query('AV1 == "%s"' % array_name).iloc[0].SE1

            a = str("SELECT SLOG_ATTR_VALUE FROM ALMA.SLOG_ENTRY_ATTR "
                    "WHERE SLOG_ATTR_TYPE = 31 "
                    "AND SLOG_SE_ID=%d" % id1)
            self.cursor.execute(a)
            ap = pd.DataFrame(self.cursor.fetchall(), columns=['antenna'])
            ap = ap[ap.antenna.str.contains('CM') == False]
            conf = pd.merge(self.antpad, ap,
                            left_on='antenna', right_on='antenna')
            conf_file = self.path + '%s.txt' % array_name
            conf.to_csv(conf_file, header=False,
                        index=False, sep=' ')
            ac = rUV.ac.ArrayConfigurationCasaFile()
            ac.createCasaConfig(conf_file)
            self.ruv = rUV.computeRuv(conf_file + ".cfg")
            self.num_bl = len(self.ruv)
            self.num_ant = len(ap)

        # If default or C34 is selected
        else:
            if array_name is None:
                conf_file = self.wto_path + 'conf/default.txt'
                io_file = open(
                    self.wto_path + 'conf/arrayConfigurationResults.txt')
                self.array_ar = float(io_file.readlines()[13].split(':')[1])
                io_file.close()
                ac = rUV.ac.ArrayConfigurationCasaFile()
                ac.createCasaConfig(conf_file)
                self.ruv = rUV.computeRuv(conf_file + ".cfg")
            else:
                conf_file = self.wto_path + 'conf/%s.txt.cfg' % array_name
                self.ruv = rUV.computeRuv(conf_file)
                # noinspection PyTypeChecker
                self.array_ar = self.arr_ar_def[array_name]
                self.num_ant = 34

            if len(self.ruv) > 33. * 17.:
                self.ruv = self.ruv[-561:]
                self.num_bl = len(self.ruv)
                self.num_ant = 34


# noinspection PyPep8Naming
def observable(solarSystem, sourcename, RA, DEC, horizon, isQuery, ephemeris,
               alma):
    """

    :param solarSystem:
    :param sourcename:
    :param RA:
    :param DEC:
    :param horizon:
    :param isQuery:
    :param ephemeris:
    :param alma:
    :return:
    """
    dtemp = alma.date
    alma.horizon = ephem.degrees(str(horizon))
    if isQuery:
        alma.date = dtemp
        return 0, 0, 0, 0, 0, 0, 0, 0, False

    if solarSystem != 'Unspecified':
        if solarSystem in SSO and solarSystem == sourcename:
            obj = eval('ephem.' + solarSystem + '()')
            obj.compute(alma)
            ra = obj.ra
            dec = obj.dec
            elev = obj.alt
            neverup = False
        elif solarSystem in MOON:
            obj = eval('ephem.' + solarSystem + '()')
            obj.compute(alma)
            ra = obj.ra
            dec = obj.dec
            elev = obj.alt
            obj.radius = 0.
            neverup = False
        elif solarSystem == 'Ephemeris':
            ra, dec, ephe = read_ephemeris(ephemeris, alma.date)
            if not ephe:
                alma.date = dtemp
                return 0, 0, 0, 0, 0, 0, 0, 0, False
            obj = ephem.FixedBody()
            obj._ra = pd.np.deg2rad(ra)
            obj._dec = pd.np.deg2rad(dec)
            obj.compute(alma)
            ra = obj.ra
            dec = obj.dec
            elev = obj.alt
            neverup = obj.neverup

        else:
            alma.date = dtemp
            return 0, 0, 0, 0, 0, 0, 0, 0, False

    else:
        obj = ephem.FixedBody()
        obj._ra = pd.np.deg2rad(RA)
        obj._dec = pd.np.deg2rad(DEC)
        obj.compute(alma)
        ra = obj.ra
        dec = obj.dec
        elev = obj.alt
        neverup = obj.neverup

    if obj.alt > ephem.degrees(str(horizon)):
        try:
            c2 = obj.circumpolar
        except AttributeError:
            c2 = False
        if not c2:
            sets = alma.next_setting(obj)
            rise = alma.previous_rising(obj)
            remaining = sets.datetime() - dtemp.datetime()
            alma.date = rise
            lstr = alma.sidereal_time()
            alma.date = sets
            lsts = alma.sidereal_time()
            obs = True
        else:
            remaining = timedelta(1)
            lstr = ephem.hours('0')
            lsts = ephem.hours('0')
            rise = ephem.hours('0')
            sets = ephem.hours('0')
            obs = True
    else:
        if neverup:
            print("Source %s is never over %d deg. of elev. (%s, %s, %s)" %
                  (sourcename, horizon, obj.dec, obj.ra, alma.date))
            remaining = timedelta(0)
            alma.horizon = ephem.degrees('0')
            obj.compute(alma)
            lstr = ephem.hours('0')
            lsts = ephem.hours('0')
            rise = ephem.hours('0')
            sets = ephem.hours('0')
            obs = False
        else:
            rise = alma.next_rising(obj)
            sets = alma.next_setting(obj)
            remaining = dtemp.datetime() - rise.datetime()
            alma.date = rise
            lstr = alma.sidereal_time()
            alma.date = sets
            lsts = alma.sidereal_time()
            obs = False

    alma.date = dtemp
    alma.horizon = ephem.degrees(str(horizon))
    return str(ra), pd.np.degrees(dec), pd.np.degrees(elev),\
        remaining.total_seconds() / 3600., rise, sets, lstr, lsts, obs


def read_ephemeris(ephemeris, date):
    # TODO: is the ephemeris file fixed in col positions?

    """

    :param ephemeris:
    :param date:
    :return:
    """
    in_data = False
    now = date
    month_ints = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
    found = False
    for line in ephemeris.split('\n'):
        if line.startswith('$$SOE'):
            in_data = True
            c1 = 0
        elif line.startswith('$$EOE'):
            if not found:
                # print "NO EPHEMERIS FOR CURRENT DATE. Setting RA=0, DEC=0"
                ra = ephem.hours('00:00:00')
                dec = ephem.degrees('00:00:00')
                ephe = False
                return ra, dec, ephe
        elif in_data:
            datestr = line[1:6] + str(month_ints[line[6:9]]) + line[9:18]
            date = datetime.strptime(datestr, '%Y-%m-%d %H:%M')
            if now.datetime() > date:
                data = line
                found = False
                # noinspection PyUnboundLocalVariable
                c1 += 1
            else:
                # noinspection PyUnboundLocalVariable
                if c1 == 0:

                    ra = ephem.hours('00:00:00')
                    dec = ephem.degrees('00:00:00')
                    ephe = False
                    return ra, dec, ephe
                # noinspection PyUnboundLocalVariable
                ra = ephem.hours(data[23:36].strip().replace(' ', ':'))
                dec = ephem.degrees(data[37:51].strip().replace(' ', ':'))
                ephe = True
                print ra, dec, ephe
                return pd.np.degrees(ra), pd.np.degrees(dec), ephe
