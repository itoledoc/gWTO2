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
    def __init__(self):
        """


        """
        super(WtoAlgorithm, self).__init__()
        self.pwv = 1.2
        self.date = ephem.now()
        self.array_ar = 1.0
        self.transmission = 0.7
        self.minha = -5.0
        self.maxha = 3.0
        self.pwvdata = pd.read_pickle(
            self.wto_path + 'conf/' + self.preferences.pwv_data).set_index(
                'freq')
        self.pwvdata.index = pd.Float64Index(
            pd.np.round(self.pwvdata.index, decimals=1), dtype='float64')
        self.alma = alma

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
        s_pwv = pd.merge(
            self.sb_summary, pwvcol, left_on='repfreq', right_index=True)
        s_pwv['airmass'] = 1/pd.np.cos(pd.np.radians(-23.0262015 - s_pwv.DEC))
        print("SBs in sb_summary: %d. SBs with a calculated transmission: %d." %
              (len(self.sb_summary), len(s_pwv)))

        s_pwv = s_pwv.rename(
            columns={str(self.pwv): 'transmission'})
        sel1 = s_pwv[s_pwv.transmission > self.transmission]
        print("SBs with a transmission higher than %2.1f: %d" %
              (self.transmission, len(sel1)))

        if array == '7m':
            sel2 = sel1[
                (sel1.array == array1[0]) or
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
        self.sel3 = sel2[((sel2.HA > self.minha) & (sel2.HA < self.maxha)) |
                         (sel2.RA == 0.)]
        print("SBs within current HA limits (or RA=0): %d" % len(self.sel3))

        pass

    def observable(self, data, date):
        pass

    def scorer(self, data, trans, array, array_ar):
        pass

    def transmission(self, freq, pwv):
        pass

    def set_trans(self, transmission):
        self.trans = transmission

    def set_pwv(self, pwv):
        self.pwv = pwv

    def set_date(self, date):
        self.date = date

    def set_arrayar(self, ar):
        self.array_ar = ar