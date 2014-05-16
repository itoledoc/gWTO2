#!/usr/bin/env python
__author__ = 'ignacio'

import numpy as np
import ephem as eph
from optparse import OptionParser
from xmlrpclib import ServerProxy

s = ServerProxy('http://asa.alma.cl/sourcecat/xmlrpc')
catalogues = [c['catalogue_id'] for c in s.sourcecat.listCatalogues()]
types = [t['type_id'] for t in s.sourcecat.listTypes()]


BEAM_CONSTANT = 1.22 * 2.99792 * 1e8 * 3600.0 * 180.0 / np.pi
MOONS = ['Titan', 'Callisto', 'Ganymede', 'Europa', 'Io']
PLANETS = ['Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']
ASTEROIDS = ['Ceres', 'Pallas', 'Juno', 'Vesta']
QSO = [
    'J0132-169',
    'J2056-472',
    'J1130-148',
    'J2232+117',
    'J1800+388',
    'J1427-421',
    'J0237+288',
    'J0519-454',
    'J1107-448',
    'J2148+069',
    'J1159+292',
    'J1058+015',
    'J0510+180',
    'J1733-130',
    '3C345',
    'J1550+054',
    'J1037-295',
    'J2025+337',
    'J0334-401',
    'J0238+166',
    'J1751+096',
    'J1517-243',
    'J2202+422',
    'J2357-5311',
    'J2157-694',
    'J1924-292',
    'J2258-279',
    '3c84',
    'J1146+399',
    'J1337-129',
    '3C279',
    'J1613-586',
    '3C454.3',
    'J1426+364',
    'J0927+390',
    '3C273',
    'J0423-013',
    'J0106-405',
    'J0635-7516',
    'J1147-6753',
    'J0538-440',
    'J0522-364',
    'J0750+125',
    'J0854+201'
]

ra = {
    'J0106-405': '1:06:45.107976',
    'J0132-169': '1:32:43.487472',
    'J0237+288': '2:37:52.40568',
    'J0238+166': '2:38:38.93',
    '3c84': '3:19:48.16',
    'J0334-401': '3:34:13.654488',
    'J0423-013': '4:23:15.800736',
    'J0510+180': '5:10:02.369136',
    'J0519-454': '5:19:49.723',
    'J0635-7516': '6:35:46.5072',
    'J0750+125' : '7:50:52.045728',
    'J0854+201' : '8:54:48.87',
    'J0927+390': '9:27:03.013944',
    'J1037-295': '10:37:16.079736',
    'J1058+015': '10:58:29.605209',
    'J1107-448': '11:07:08.694144',
    'J1130-148': '11:30:07.052592',
    'J1146+399': '11:46:58.29792',
    'J1147-6753': '11:47:33.400031',
    'J1159+292': '11:59:31.833912',
    '3C273': '12:29:06.69972',
    '3C279': '12:56:11.16656',
    'J1337-129': '13:37:39.782784',
    'J1426+364': '14:26:37.087488',
    'J1427-421': '14:27:56.297568',
    'J1517-243': '15:17:41.813132',
    'J1550+054': '15:50:35.269248',
    'J1613-586': '16:17:17.892',
    '3C345': '16:42:58.80996',
    'J1733-130': '17:33:02.70579000001',
    'J1751+096': '17:51:32.818573',
    'J1800+388': '18:00:24.76536',
    'J1924-292': '19:24:51.055944',
    'J2025+337': '20:25:10.842096',
    'J2056-472': '20:56:16.359816',
    'J2148+069': '21:48:05.458679',
    'J2157-694': '21:57:05.98056000001',
    'J2202+422': '22:02:43.29',
    'J2232+117': '22:32:36.4099999999',
    '3C454.3': '22:53:57.747936',
    'J2258-279': '22:58:05.95999999991',
    'J2357-5311': '23:57:53.266',
    'J0538-440' : '5:38:50.361552',
    'J0522-364' : '5:22:57.985'
}

