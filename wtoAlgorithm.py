__author__ = 'itoledo'

import pandas as pd
import ephem as eph
from wtoDatabase import WtoDatabase


class WtoAlgorithm(WtoDatabase):

    def __init__(self):
        super(WtoAlgorithm, self).__init__()
        self.pwv = 1.2
        self.date = eph.now()

    def selector(self, data, array):

        """

        :param data:
        :param array:
        """
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