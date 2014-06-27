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
    def selector(self, array, array_name=None):

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

        if array not in ['12m', '7m', 'tp']:
            print("Use 12m, 7m or tp for array selection.")
            return None
        else:
            if array == '12m':
                array1 = ['TWELVE-M']
                if array_name is not None:
                    self.set_bl_prop(array_name=array_name)
                    self.array_ar = 61800 / (100.0 * self.ruv.max())
                else:
                    self.set_bl_prop(array_name=None)
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
        sel3['tsysfrac'] = (sel3.tsys / sel3.tsys_org) ** 2.
        print("SBs within current HA limits (or RA=0): %d" % len(sel3))
        if array == '12m':
            sel3 = sel3.query(
                '((arrayMinAR+arrayMaxAR/1.44)/2. < %f and %f < arrayMaxAR)'
                ' and (band != "ALMA_RB_04" and band != "ALMA_RB_08") '
                'and SB_state != "Phase2Submitted" and array=="TWELVE-M"' %
                (self.array_ar, self.array_ar))
            print("SBs for current 12m Array AR: %d. "
                  "(AR=%.2f, #bl=%d, #ant=%d)" %
                  (len(sel3), self.array_ar, self.num_bl, self.num_ant))
            sel3['blmax'] = sel3.apply(
                lambda row: rUV.computeBL(row['AR'], row['repfreq']), axis=1)
            sel3['blfrac'] = sel3.apply(
                lambda row: (33. * 17) / (1.*len(
                    self.ruv[self.ruv < row['blmax']]))
                if (row['LAS'] != 0) else (33. * 17) / self.num_ant, axis=1)
            sel3['frac'] = sel3.tsysfrac * sel3.blfrac
            self.select12m = sel3
            special = self.select12m.query(
                'PRJ_state != "Completed" and SB_state != "FullyObserved"'
                ' and SB_state != "Deleted" and isTimeConstrained == False')
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

        # TODO: merge sb_summary with target left on SB_UID, science, right on
        #       SB_UID, paramRef (t1)
        # TODO: merge t1 with fieldsource on fieldRef (and SB_UID) (t2)
        # TODO: group t2 by SB_UID and calculate mean RA_y and DEC_y
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

    def query_arrays(self):
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
        if array_name is not None and len(self.bl_arrays) != 0:
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
        else:
            conf_file = self.wto_path + 'conf/default.txt'
            io_file = open(self.wto_path + 'conf/arrayConfigurationResults.txt')
            self.array_ar = float(io_file.readlines()[13].split(':')[1])
            ac = rUV.ac.ArrayConfigurationCasaFile()
            ac.createCasaConfig(conf_file)
            self.ruv = rUV.computeRuv(conf_file + ".cfg")
            if len(self.ruv) > 33. * 17.:
                self.ruv = self.ruv[-561:]
                self.num_bl = len(self.ruv)
                self.num_ant = 34.
            else:
                self.num_bl = len(self.ruv)
                self.num_ant = int((1 + pd.np.sqrt(1 + 8 * self.num_bl)) / 2.)


def observable(solarSystem, sourcename, RA, DEC, horizon, isQuery, ephemeris,
               alma=alma1):
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
    return str(ra), str(dec), pd.np.degrees(elev), remaining.total_seconds() / 3600., rise, sets, lstr,\
        lsts, obs


def read_ephemeris(ephemeris, date):

    in_data = False
    now = date
    month_ints = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
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
                c1 += 1
            else:
                if c1 == 0:
                    #print("NO EPHEMERIS FOR CURRENT DATE. Setting RA=0,"
                    #      " DEC=0")
                    ra = ephem.hours('00:00:00')
                    dec = ephem.degrees('00:00:00')
                    ephe = False
                    return ra, dec, ephe
                ra = ephem.hours(data[23:34].strip().replace(' ', ':'))
                dec = ephem.degrees(data[35:46].strip().replace(' ', ':'))
                ephe = True
                return ra, dec, ephe

"""
To fit the ruv distribution
from scipy.stats import norm,rayleigh

samp = rayleigh.rvs(loc=5,scale=2,size=150) # samples generation

param = rayleigh.fit(samp) # distribution fitting

x = linspace(5,13,100)
# fitted distribution
pdf_fitted = rayleigh.pdf(x,loc=param[0],scale=param[1])
# original distribution
pdf = rayleigh.pdf(x,loc=5,scale=2)

title('Rayleigh distribution')
plot(x,pdf_fitted,'r-',x,pdf,'b-')
hist(samp,normed=1,alpha=.3)
show()
"""