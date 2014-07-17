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


class WtoAllsb(WtoDatabase):
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

        super(WtoAllsb, self).__init__(path, source, forcenew)