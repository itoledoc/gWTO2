__author__ = 'itoledo'

import pandas as pd
import ephem as eph
from wtoDatabase import WtoDatabase


class WtoAlgorithm(WtoDatabase):
    """


    """
    def __init__(self):
        """


        """
        super(WtoAlgorithm, self).__init__()
        self.pwv = 1.2
        self.date = eph.now()
        self.array_ar = 1.0
        self.pwvdata = pd.read_pickle(
            self.wto_path + 'conf/' + self.preferences.pwv_data).set_index(
                'freq')
        self.pwvdata.index = pd.Float64Index(
            pd.np.round(self.pwvdata.index, decimals=1), dtype='float64')

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

        # merge targets with fieldsources

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