dec = {
    'J0106-405': '-40:34:19.96032',
    'J0132-169': '-16:54:48.52188',
    'J0237+288': '28:48:08.98992',
    'J0238+166': '16:36:59.275',
    '3c84': '41:30:42.0999999998',
    'J0334-401': '-40:8:25.39788',
    'J0423-013': '-1:20:33.06552',
    'J0510+180': '18:0:41.5818',
    'J0519-454': '-45:46:43.853',
    'J0750+125' : '12:31:04.82',
    'J0854+201' : '20:06:30.64',
    'J0635-7516': '-75:16:16.824',
    'J0927+390': '39:2:20.8518',
    'J1037-295': '-29:34:2.81316',
    'J1058+015': '1:33:58.82372',
    'J1107-448': '-44:49:7.61844000001',
    'J1130-148': '-14:49:27.3882',
    'J1146+399': '39:58:34.30452',
    'J1147-6753': '-67:53:41.76564',
    'J1159+292': '29:14:43.827',
    '3C273': '02:03:08.59824',
    '3C279': '-5:47:21.52458',
    'J1337-129': '-12:57:24.69312',
    'J1426+364': '36:25:09.57359999999',
    'J1427-421': '-42:06:19.43748',
    'J1517-243': '-24:22:19.47594',
    'J1550+054': '5:27:10.44828',
    'J1613-586': '-58:48:07.85499999999',
    '3C345': '39:48:36.99396',
    'J1733-130': '-13:04:49.54823',
    'J1751+096': '9:39:00.72851',
    'J1800+388': '38:48:30.69756',
    'J1924-292': '-29:14:30.12108',
    'J2025+337': '33:43:00.214319999988',
    'J2056-472': '-47:14:47.62752',
    'J2148+069': '6:57:38.60422',
    'J2157-694': '-69:41:23.68572',
    'J2202+422': '42:16:39.9799999999',
    'J2232+117': '11:43:50.9000000002',
    '3C454.3': '16:8:53.56104',
    'J2258-279': '-27:58:21.2599999999',
    'J2357-5311': '-53:11:13.69',
    'J0538-440' : '-44:5:8.93904',
    'J0522-364' : '-36:27:30.851'
}

# Add orbital elements for asteroids. The data base comes from
# http://cdsarc.u-strasbg.fr/ftp/cats/B/astorb/astorb.dat.gz
# and is the May 2013 release
# The perl script astorb2edb.pl (included in xephem) is used to convert
# the file into the pyepehm fortmat. Example:
#
# grep Ceres astorb.dat > myasteroids
# ./astorb2edb.pl < myasteroids

eph.Ceres = eph.readdb("Ceres,e,10.593979,80.327633,72.292128,2.76680728,"
                       "0,0.07579733,10.557582,11/4/2013,2000.0,3.34,0.12")
eph.Pallas = eph.readdb("Pallas,e,34.836245,173.102354,309.933755,2.77243389,"
                        "0,0.2315651,352.778998,11/4/2013,2000.0,4.13,0.11")
eph.Juno = eph.readdb("Juno,e,12.980573,169.877848,248.349895,2.67030537,"
                      "0,0.255287,302.768187,11/4/2013,2000.0,5.33,0.32")
eph.Vesta = eph.readdb("Vesta,e,7.140518,103.851567,151.199439,2.36138405,"
                       "0,0.08850238,272.215309,11/4/2013,2000.0,3.2,0.32")

ALMA = eph.Observer()
#noinspection PyPropertyAccess
ALMA.lat = '-23.0262015'
#noinspection PyPropertyAccess
ALMA.long = '-67.7551257'
ALMA.elev = 5060


#noinspection PyPropertyAccess
class Target(object):
    def __init__(self, name, ra, dec, epoch, site, date):
        """
        Class with data for sources with fixed coordinates. Also provides the
        function to calcuate positions.
        @param name:
        @param ra: sexagesimal notation, in hours
        @param dec: sexagesimal notation, in degrees
        @param epoch:
        @param site: is the alma ephem.Observer() object
        @param date: UTC time, ephem.Date() type
        """
        self.obj = eph.FixedBody()
        self.obj._ra = ra
        self.obj._dec = dec
        self.obj._epoch = epoch
        self.name = name
        self.site = site
        self.site.date = date
        self.ptype = [('time', 'a19'), ('az', 'f4'), ('alt', 'f4'),
                      ('sidereal', 'a15')]
        self.data = np.zeros(0, dtype=self.ptype)

    def calc_positions(self):
        """
        Calculates ephemerides for the Target with the observer conditions at
        the AOS
        """
        self.obj.compute(self.site)
        tdata = np.array([(self.site.date.datetime(), np.degrees(self.obj.az),
                           np.degrees(self.obj.alt),
                           self.site.sidereal_time())],
                         dtype=self.ptype)
        self.data = np.concatenate((self.data, tdata))

    def create_data(self):
        """
        Data structure which is a numpy Structured array, defined by ptype. It
        is filled with calculations performed every 5 minutes for 24 hours,
        starting at DATE
        """
        initDate = eph.Date(self.site.date)
        self.calc_positions()
        self.circumpolar = self.obj.circumpolar
        while self.site.date - initDate <= 23.7 * eph.hour:
            self.site.date += 5 * eph.minute
            self.calc_positions()
        self.site.date = initDate
        self.obj.compute(self.site)


