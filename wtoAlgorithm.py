"""
wtoAlgorithm.py: the gWTO selector and scorer library.
======================================================
This library contains the classes and functions required to select and rank
SBs from the information that is stored in a WtoDatabse object.
"""

__author__ = 'itoledo'

from datetime import datetime
from datetime import timedelta
import numpy as np

import pandas as pd
import ephem
from lxml import objectify

from wtoDatabase import WtoDatabase
import ruvTest as rUV
from scipy.stats import rayleigh

confDf = pd.DataFrame(
    [('C34-1', 3.73, 2.49, 1.62, 1.08, 0.81, 0.57)],
    columns=['Conf', 'ALMA_RB_03', 'ALMA_RB_04', 'ALMA_RB_06', 'ALMA_RB_07',
             'ALMA_RB_08', 'ALMA_RB_09'],
    index=['C34-1'])
confDf.ix['C34-2'] = ('C34-2', 2.04, 1.36, 0.89, 0.59, 0.44, 0.31)
confDf.ix['C34-3'] = ('C34-3', 1.4, 0.93, 0.61, 0.4, 0.3, 0.21)
confDf.ix['C34-4'] = ('C34-4', 1.11, 0.74, 0.48, 0.32, 0.24, 0.17)
confDf.ix['C34-5'] = ('C34-5', 0.75, 0.50, 0.33, 0.22, 0.16, 0.12)
confDf.ix['C34-6'] = ('C34-6', 0.57, 0.38, 0.25, 0.16, 0.12, 0.09)
confDf.ix['C34-7'] = ('C34-7', 0.41, 0.27, 0.18, 0.12, None, None)

pwn = [0., 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35,
       0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75,
       0.8, 0.85, 0.9, 0.95, 1., 1.05, 1.1, 1.15,
       1.2, 1.25, 1.3, 1.35, 1.4, 1.45, 1.5, 1.55,
       1.6, 1.65, 1.7, 1.75, 1.8, 1.85, 1.9, 1.95,
       2., 2.05, 2.1, 2.15, 2.2, 2.25, 2.3, 2.35,
       2.4, 2.45, 2.5, 2.55, 2.6, 2.65, 2.7, 2.75,
       2.8, 2.85, 2.9, 2.95, 3., 3.05, 3.1, 3.15,
       3.2, 3.25, 3.3, 3.35, 3.4, 3.45, 3.5, 3.55,
       3.6, 3.65, 3.7, 3.75, 3.8, 3.85, 3.9, 3.95,
       4., 4.05, 4.1, 4.15, 4.2, 4.25, 4.3, 4.35,
       4.4, 4.45, 4.5, 4.55, 4.6, 4.65, 4.7, 4.75,
       4.8, 4.85, 4.9, 4.95, 5., 5.05, 5.1, 5.15,
       5.2, 5.25, 5.3, 5.35, 5.4, 5.45, 5.5, 5.55,
       5.6, 5.65, 5.7, 5.75, 5.8, 5.85, 5.9, 5.95,
       6., 6.2, 6.4, 6.6, 6.8, 7., 7.2, 7.4,
       7.6, 7.8, 8., 8.2, 8.4, 8.6, 8.8, 9.,
       9.2, 9.4, 9.6, 9.8, 10., 10.2, 10.4, 10.6,
       10.8, 11., 11.2, 11.4, 11.6, 11.8, 12., 12.2,
       12.4, 12.6, 12.8, 13., 13.2, 13.4, 13.6, 13.8,
       14., 14.2, 14.4, 14.6, 14.8, 15., 15.2, 15.4,
       15.6, 15.8, 16., 16.2, 16.4, 16.6, 16.8, 17.,
       17.2, 17.4, 17.6, 17.8, 18., 18.2, 18.4, 18.6,
       18.8, 19., 19.2, 19.4, 19.6, 19.8, 20.]

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


