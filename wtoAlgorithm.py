__author__ = 'itoledo'

import pandas as pd
import ephem
from wtoDatabase import WtoDatabase

SSO = ['Moon', 'Sun', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn',
       'Uranus', 'Neptune', 'Pluto']
MOON = ['Ganymede', 'Europa', 'Callisto', 'Io', 'Titan']

alma = ephem.Observer()
alma.lat = '-23.0262015'
alma.long = '-67.7551257'
alma.elev = 5060

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
        self.array_ar = 0.94
        self.transmission = 0.7
        self.minha = -5.0
        self.maxha = 3.0
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
        self.alma = alma
        self.reciever = pd.DataFrame(
            [55., 45., 75., 110., 51., 150.],
            columns=['trx'],
            index=['ALMA_RB_06', 'ALMA_RB_03', 'ALMA_RB_07', 'ALMA_RB_09',
                   'ALMA_RB_04', 'ALMA_RB_08'])
        self.reciever['g'] = [0., 0., 0., 1., 0., 0.]

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
        sum2['airmass'] = 1/pd.np.cos(pd.np.radians(-23.0262015 - sum2.DEC))
        sum2 = pd.merge(sum2, self.reciever, left_on='band', right_index=True,
                        how='left')
        tskycol = self.tsky[[str(self.pwv)]]
        sum2 = pd.merge(sum2, tskycol, left_on='repfreq', right_index=True)
        taucol = self.tau[[str(self.pwv)]]
        sum2 = sum2.rename(
            columns={str(self.pwv): 'tsky'})
        sum2 = pd.merge(sum2, taucol,  left_on='repfreq', right_index=True)
        sum2 = sum2.rename(
            columns={str(self.pwv): 'tau'})
        print("SBs in sb_summary: %d. SBs merged with tau/tsky info: %d." %
              (len(self.sb_summary), len(sum2)))
        sum2['tsys'] = (
            1 + sum2['g']) * \
            (sum2['trx'] + sum2['tsky'] *
             ((1 - pd.np.exp(-1*sum2['airmass']*sum2['tau'])) /
              (1 - pd.np.exp(-1. * sum2['tau']))) * 0.95 + 0.05 * 270.) / \
            (0.95 * pd.np.exp(-1 * sum2['tau'] * sum2['airmass']))
        sum2['tsys_org'] = (
            1 + sum2['g']) * \
            (sum2['trx'] + sum2['tsky_org'] *
             ((1 - pd.np.exp(-1*sum2['airmass']*sum2['tau_org'])) /
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
        ha = (lst - sel2.RA) / 15.
        ha.loc[ha > 12] = 24. - ha.loc[ha > 12]
        ha.loc[ha < -12] = 24. + ha.loc[ha < -12]
        sel2['HA'] = ha
        sel2 = sel2
        sel3 = sel2[((sel2.HA > self.minha) & (sel2.HA < self.maxha)) |
                    (sel2.RA == 0.)]
        sel3['frac'] = (sel3.tsys_org / sel3.tsys) ** 2.
        print("SBs within current HA limits (or RA=0): %d" % len(sel3))
        if array == '12m':
            sel3 = sel3.query(
                '((arrayMinAR+arrayMaxAR/1.44)/2. < %f and %f < arrayMaxAR)'
                ' and (band != "ALMA_RB_04" and band != "ALMA_RB_08") '
                'and SB_state != "Phase2Submitted" and array=="TWELVE-M"' %
                (self.array_ar, self.array_ar))
            print("SBs for current 12m Array AR: %d." % len(sel3))
            self.select12m = sel3
            special = self.select12m.query(
                'PRJ_state != "Completed" and SB_state != "FullyObserved"')
            special = special[
                special.name.str.contains('not', case=False) == False]
            special = special[special.isPolarization == False]
            special[['SB_UID', 'name']].to_csv(
                self.path + 'special.sbinfo', header=False, index=False,
                sep=' ')
        elif array == '7m':
            self.select7m = sel3
        else:
            self.selecttp = sel3
        pass

    def observable(self, data, date):
        pass

    def scorer(self, data, trans, array, array_ar):
        pass

    def set_trans(self, transmission):
        self.transmission = transmission

    def set_pwv(self, pwv):
        self.pwv = pwv

    def set_date(self, date):
        self.date = date

    def set_arrayar(self, ar):
        self.array_ar = ar

    def set_minha(self, ha):
        self.minha = ha

    def set_maxha(self, ha):
        self.maxha = ha

    def set_array_ar(self, ar):
        self.array_ar = ar