class MinorPlanet(Target):
    #noinspection PyMissingConstructor
    def __init__(self, name, site, date):
        """
        Class with data for Minor Planets. Difference with Target class is the
        hability to calculate RA and DEC coordinates acording to DATE
        @param name:
        @param site:
        @param date:
        """
        self.obj = eval('eph.' + name)
        self.site = site
        self.site.date = date
        self.name = name
        self.ptype = [('time', 'a19'), ('az', 'f4'), ('alt', 'f4'),
                      ('sidereal', 'a15')]
        self.data = np.zeros(0, dtype=self.ptype)


class Planet(Target):
    #noinspection PyMissingConstructor
    def __init__(self, name, site, date):
        """

        @param name:
        @param site:
        @param date:
        """
        self.obj = eval('eph.' + name + '()')
        self.site = site
        self.site.date = date
        self.name = name
        self.ptype = [('time', 'a19'), ('az', 'f4'), ('alt', 'f4'),
                      ('sidereal', 'a15')]
        self.data = np.zeros(0, dtype=self.ptype)


class Moon(Target):
    #noinspection PyMissingConstructor
    def __init__(self, name, site, date, freq):
        """
        Class with data for Moons. Similar to MinorPlanet class, but adds the
        fields separation and freq, to calculate separation to planet and
        observational limit based in the BeamWidth for a particular frequency
        @param name:
        @param site:
        @param date:
        @param freq:
        """

        self.obj = eval('eph.' + name + '()')
        self.obj.radius = eph.degrees('0.00001')
        self.obj.circumpolar = False
        self.site = site
        self.site.date = date
        self.name = name
        self.ptype = [('time', 'a19'), ('az', 'f4'), ('alt', 'f4'),
                      ('separation', 'f4'), ('sidereal', 'a15'), ('freq', 'f4')]
        self.freq = freq
        self.data = np.zeros(0, dtype=self.ptype)

    def calc_positions(self):
        """
        Calculates positions, replacing the Target.calc_position method, since
        we also need the separation for each time.
        @rtype : object
        """

        self.planet = (eph.Saturn() if 'Tita' in self.name else
                       eph.Jupiter())
        initDate = eph.Date(self.site.date)
        self.obj.compute(self.site)
        #noinspection PyUnresolvedReferences
        self.planet.compute(self.site)
        #noinspection PyUnresolvedReferences
        separation = 3600. * np.degrees(
            eph.separation([self.planet.ra, self.planet.dec],
                           [self.obj.ra, self.obj.dec]))  # in arcsec
        tdata = np.array([(self.site.date.datetime(), np.degrees(self.obj.az),
                           np.degrees(self.obj.alt), separation,
                           self.site.sidereal_time(), self.freq)],
                         dtype=self.ptype)
        self.data = np.concatenate((self.data, tdata))
        self.site.date = initDate
        self.obj.compute(self.site)


def freq_hpbw(freq):
    """
    Calculates Beam width in arcsec given a frequency in GHz
    @param freq:
    @return:
    """
    hpbw = BEAM_CONSTANT / (12. * freq * 1E9)
    return hpbw


def read_data(source, date=eph.now(), freq=91.):

    if source in ['Ceres', 'Pallas', 'Vesta', 'Juno']:
        data = MinorPlanet(source, ALMA, date)
        data.create_data()

    elif source in ['Ganymede', 'Europa', 'Callisto', 'Io', 'Titan']:
        data = Moon(source, ALMA, date, freq)
        data.create_data()

    elif source in ['Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune',
                    'Pluto']:
        data = Planet(source, ALMA, date)
        data.create_data()

    else:
        data = Target(source, ra[source], dec[source], '2000', ALMA, date)
        data.create_data()
    return data


def find_alt_time(sol, alt, date, alma):
    """
    Finds sun alt times, i.e., the two times in the day that the sun goes
    through a particular altitude.
    WARNING: this function for working with alma site parameters and different
    twilight altitudes. Using altitudes that the sun might not pass through
    could result in an endless loop.
    @param sol:
    @param alt:
    @param alma:
    @return:
    """

    alma.date = date
    alma.horizon = str(alt)
    try:
        dusk = alma.next_setting(sol)
        dawn = alma.next_rising(sol)
        init_cond = 'under'
        if dusk < dawn:
            init_cond = 'over'
        return init_cond, dusk, dawn
    except eph.NeverUpError:
        return 'neverup', 0, 0