# noinspection PyUnresolvedReferences
class WtoAlgorithm(WtoDatabase):
    """
    Inherits from WtoDatabase, adds the methods for selection and scoring.
    It also sets the default parameters for these methods: pwv=1.2, date=now,
    array angular resolution, transmission=0.5, minha=-5, maxha=3, etc.

    :param path: A path, relative to $HOME, where the cache is stored.
    :type path: (default='/.wto/') String.
    :param source: See WtoDatabase definitions.
    :param forcenew: See WtoDatabase definitions.
    :return: A WtoAlgorithm instance.
    """
    def __init__(self, path='/.wto/', source=None, forcenew=False):

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
        type) and SB/Project Status. See
        :ref:`Selection and Data preparation <selection>`

        :param array: '12m', '7m', 'tp'
        :type array: String.
        :return: Depending on the array type, creates tables select12m, select7m
           or selecttp.
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

        sel = self.sb_summary.copy()

        if array == '7m':
            sel = sel[
                (sel.array == array1[0]) |
                (sel.array == array1[1])]
        else:
            sel = sel[sel.array == array1[0]]

        print("SBs for %s array: %d" % (array, len(sel)))

        pwvcol = self.pwvdata[[str(self.pwv)]]

        len_bf_cond = len(sel)
        sel = pd.merge(
            sel, pwvcol, left_on='repfreq', right_index=True)
        sel.rename(columns={str(self.pwv): 'transmission'}, inplace=True)
        ind1 = sel.repfreq
        ind2 = pd.np.around(sel.maxPWVC, decimals=1).astype(str)

        sel['tau_org'] = self.tau.lookup(ind1, ind2)
        sel['tsky_org'] = self.tsky.lookup(ind1, ind2)
        sel['airmass'] = 1 / pd.np.cos(pd.np.radians(-23.0262015 - sel.DEC))
        sel = pd.merge(sel, self.reciever, left_on='band', right_index=True,
                       how='left')
        tskycol = self.tsky[[str(self.pwv)]]

        sel = pd.merge(sel, tskycol, left_on='repfreq', right_index=True)
        taucol = self.tau[[str(self.pwv)]]
        sel.rename(columns={str(self.pwv): 'tsky'}, inplace=True)
        sel = pd.merge(sel, taucol, left_on='repfreq', right_index=True)
        sel.rename(columns={str(self.pwv): 'tau'}, inplace=True)

        print("SBs in sb_summary: %d. SBs merged with tau/tsky info: %d." %
              (len_bf_cond, len(sel)))

        sel['sel_array'] = False

        # Patch for hybrid configuration, C34-6 & C34-7

        self.ruv.sort()
        ruv6 = self.ruv[self.ruv < 1091.].copy()
        x = np.linspace(0, ruv6.max() + 100., 1000)
        param = rayleigh.fit(ruv6)
        maxl6 = np.min([ruv6.max(), rayleigh.interval(0.992, loc=param[0], scale=param[1])[1]])
        self.ruv6 = ruv6.copy()
        self.res6 = 61800 / (100. * maxl6)
        self.blnum6 = len(ruv6)
        if self.blnum6 < 591:
            self.ruv6 = self.ruv.copy()
            self.res6 = self.array_ar
        print self.blnum6, self.res6

        if array == '12m':
            sel.loc[
                ((sel.arrayMinAR <= self.array_ar) & (sel.arrayMaxAR >= self.array_ar)) |
                ((sel.arrayMinAR <= self.res6) & (sel.arrayMaxAR >= self.res6)) |
                ((sel.arrayMinAR >= self.array_ar) & (sel.arrayMaxAR <= self.res6))
                , 'sel_array'] = True

            print("SBs for current 12m Array AR: %d. "
                  "(AR=%.2f, #bl=%d, #ant=%d)" %
                  (len(sel.query('sel_array == True')), self.array_ar,
                   self.num_bl, self.num_ant))

            sel['blmax'] = sel.apply(
                lambda row: rUV.computeBL(row['AR'], row['repfreq']), axis=1)
            sel['blmin'] = sel.apply(
                lambda row: rUV.computeBL(row['LAS'], row['repfreq']), axis=1)

            if self.array_name is not None:
                sel['blfrac'] = sel.apply(
                    lambda row: (33. * 17) / (1. * len(
                        self.ruv[(self.ruv <= row['blmax'])]))
                    if (row['isPointSource'] == False)
                    else (33. * 17) / (self.num_ant * (self.num_ant - 1) / 2.), axis=1)
            else:
                sel['blfrac'] = sel.apply(
                    lambda row: (33. * 17) / (1. * len(
                        self.ruv[self.ruv < row['blmax']]))
                    if (row['isPointSource'] == False)
                    else (33. * 17) /
                         (34. * (34. - 1) / 2.),
                    axis=1)
                if self.num_ant != 34:
                    sel.loc[:, 'blfrac'] = sel.loc[:, 'blfrac'] * (
                        33 * 17 / (self.num_ant * (
                            self.num_ant - 1) / 2.))

            sel.loc[:, 'blfrac'] = sel.apply(
                lambda row: ret_cycle(row[u'CODE'], row['blfrac']), axis=1
            )

        elif array == '7m':
            sel['sel_array'] = True
            sel['blfrac'] = 1.
            if self.num_ant != 9:
                sel.loc[:, 'blfrac'] = sel.loc[:, 'blfrac'] * (
                    9 * 4 / (self.num_ant * (
                        self.num_ant - 1) / 2.))

        else:
            sel['sel_array'] = True
            sel['blfrac'] = 1.

        sel['tsys'] = (
            1 + sel['g']) * \
            (sel['trx'] + sel['tsky'] *
             ((1 - pd.np.exp(-1 * sel['airmass'] * sel['tau'])) /
              (1 - pd.np.exp(-1. * sel['tau']))) * 0.95 + 0.05 * 270.) / \
            (0.95 * pd.np.exp(-1 * sel['tau'] * sel['airmass']))
        sel['tsys_org'] = (
            1 + sel['g']) * \
            (sel['trx'] + sel['tsky_org'] *
             ((1 - pd.np.exp(-1 * sel['airmass'] * sel['tau_org'])) /
              (1 - pd.np.exp(-1. * sel['tau_org']))) * 0.95 + 0.05 * 270.) / \
            (0.95 * pd.np.exp(-1 * sel['tau_org'] * sel['airmass']))

        sel['sel_trans'] = False

        sel.loc[(sel.transmission > self.transmission) | (sel.maxPWVC >= self.pwv),
                'sel_trans'] = True

        print("SBs with a transmission higher than %2.1f: %d" %
              (self.transmission,
               len(sel.query('sel_array == True and sel_trans == True'))))

        self.alma.date = self.date
        lst = pd.np.degrees(self.alma.sidereal_time())

        ha = (lst - sel.RA) / 15.
        ha.loc[ha > 12] = ha.loc[ha > 12] - 24.
        ha.loc[ha < -12] = 24. + ha.loc[ha < -12]
        sel['HA'] = ha
        sel['sel_ha'] = False
        sel.loc[
            ((sel.HA > self.minha) & (sel.HA < self.maxha)) |
            (sel.RA == 0.), 'sel_ha'] = True

        s3 = len(sel.query('sel_array == True and sel_trans == True and'
                           ' sel_ha == True'))
        print("SBs within current HA limits (or RA=0): %d" % s3)

        sel['tsysfrac'] = (sel.tsys / sel.tsys_org) ** 2.
        sel = pd.merge(sel, self.obser_prop, left_on='SB_UID',
                       right_index=True)

        sel['sel_el'] = False

        if self.not_horizon is False:
            sel.loc[(sel.up == 1) & (sel.etime > 1.5), 'sel_el'] = True
            s4 = len(
                sel.query('sel_array == True and sel_trans == True and'
                          ' sel_ha == True and sel_el == True'))
            print("SBs over %d degrees, 1.5 hours: %d" %
                  (self.horizon, s4))

        sel['sel_st'] = False
        sel.loc[(sel.SB_state != "Phase2Submitted") &
                (sel.SB_state != "FullyObserved") &
                (sel.SB_state != "Deleted") &
                (sel.SB_state != "Canceled") &
                (sel.PRJ_state != "Phase2Submitted") &
                (sel.PRJ_state != "Completed"), 'sel_st'] = True
        sel.loc[
            (sel.name.str.contains('not', case=False) == True),
            'sel_st'] = False

        s5 = len(
            sel.query(
                'sel_array == True and sel_trans == True and sel_ha == True '
                'and sel_el == True and sel_st == True'))
        print("SBs with Ok state: %d" % s5)

        sel['sel_exe'] = False
        sel.loc[sel.execount > sel.Total, 'sel_exe'] = True

        s6 = len(
            sel.query(
                'sel_array == True and sel_trans == True and sel_ha == True '
                'and sel_el == True and sel_st == True and sel_exe == True'))

        print("SBs with missing exec: %d" % s6)

        sel['frac'] = sel.tsysfrac * sel.blfrac
        fg = self.fieldsource.query(
            'isQuery == False and name == "Primary:"'
        ).groupby('SB_UID')
        p = pd.DataFrame(
            [fg.pointings.mean(), fg.pointings.count()],
            index=['mpointings', 'sources']).transpose()

        sel = pd.merge(sel, p, left_on='SB_UID', right_index=True, how='left')

        if array == '12m':
            self.select12m = sel.query(
                'sel_array == True and sel_trans == True and sel_ha == True '
                'and sel_el == True and sel_st == True and sel_exe == True and '
                'frac < 2.1')

            self.all12m = sel
            print("SBs with 'frac' < 2.1: %d" % len(self.select12m))

        elif array == '7m':
            self.select7m = sel.query(
                'sel_array == True and sel_trans == True and sel_ha == True '
                'and sel_el == True and sel_st == True and sel_exe == True and '
                'frac < 2.1')

            self.all7m = sel
            print("SBs with 'frac' < 2.1: %d" % len(self.select7m))

        else:
            self.selecttp = sel.query(
                'sel_array == True and sel_trans == True and sel_ha == True '
                'and sel_el == True and sel_st == True and sel_exe == True and '
                'frac < 2.1')

            self.alltp = sel
            print("SBs with 'frac' < 2.1: %d" % len(self.selecttp))

    def scorer(self, array):

        """
        Method that handles the score calculation for each array type. It
        applies ``self.calculate_score()`` to the previously selected SBs using
        ``self.selector()``

        :param array: '12m', '7m', 'tp'
        :type array: String.
        :return: Creates a score table for the instance, which will be named as
           ``score12m``, ``score7m`` or ``scoretp``.
        """

        if array == '12m':
            try:
                df = self.select12m
            except AttributeError:
                print("Please execute method self.selector('12m') first.")
                return None
        elif array == '7m':
            try:
                df = self.select7m
            except AttributeError:
                print("Please execute method self.selector('7m') first.")
                return None
        elif array == 'tp':
            try:
                df = self.selecttp
            except AttributeError:
                print("Please execute method self.selector('tp') first.")
                return None
        else:
            print("array must be either 12m, 7m or tp.")
            return None

        self.max_scirank = df.scienceRank.max()
        if len(df) > 0:
            scores = df.apply(
                lambda r: self.calculate_score(
                    r['execount'], r['Total'], r['scienceRank'], r['AR'],
                    r['arrayMinAR'], r['arrayMaxAR'], r['LAS'],
                    r['grade'], r['repfreq'], r['DEC'], r['EXEC'], array,
                    r['frac'], r['maxPWVC'], r['CODE'], r['isPointSource'],
                    r['name'], r['HA']),
                axis=1)
            scores = pd.DataFrame(scores.values.tolist(), index=scores.index)
            scores.columns = pd.Index(
                [u'sb_cond_score', u'sb_array_score', u'sb_completion_score',
                 u'sb_ha_scorer',
                 u'sb_exec_score', u'sb_science_score', u'sb_grade_score',
                 u'arcorr', u'score', u'lascorr'])
        else:
            scores = pd.DataFrame(
                columns=pd.Index(
                    [u'sb_cond_score', u'sb_array_score',
                     u'sb_completion_score', u'sb_ha_scorer', u'sb_exec_score',
                     u'sb_science_score', u'sb_grade_score', u'arcorr',
                     u'score', u'lascorr']))
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
                        frac, maxpwvc, code, points, name, ha):

        """
        Please go to the :ref:`Score and ranking <score>` section for an
        algorithm's description.

        :param ecount: Executions requested by the SB
        :type ecount: Integer.
        :param tcount: Total executions with QA0 Pass or Unset for the SB.
        :type tcount: Integer.
        :param srank: SB Science ranking.
        :type srank: Intenger
        :param ar: SB requested Angular Resolution, from the Science Goal.
        :type ar: Float.
        :param aminar: The minum angular resolution the SB can accept to be
           observed.
        :type aminar: Float. In arcsec.
        :param amaxar: The maximum angular resolution the SB can accept to be
           observed.
        :type amaxar: Float. In arcsec.
        :param las: SB requested Largest Angular Scale, from the Science Goal.
        :type las: Float. In arcsec.
        :param grade: SB's Project letter grade.
        :type grade: String, can be A, B or C.
        :param repfreq: SB's representative frequency.
        :type repfreq: Float, in GHz.
        :param dec: SB's representative declination coordinates, as determined
           by self.check_observability().
        :type dec: Float, in degrees.
        :param execu: SB's Project Executive.
        :type execu: String, can be NA, EU, EA, CL or OTHER.
        :param array: Array type.
        :type array: String, can be 12m, 7m or tp.
        :param frac: Total time fraction calculated by self.selector() for the
           SB to reach the required sensitivity.
        :type frac: Float.
        :param maxpwvc: SB's maxPWVC variable.
        :type maxpwvc: Float, a value between 0 and 20.
        :param code: SB's project code.
        :type code: String.
        :return: Tuple with ...
        """
        sb_completion = tcount / ecount
        sb_completion_score = 6. * sb_completion + 4.

        # set sb priority score

        if grade == 'A' and str(code).startswith('2013'):
            sb_grade_score = 10.
        elif str(code).startswith('2012'):
            sb_grade_score = 8.
        elif grade == 'B':
            sb_grade_score = 4.
        else:
            sb_grade_score = -100.

        # set science score
        sb_science_score = 10. * (self.max_scirank - srank) / self.max_scirank

        # set array score
        if array == '7m' or array == 'tp':
            sb_array_score = 10.
            arcorr_or = 0.
            lascorr = 0.
        else:
            c_bmax = 0.4001 / pd.np.cos(pd.np.radians(-23.0262015) -
                                        pd.np.radians(dec)) + 0.6103
            c_freq = repfreq / 100.
            corr = c_freq / c_bmax
            arcorr = ar * corr
            arcorr_or = arcorr
            lascorr = las * corr

            if name.endswith('_TC'):
                arcorr = 0.9 * amaxar
                arcorr_or = arcorr

            if arcorr > 3.73:
                arcorr = 3.73

            if aminar > self.array_ar and amaxar >= self.res6:
                array_ar = self.res6
            elif aminar > self.array_ar and amaxar < self.res6:
                array_ar = (self.res6 + self.array_ar) / 2.
            else:
                array_ar = self.array_ar

            if 0.9 * arcorr <= array_ar <= 1.1 * arcorr:
                sb_array_score = 10.

            elif 0.8 * arcorr < array_ar <= 1.2 * arcorr:
                sb_array_score = 8.0

            elif array_ar < 0.8 * arcorr:  # and not points:
                l = 0.8 * arcorr - aminar
                sb_array_score = ((array_ar - aminar) / l) * 8.0

            # elif self.array_ar < 0.8 * arcorr and points:
            #     sb_array_score = 8.0
            elif array_ar > 1.2 * arcorr:
                l = arcorr * 1.2 - amaxar
                s = 8. / l
                sb_array_score = (array_ar - amaxar) * s
            else:
                print("What happened with?")
                sb_array_score = -1.

            narray = 0.
            for a in confDf['ALMA_RB_03'].values:
                if aminar < a < amaxar:
                    narray += 1

            if narray == 0:
                print "Warning, no official configuration for %s" % name

            elif narray == 1 and sb_array_score < 8.5:
                sb_array_score = 9.

        # set exec score:
        sb_exec_score = self.exec_prio[execu]

        # set condition score:
        pwv_corr = 1 - (abs(self.pwv - maxpwvc) / 4.)
        if pwv_corr < 0.1:
            pwv_corr = 0.1

        if frac < 1:
            x = frac - 1.
            sb_cond_score = 10 * (1 - (x ** 10.)) * pwv_corr
        elif frac == 1:
            sb_cond_score = 10.
        else:
            x = frac - 1
            if frac <= 1.3:
                sb_cond_score = (1. - (x / 0.3) ** 3.) * 10. * pwv_corr
            else:
                sb_cond_score = 0.

        sb_ha_scorer = ((np.cos(np.radians((ha + 1) * 15.)) - 0.3)
                        /
                        (1 - 0.3)) * 10.

        score = (0.35 * sb_cond_score +
                 0.20 * sb_array_score +
                 0.10 * sb_completion_score +
                 0.05 * sb_exec_score +
                 0.05 * sb_science_score +
                 0.15 * sb_grade_score +
                 0.10 * sb_ha_scorer)
        return (sb_cond_score, sb_array_score, sb_completion_score,
                sb_ha_scorer, sb_exec_score, sb_science_score, sb_grade_score,
                arcorr_or, score, lascorr)

    def check_observability(self, array):

        """

        :param array:
        :return:
        """
        if self.date == self.old_date:
            return None
        alma1.date = self.date
        print(alma1.date)
        if array == '12m':
            fs_arr = self.fieldsource.query(
                'arraySB == "TWELVE-M" and isQuery == False')
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
            fs_arr[['fieldRef', 'SB_UID', 'isQuery', 'name', 'intendedUse']],
            df_fs, left_index=True, right_index=True,
            how='left')

        #  Libes 636-654 + donotuse query, workaround for multiple field sources
        donotuse = [
            'Pointing Template (Cal Group)',
            'Pointing Template (Science Group)', 'Amplitude', 'Phase',
            'Bandpass', 'J0423 Bandpass', 'J2258 2nd Bandpass',
            'Pointing', 'Check source', 'Phase calibrator', 'J1427-4206',
            'Bandpass calibrator', 'AmpAux_3', 'AmpAux_1', 'PhaseCal',
            'Calibrator: ', 'Polarization', 'AmpCheck1', 'AmpCheck2',
            'Polarization calibrator', 'Delay', 'Focus', 'Amplitude query',
            'calibrator_J1256', 'J192451-291428', 'J1911-2006', 'CheckSource',
            'Check', 'check', 'J0854+201', 'phase_and_checksource',
            'phase_and_checksource queries', 'phase+and_checksource',
            'Bandpass_3C279', 'Field Check source ', 'Phase 2', 'Phase 3',
            'Phase P', 'Bandpass (J1924-2914)', 'Pluto_May21-Jun01',
            'Pluto_Jun01-11', 'Pluto_Jun11-Jun21', 'Pluto_Jul01-11',
            'Pluto_Jul11-21', 'Pluto_Jul21-Aug01', 'Pluto_Aug01-11',
            'Pluto_Aug11-21', 'Pluto_Aug21-Sep01', 'Pluto_Sep01-11',
            'Pluto_Sep11-Sep21', 'Pluto_Sep21-Oct01']

        self.fs_1 = fs_1.query(
            'isQuery == False and name not in @donotuse').copy()
        fs_1g = fs_1.query(
            'isQuery == False and name not in @donotuse').groupby('SB_UID')
        allup = pd.DataFrame(
            fs_1g.observable.mean())
        allup.columns = pd.Index([u'up'])
        fs_2 = pd.merge(fs_1, allup, left_on='SB_UID', right_index=True,
                        how='left')
        fs_2g = fs_2.query(
            'isQuery == False and name not in @donotuse').groupby('SB_UID')
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

        ra = pd.DataFrame(
            fs_2g.RA.mean())
        ra.columns = pd.Index([u'RA'])

        fs_3 = pd.merge(allup, etime, right_index=True, left_index=True,
                        how='left')
        fs_4 = pd.merge(fs_3, elevation, right_index=True,
                        left_index=True, how='left')
        fs_5 = pd.merge(fs_4, lstr, right_index=True,
                        left_index=True, how='left')

        self.sb_summary.loc[dec.index, 'DEC'] = dec.loc[dec.index, 'DEC']
        self.sb_summary.loc[dec.index, 'RA'] = ra.loc[dec.index, 'RA']

        self.obser_prop = pd.merge(fs_5, lsts, right_index=True,
                                   left_index=True, how='left')
        self.old_date = self.date
        print(self.old_date, self.date)

    def set_trans(self, transmission):
        """

        :param transmission:
        """
        self.transmission = transmission

    def set_pwv(self, pwv):
        """

        :param pwv:
        """
        self.pwv = min(pwn, key=lambda x: abs(x - pwv))

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
        a = str("select se.SE_TIMESTAMP ts1, sa.SLOG_ATTR_VALUE av1, "
                "se.SE_ARRAYNAME, se.SE_ID se1 from ALMA.SHIFTLOG_ENTRIES se, "
                "ALMA.SLOG_ENTRY_ATTR sa "
                "WHERE se.SE_TYPE=7 and se.SE_TIMESTAMP > SYSDATE - 1/1. "
                "and sa.SLOG_SE_ID = se.SE_ID and sa.SLOG_ATTR_TYPE = 31 "
                "and se.SE_LOCATION='OSF-AOS' and se.SE_CORRELATORTYPE = 'BL'")
        try:
            self.cursor.execute(a)
            self.bl_arrays = pd.DataFrame(
                self.cursor.fetchall(),
                columns=[rec[0] for rec in self.cursor.description]
            ).sort('TS1', ascending=False)
        except ValueError:
            self.bl_arrays = pd.DataFrame(
                columns=pd.Index(
                    [u'TS1', u'AV1', u'SE_ARRAYNAME', u'SE1'], dtype='object'))
            print("No BL arrays have been created in the last 6 hours.")
        b = str("select se.SE_TIMESTAMP ts1, sa.SLOG_ATTR_VALUE av1, "
                "se.SE_ARRAYNAME, se.SE_ID se1 from ALMA.SHIFTLOG_ENTRIES se, "
                "ALMA.SLOG_ENTRY_ATTR sa "
                "WHERE se.SE_TYPE=7 and se.SE_TIMESTAMP > SYSDATE - 1/1. "
                "and sa.SLOG_SE_ID = se.SE_ID and sa.SLOG_ATTR_TYPE = 31 "
                "and se.SE_LOCATION='OSF-AOS' and se.SE_CORRELATORTYPE = 'ACA'")
        try:
            self.cursor.execute(b)
            self.aca_arrays = pd.DataFrame(
                self.cursor.fetchall(),
                columns=[rec[0] for rec in self.cursor.description]
            ).sort('TS1', ascending=False)
        except ValueError:
            self.aca_arrays = pd.DataFrame(
                columns=pd.Index(
                    [u'TS1', u'AV1', u'SE_ARRAYNAME', u'SE1'], dtype='object'))
            print("No ACA arrays have been created in the last 6 hours.")

    def set_bl_prop(self, array_name):

        """

        :param array_name:
        """
        # In case a bl_array is selected
        if (array_name is not None and len(self.bl_arrays) != 0
                and array_name not in self.defarrays):
            id1 = self.bl_arrays.query(
                'SE_ARRAYNAME == "%s"' % array_name).iloc[0].SE1

            # a = str("SELECT SLOG_ATTR_VALUE FROM ALMA.SLOG_ENTRY_ATTR "
            #        "WHERE SLOG_ATTR_TYPE = 31 "
            #        "AND SLOG_SE_ID=%d" % id1)
            # self.cursor.execute(a)
            # ap = pd.DataFrame(self.cursor.fetchall(), columns=['antenna'])

            ap = self.bl_arrays.query(
                'SE_ARRAYNAME == "%s" and SE1 == %d' % (array_name, id1)
            )[['AV1']]
            ap.rename(columns={'AV1': 'antenna'}, inplace=True)
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
                lines = io_file.readlines()
                self.array_ar = float(lines[13].split(':')[1])
                self.num_ant = int(lines[3].split(':')[1])
                print self.num_ant
                self.num_bl = self.num_ant * (self.num_ant - 1.) / 2.
                io_file.close()
                ac = rUV.ac.ArrayConfigurationCasaFile()
                ac.createCasaConfig(conf_file)
                self.ruv = rUV.computeRuv(conf_file + ".cfg")

            else:
                conf_file = self.wto_path + 'conf/%s.txt.cfg' % array_name
                self.ruv = rUV.computeRuv(conf_file)
                # noinspection PyTypeChecker
                self.array_ar = self.arr_ar_def[array_name]
                self.num_bl = self.num_ant * (self.num_ant - 1.) / 2.
                self.num_ant = 34

            # if len(self.ruv) > 33. * 17.:
            #    self.ruv = self.ruv[-561:]
            #    self.num_bl = len(self.ruv)
            #    self.num_ant = 34


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
        ra = 0
        dec = 0
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
            try:
                ra, dec, ephe = read_ephemeris(ephemeris, alma.date)
            except TypeError:
                #print(ephemeris, sourcename)
                ephe = False
            if not ephe:
                alma.date = dtemp
                print("Source %s doesn't have ephemeris for current's date" %
                      sourcename)
                return 0, 0, 0, 0, 0, 0, 0, 0, False
            obj = ephem.FixedBody()
            obj._ra = pd.np.deg2rad(ra)
            obj._dec = pd.np.deg2rad(dec)
            obj.compute(alma)
            ra = obj.ra
            dec = obj.dec
            elev = obj.alt
            neverup = obj.neverup
            print sourcename, ra, dec, elev

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
    return pd.np.degrees(ra), pd.np.degrees(dec), pd.np.degrees(elev),\
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
        elif line.startswith('$$EOE') or line.startswith(' $$EOE'):
            if not found:
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
                ra_temp = data[23:36].strip()
                dec_temp = data[37:50].strip()
                if len(ra_temp.split()) > 3:
                    ra_temp = data[23:34].strip()
                    dec_temp = data[35:46].strip()
                ra = ephem.hours(ra_temp.replace(' ', ':'))
                dec = ephem.degrees(dec_temp.replace(' ', ':'))
                ephe = True
                print(ra, dec, ephe, now)
                return pd.np.degrees(ra), pd.np.degrees(dec), ephe


def ret_cycle(code, blfrac):
    if code[:4] == '2012':
        return blfrac * (31. * 16.) / (33. * 17)
    else:
        return blfrac * 1.