def main():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)

    parser.add_option(
        "-d", dest="date", action='store',
        type='string', default=eph.now(),
        help="set starting date to DATE \'yyyy/mm/dd HH:MM\' UTC. "
             "Use of single quotes is mandatory when providing a time"
             " time. Default is current UTC time")
    parser.add_option(
        "-f", dest="freq", action="store",
        default=90.0, help="Frequency of observations for moon separation"
                           "calculations. Default = 90 (GHz)")
    parser.add_option(
        "-e", dest="elev", action="store",
        default=30.0, help="Elevation limit. Default = 30 (degrees)")

    parser.add_option("-q", dest="qso", action="store_true", default=False,
                      help='Display only QSO information')

    (options, args) = parser.parse_args()
    date = eph.date(options.date)
    freq = float(options.freq)
    elev = float(options.elev)
    ALMA.date = date

    if options.qso:
        print("\nQSOs                                                             ")
        print("-------------------------------------------------------------------"
              "-------------------------------------------------------------------"
              "---------")
        lis = ra.keys()
        lis.sort()
        doinfo(lis)
        print("-------------------------------------------------------------------"
              "-------------------------------------------------------------------"
              "---------")
        return 0

    print("*******************************************************************"
          "*******************************************************************"
          "*********")
    print("EPHEMERIS FOR %s (UTC):" % date)
    print("LST: %s" % ALMA.sidereal_time())
    print("(Rise and set calculations using an EL limit of %d deg.)" % elev)
    print("*******************************************************************"
          "*******************************************************************"
          "*********")
    print("PLANETS")
    print("-------------------------------------------------------------------"
          "-------------------------------------------------------------------"
          "---------")
    docalc(PLANETS, date, elev)

    print("\nMOONS                                                            ")
    print("-------------------------------------------------------------------"
          "-------------------------------------------------------------------"
          "---------")
    no = []
    for s in MOONS:
        data = read_data(s)
        alt = data.obj.alt
        cond, sets, rise = find_alt_time(data.obj, elev, date, ALMA)
        if cond == 'under':
            no.append(s)

        elif cond == 'neverup':
            no.append(s)

        else:
            hpbw = freq_hpbw(freq)
            if data.data[0]['separation'] < 2 * hpbw:
                print ("%s is at %5.2f deg, but to close to planet (assuming "
                       "freq %s GHz, distance %s)" % (s, np.rad2deg(alt), freq, data.data[0]['separation']))
                test = True
                tim = ''
                c = 1
                while test and (c < len(data.data['separation'])):
                    if ((data.data[c]['separation'] >= 2 * hpbw) and
                            (data.data[c]['alt'] > elev)):
                        test = False
                        tim = eph.Date(data.data[c]['time'])
                    c += 1
                if test:
                    print("                (It won't be available in the next "
                          "24 hrs)")
                else:
                    print("                (Available again at  %s)" % tim)
            else:

                test = True
                c = 1
                tim = sets
                while test and (c < len(data.data['separation'])):
                    if (data.data[c]['separation'] <= 2 * hpbw or
                            data.data[c]['alt'] < elev):
                        test = False
                        tim = eph.Date(data.data[c]['time'])
                    c += 1
                dif = str(eph.hours(str(24 * (tim - date))))[:-6]
                print("%-15s is currently at %5.2f deg. Available for the "
                      "next %s hours (%s)" % (s, np.rad2deg(alt), dif, sets))
    for s in no:
        data = read_data(s)
        cond, sets, rise = find_alt_time(data.obj, elev, date, ALMA)
        if cond == 'under':
            dif = str(eph.hours(str(24 * (rise - date))))[:-6]
            print ("%-15s Under %s deg. Rises in %5s hours"
                   " (%s)" % (s, elev, dif, rise))
        elif cond == 'neverup':
            print ("%-15s never goes over %s deg." % s)

    print("\nASTEROIDS                                                        ")
    print("-------------------------------------------------------------------"
          "-------------------------------------------------------------------"
          "---------")
    docalc(ASTEROIDS, date, elev)

    print("\nQSOs                                                             ")
    print("-------------------------------------------------------------------"
          "-------------------------------------------------------------------"
          "---------")
    docalc(QSO, date, elev)
    print("-------------------------------------------------------------------"
          "-------------------------------------------------------------------"
          "---------")


def doinfo(lista):
    for s in lista:
        data = read_data(s)
        if len(lista) > 0:
            m3 = wrapSearch(name=s, limit=2, fLower=84e9, fUpper=116e9)
            m7 = wrapSearch(name=s, limit=2, fLower=275e9, fUpper=373e9)
            fluxes = 'Latest Fluxes: '
            if len(m3) > 0:
                fluxes += 'Band 3: %.2fJy, ' % m3[0]['flux']
            if len(m7) > 0:
                fluxes += ', Band 7: %.2fJy.' % m7[0]['flux']
                # print m7[0]['frequency']*1e-9, m7[0]['flux'], \
                #     m7[0]['date_observed']
            else:
                fluxes += '.'
        else:
            fluxes = ''
        print ("%-15s RA=%11s DEC=%11s %s" % (s, data.obj.ra, data.obj.dec, fluxes))


def docalc(lista, date, elev):
    no = []
    listan = ''
    if lista == QSO:
        listan = 'QSO'
        lista = ra.keys()
        lista.sort()
    for s in lista:
        data = read_data(s)
        alt = data.obj.alt
        cond, sets, rise = find_alt_time(data.obj, elev, date, ALMA)
        if cond == 'under':
            no.append(s)

        elif cond == 'neverup':
            no.append(s)

        else:
            dif = str(eph.hours(str(24 * (sets - date))))[:-6]
            if listan == 'QSO':
                m3 = wrapSearch(name=s, limit=2, fLower=84e9, fUpper=116e9)
                m7 = wrapSearch(name=s, limit=2, fLower=275e9, fUpper=373e9)
                fluxes = 'Latest Fluxes: '
                if len(m3) > 0:
                    fluxes += 'Band 3: %.2fJy, ' % m3[0]['flux']
                if len(m7) > 0:
                    fluxes += ', Band 7: %.2fJy.' % m7[0]['flux']
                else:
                    fluxes += '.'
            else:
                fluxes = ''
            print ("%-15s Currently at %5.2f deg. Sets in %5s hours ("
                   "%s) %s" % (s, np.rad2deg(alt), dif, sets, fluxes))
    if listan != 'QSO':
        for s in no:
            data = read_data(s)
            cond, sets, rise = find_alt_time(data.obj, elev, date, ALMA)
            if cond == 'under':
                dif = str(eph.hours(str(24 * (rise - date))))[:-6]
                print ("%-15s Under %s deg. El. Rises in %5s hours ("
                       "%s)" % (s, elev, dif, rise))
            elif cond == 'neverup':
                print ("%-15s never goes over %s deg." % (s, elev))


def wrapSearch(s=s, limit=5, catalogues=catalogues, types=types, name='',
               ra=-1.0, dec=-1.0, radius=-1.0, ranges=None, fLower=-1.0,
               fUpper=-1.0, fluxMin=-1.0, fluxMax=-1.0, degreeMin=-1.0,
               degreeMax=-1.0, angleMin=-361.0, angleMax=-361.0,
               sortBy='date_observed', asc=False, searchOnDate=False,
               dateCriteria=0, date=''):
        """
        This is the basic search. It is a wrapper around the  catalog's
        searching function
        """
        if not ranges:
            ranges = []
        try:
            measurements = s.sourcecat.searchMeasurements(
                limit, catalogues, types, name, ra, dec, radius, ranges,
                fLower, fUpper, fluxMin, fluxMax, degreeMin, degreeMax,
                angleMin, angleMax, sortBy, asc, searchOnDate, dateCriteria,
                date)

            checkForPseudoNullsInMeasurement(measurements)

            return measurements
        except Exception, ex:
            print("Exception caught: %s" % ex)
            return []


def checkForPseudoNullsInMeasurement(measurements):
    for m in measurements:
        m['ra_uncertainty'] = convertPseudoNullToNone(
            m['ra_uncertainty'])
        m['dec_uncertainty'] = convertPseudoNullToNone(
            m['dec_uncertainty'])
        m['flux_uncertainty'] = convertPseudoNullToNone(
            m['flux_uncertainty'])
        m['degree'] = convertPseudoNullToNone(m['degree'])
        m['degree_uncertainty'] = convertPseudoNullToNone(
            m['degree_uncertainty'])
        m['angle'] = convertPseudoNullToNone(m['angle'])
        m['angle_uncertainty'] = convertPseudoNullToNone(
            m['angle_uncertainty'])
        m['extension'] = convertPseudoNullToNone(m['extension'])
        m['origin'] = convertPseudoNullToNone(m['origin'])
    return measurements


def convertPseudoNullToNone(value):
    # Either XmlRpc or Java formats the value like this and returns it as a
    # String
    NULL_AS_FLOAT_STRING = '1.7976931348623157E308'
    NULL_AS_STRING = 'null'
    if ((value == NULL_AS_STRING) or (value == '') or
            (value == NULL_AS_FLOAT_STRING)):
        return None
    return value


if __name__ == '__main__':
    main()
