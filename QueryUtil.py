__author__ = 'ignacio'

import os
import cx_Oracle
import ephem as eph
import math
from datetime import datetime, timedelta
import numpy as np

# Add orbital elements for asteroids. The data base comes from
# http://cdsarc.u-strasbg.fr/ftp/cats/B/astorb/astorb.dat.gz
# and is the November 4th, 2013 release
# The perl script astorb2edb.pl (included in xephem) is used to convert
# the file into the pyepehm fortmat. Example:
#
# grep Ceres astorb.dat > myasteroids
# ./astorb2edb.pl < myasteroids

BEAM_CONSTANT = 1.22 * 2.99792 * 1e8 * 3600.0 * 180.0 / np.pi

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
ALMA.lat = '-23.019283'
#noinspection PyPropertyAccess
ALMA.long = '-67.753178'
ALMA.elev = 5060


# h.catalogue[h.catalogue['date_observed'] > np.datetime64(datetime.datetime(2011, 5, 1, 0, 0))]['date_observed'][0]
class CalibratorCatalog(object):
    def __init__(self, date=datetime.utcnow(), alma=ALMA):
        """
        CalibratorCatalog constructor.

        @src : dictionary with details of the source to be queried
               {'source': querySource.tag,
                'fieldSource': cal,
                'intent': queryIntended,
                'queryCenterLong': queryCenterLongVal,
                'queryCenterLat': queryCenterLatVal,
                'searchRadius': searchRadius,
                'minFrequency': minFreq,
                'maxFrequency': maxFreq,
                'minFlux': minFlux,
                'maxFlux': maxFlux,
                'maxSources': maxSources,
                'bandwidths': BW,
                'frequencies': freqList,
                'channels': channels,
                'isquery': True}
        @date : date in utc as a datetime object
        @default : use default query restrains. Set to False if intend to use SB
                   limits
        """
        self.sctype = [
            ('m_id', np.int32), ('cat_id', np.int32), ('source_id', np.int32),
            ('ra', np.float32), ('dec', np.float32), ('frequency', np.float32),
            ('flux', np.float32), ('flux_error', np.float32), ('flux_w', np.float32),
            ('date_observed', 'datetime64[s]'), ('radius', np.float32), ('nobs', 'i4')]
        self.max_sep_phase = 15.0  # Degrees
        self.max_sep_bpass = 45.0  # Degrees
        self.min_radius = 3.0  # Degrees
        self.max_separation = 15.0  # Deegres for phase calibrators
        self.signal_to_noise = 15.  # Signal to noise of 15 for phase calibrators
        self.max_integration = 30.  # Time in seconds
        self.min_integration = 10.  # Time in seconds
        self.min_el_ampcal = 40.  # In degrees
        self.min_el_phasecal = 20.0  # In degrees
        self.min_bandpass_el = 56.0  # In degrees
        self.phasecal_time = 1800.0  # In seconds

        self.infile = 'Temp_Calibrator_catalog.txt'
        self.sensitivities = [
            '84.', '0.10', '88.', '0.09', '100.', '0.10', '108.', '0.10',
            '112.', '0.12', '114.', '0.14', '116.', '0.24', '211.', '0.14',
            '231.', '0.15', '251.', '0.16', '275.', '0.17', '280.', '0.19',
            '300.', '0.21', '310.', '0.23', '320.', '0.48', '325.', '16.57',
            '330.', '0.40', '340.', '0.27', '350.', '0.29', '360.', '0.36',
            '367.', '0.71', '372.', '1.19', '602.', '8.02', '612.', '5.80',
            '620.', '99.99', '624.', '13.79', '634.', '3.29', '644.', '2.69',
            '654.', '2.91', '664.', '2.43', '674.', '2.70', '684.', '2.78',
            '694.', '3.31', '700.', '3.71', '710.', '5.56', '716.', '63.0 ',
            '720.', '12.01']

        self.grid_names = [
            'J0237+288', 'J0238+166', '3c84', 'J0334-401', 'J0423-013',
            'J0510+180', 'J0519-454', 'J0522-364', 'J0538-440', 'J0635-7516',
            'J0750+125', 'J0854+201', 'J1037-295', 'J1058+015', 'J1107-448',
            'J1146+399', '3c273', '3c279', 'J1337-129', 'J1427-421',
            'J1517-243', 'J1550+054', 'J1613-586', '3c345', 'J1733-130',
            'J1751+096', 'J1924-292', 'J2025+337', 'J2056-472', 'J2148+069',
            'J2232+117', 'J2258-279', 'J2357-5311']

        self.grid_dict = {
            '3c273': 5467, '3c279': 5683, '3c345': 7342, '3c84': 1626,
            'J0237+288': 1306, 'J0238+166': 1311, 'J0334-401': 1754,
            'J0423-013': 2117, 'J0510+180': 2499, 'J0519-454': 2570,
            'J0522-364': 2598, 'J0538-440': 2713, 'J0635-7516': 3088,
            'J0750+125': 3501, 'J0854+201': 3916, 'J1037-295': 4625,
            'J1058+015': 4770, 'J1107-448': 4832, 'J1146+399': 5137,
            'J1337-129': 6016, 'J1427-421': 6406, 'J1517-243': 6774,
            'J1550+054': 6996, 'J1613-586': 7169, 'J1733-130': 7671,
            'J1751+096': 7795, 'J1924-292': 8331, 'J2025+337': 8725,
            'J2056-472': 8943, 'J2148+069': 9343, 'J2232+117': 9706,
            'J2258-279': 9895, 'J2357-5311': 10341}

        self.sso_names = ['Mars', 'Venus', 'Jupiter', 'Uranus', 'Neptune',
                          'Titan', 'Ceres', 'Ganymede', 'Callisto', 'Pallas']
        self.date = date
        self.ALMA = alma
        self.ALMA.date = self.date
        self.catalogue = np.zeros(0, dtype=self.sctype)
        self.names = np.zeros(0, dtype=self.sctype)
        self.populate_catalogue()

    def populate_catalogue(self):

        sntype = [
            ('source_id', np.int32), ('name_id', np.int32),
            ('source_name', np.str_, 30)]
        self.names = np.zeros(0, dtype=sntype)

        try:
            last = datetime.fromtimestamp(os.path.getmtime('catalogue.npy'))
            now = datetime.now()
            delta = timedelta(1)
            old = now - delta
            outdated = last < old
        except OSError:
            outdated = True

        if not outdated:
            print "Using catalogue backup"
            cat = np.load('catalogue.npy')
            for r in cat:
                row = np.array([tuple(r.tolist())], dtype=self.sctype)
                self.catalogue = np.concatenate([self.catalogue, row])
            cat2 = np.load('names.npy')
            for r2 in cat2:
                row = np.array([tuple(r2.tolist())], dtype=sntype)
                self.names = np.concatenate([self.names, row])

        else:
            conx_string = 'SRCCAT_RO/ssrtest@ALMA_ONLINE.OSF.CL'
            connection = cx_Oracle.connect(conx_string)
            #dns_tns = cx_Oracle.makedsn('oraosf.osf.alma.cl', 1521, 'ALMA1')
            #connection = cx_Oracle.connect('almasu', 'alma4dba', dns_tns)
            cursor = connection.cursor()

            cursor.execute(
                "SELECT measurement_id, catalogue_id, source_id, ra, dec, "
                "frequency, flux, flux_uncertainty, 5., date_observed, 0., 0. "
                "FROM SOURCECATALOGUE.measurements")
            query = cursor.fetchall()
            for r in query:
                row = np.array([r], dtype=self.sctype)
                print row
                self.catalogue = np.concatenate([self.catalogue, row])
            np.save('catalogue', query)

            cursor.execute(
                "SELECT sn.source_id, nm.name_id, nm.source_name "
                "FROM SOURCECATALOGUE.source_name sn, SOURCECATALOGUE.names nm "
                "WHERE nm.name_id = sn.name_id")
            query2 = cursor.fetchall()
            for r in query2:
                row = np.array([r], dtype=sntype)
                self.names = np.concatenate([self.names, row])
            np.save('names', query2)
            cursor.close()
            connection.close()

    def setdate(self, date):
        self.date = date
        self.ALMA.date = self.date

    def query(self, ra=0., dec=0., min_flux=0., max_flux=1e13,
              min_freq=0., max_freq=1e15, radius=3., exp_freq=90.e9, tdy=2,
              tdd=0, grid=False):

        query = np.zeros(0, dtype=self.sctype)
        catalogue = np.copy(self.catalogue)
        qrsrc = eph.FixedBody()
        qrsrc._ra = np.deg2rad(ra)
        qrsrc._dec = np.deg2rad(dec)
        qrsrc.compute(self.ALMA)
        delta = timedelta(days=365 * tdy + tdd)
        sel1 = catalogue[
            (catalogue['frequency'] >= min_freq) &
            (catalogue['frequency'] <= max_freq) &
            (catalogue['flux'] >= min_flux) &
            (catalogue['flux'] <= max_flux) &
            (catalogue['date_observed'] >= self.date - delta)]
        for ids in np.unique(sel1['source_id']):
            if grid:
                if ids not in self.grid_dict.values():
                    continue
            sel = sel1[sel1['source_id'] == ids]
            if sel.size == 0:
                continue
            calsrc = eph.FixedBody()
            calsrc._ra = np.deg2rad(sel[0]['ra'])
            calsrc._dec = np.deg2rad(sel[0]['dec'])
            calsrc.compute(self.ALMA)
            if eph.separation(qrsrc, calsrc) > np.deg2rad(radius):
                continue
            estflux = self.estimate_flux(sel, exp_freq)
            if estflux is None:
                continue
            else:
                flux, flux_error, wt_sum, min_date, nobs, min_freq_ratio = estflux
            row = np.array([sel[0]])
            row['flux'] = flux
            row['flux_error'] = flux_error
            row['frequency'] = exp_freq
            row['flux_w'] = wt_sum
            row['date_observed'] = np.max(sel['date_observed'])
            row['radius'] = np.rad2deg(eph.separation(qrsrc, calsrc))
            row['nobs'] = nobs
            print ids, min_date, nobs
            query = np.concatenate([query, row])
        self.queryResult = query
        return query

    def query2(self, ra=0., dec=0., min_flux=0., max_flux=1e13,
               min_freq=0., max_freq=1e15, radius=3., tdy=2,
               tdd=0, tlimit=160, grid=False):

        """
        Special method to query non_grid sources that need to be observed.
        :param ra:
        :param dec:
        :param min_flux:
        :param max_flux:
        :param min_freq:
        :param max_freq:
        :param radius:
        :param exp_freq:
        :param tdy:
        :param tdd:
        :param tlimit:
        :param grid:
        :return:
        """

        query2 = np.zeros(0, dtype=self.sctype)
        catalogue = np.copy(self.catalogue)
        qrsrc = eph.FixedBody()
        qrsrc._ra = np.deg2rad(ra)
        qrsrc._dec = np.deg2rad(dec)
        qrsrc.compute(self.ALMA)
        delta = timedelta(days=365 * tdy + tdd)
        sel1 = catalogue[
            (catalogue['frequency'] >= min_freq) &
            (catalogue['frequency'] <= max_freq) &
            (catalogue['flux'] >= min_flux) &
            (catalogue['flux'] <= max_flux) &
            (catalogue['cat_id'] == 5)]
        for ids in np.unique(sel1['source_id']):
            if grid:
                if ids not in self.grid_dict.values():
                    continue
            sel = sel1[(sel1['source_id'] == ids) & (sel1['date_observed'] >= self.date - delta)]
            print ids
            if sel.size != 0:
                continue
            sel2 = sel1[(sel1['source_id'] == ids)]
            print sel2['cat_id']
            calsrc = eph.FixedBody()
            calsrc._ra = np.deg2rad(sel2[0]['ra'])
            calsrc._dec = np.deg2rad(sel2[0]['dec'])
            calsrc.compute(self.ALMA)
            if eph.separation(qrsrc, calsrc) > np.deg2rad(radius):
                continue

            row = np.array([sel2[0]])
            row['date_observed'] = np.max(sel2['date_observed'])
            row['radius'] = np.rad2deg(eph.separation(qrsrc, calsrc))
            query2 = np.concatenate([query2, row])
        self.queryResult2 = query2
        return query2

    def estimate_flux(self, sel, exp_freq):
        sp_index = -0.7
        p_flux = []
        pw_flux = []
        wt_sum = 0.0
        nobs = 0
        min_freq_ratio = 100000.0
        obs_date = self.date.year + self.date.month / 100. + self.date.day / 10000.
        min_date = self.date - timedelta(365)
        sel_c = np.copy(sel)
        maxfreq = np.max(sel_c['frequency'])

        if 85.0e9 < maxfreq < 602.0e9:
            allflux = np.max(sel_c[sel_c['frequency'] == maxfreq]['flux'])
            flux9row = np.array([sel_c[sel_c['frequency'] == maxfreq][0]])
            flux9row['flux'] = allflux * ((660.0e9 / maxfreq) ** (-0.7))
            flux9row['frequency'] = 660.0e9
            flux9row['date_observed'] = self.date
            sel_c = np.concatenate([sel_c, flux9row])
        if sel_c.size == 0:
            return None
        for m in sel_c:
            freq_temp = m['frequency']
            flux_temp = m['flux'] * 1000.0
            tratio = exp_freq / freq_temp
            xratio = tratio
            date_temp = np.float(str(m['date_observed']).split('T')[0].replace('-', ''))
            date_time = self.getDate(date_temp)
            dif_time = obs_date - date_time
            if xratio < 1.0:
                xratio = 1.0 / xratio
            if tratio > 0.5 and dif_time < 1.0:
                tflux = flux_temp * (tratio ** sp_index)
                p_flux.append(tflux)
                tempwt = 1.00
                min_freq_ratio = np.minimum(min_freq_ratio, xratio)
                if tratio > 2.0 or tratio < 0.8:
                    tempwt = 0.5
                if tratio > 3.0 or tratio < 0.5:
                    tempwt = 0.3
                if dif_time > 0.3:
                    tempwt *= 0.5
                if dif_time > 0.7:
                    tempwt *= 0.5
                pw_flux.append(tflux * tempwt)
                wt_sum += tempwt
                min_date = np.maximum(min_date, m['date_observed'])
                nobs += 1
        if len(p_flux) == 0:
            return None
        elif len(p_flux) == 1:
            s_flux = p_flux[0]
            e_flux = s_flux / 10.0
        else:
            s_flux = np.average(pw_flux) / wt_sum * len(p_flux)
            e_flux = np.std(p_flux)
            if e_flux < s_flux / 10.0:
                e_flux = s_flux / 10.0
        return s_flux, e_flux, wt_sum, min_date, nobs, min_freq_ratio

    def find_bandpass(self, target_dict, freq, horizon='20'):
        self.ALMA.horizon = horizon
        ephemeris = False
        ra = []
        dec = []
        numSci = 0
        for src in target_dict:
            if src['fieldSource'] == 'ScienceParameters':
                ra.append(src['ra'])
                dec.append(src['dec'])
                numSci += 1
                if src['solarSystem'] != 'Unspecified':
                    ephemeris = True
        if ephemeris:
            use_new_qc = True
            if len(ra) == 1:
                qc_ra = ra[0]
                qc_dec = dec[0]
            elif len(ra) > 0:
                qc_ra, qc_dec = calc_center(ra, dec)
        else:
            if numSci == 0:
                use_new_qc = False
            elif numSci == 1:
                use_new_qc = False
            else:
                use_new_qc = True
                qc_ra, qc_dec = calc_center(ra, dec)

        for src in target_dict:
            if src['intent'] == 'Science':
                continue
            if 'BandpassCal' in src['fieldSource'] and src['isquery']:
                good = np.zeros(0, dtype=self.sctype)
                radius = src['searchRadius']
                if not use_new_qc:
                    candidates = self.query(
                        ra=src['queryCenterLong'], dec=src['queryCenterLat'], min_flux=1.0, radius=radius,
                        exp_freq=freq * 1e9, tdy=1)
                else:
                    candidates = self.query(
                        ra=qc_ra, dec=qc_dec, min_flux=1.0, radius=radius,
                        exp_freq=freq * 1e9, tdy=1)
                nchan = 128
                nant12 = 32
                nspw = len(src['bandwidths'])
                ch_BW = np.min(src['bandwidths']) / nchan / nspw * 1000.0
                rms_chan1 = self.getRms(src['frequencies']) * np.sqrt((32.0 / nant12) * (7500.0 / ch_BW) * 2.0)
                rms_chan64 = rms_chan1 / 8.0
                SNR_bcal = 50
                bmax_scan = 15.0
                min_band_flux64 = rms_chan64 * SNR_bcal / np.sqrt(bmax_scan) * np.sqrt(nant12 * (nant12 - 1) * 0.5 / (nant12 - 3))
                candidates_flux = candidates[candidates['flux'] > 0.9 * min_band_flux64]
                for c in candidates_flux:
                    obj = eph.FixedBody()
                    obj._ra = eph.degrees(str(c['ra']))
                    obj._dec = eph.degrees(str(c['dec']))
                    obj.compute(self.ALMA)
                    if obj.alt > eph.degrees('56'):
                        good = np.concatenate([good, np.array([c])])
                rating = -9999
                bpc = ''
                if good.size == 0 and radius < 120:
                    ok = 'No Bandpass available. Radius for query is %d' % radius
                    return ok
                if good.size == 0:
                    ok = 'No Bandpass available.'
                    return ok
                if good.size > 0:
                    print good
                    for g in good:
                        rated = np.minimum(5.0, g['flux_w'])
                        tflux = g['flux'] / (4.0 * min_band_flux64)
                        rated *= np.minimum(1.0, tflux)
                        sep = g['radius']
                        rated *= np.minimum(1.0, (8. / sep) ** 1.5)
                        terr = g['flux'] / g['flux_error'] / 5.0
                        rated *= np.minimum(1.0, terr)
                        print rated
                        if rated > rating:
                            rating = rated
                            bpc = g
                    calibrators = bpc
            if 'BandpassCal' in src['fieldSource'] and not src['isquery']:
                calibrators = src

        return calibrators

    def getRms(self, obs_freq):
        # Use sensitivies from private Table
        freq_sens = self.sensitivities
        nsen = len(freq_sens)
        freq = []
        sens = []

        for i in range(0, nsen / 2 - 1):
            freq.append(np.float(freq_sens[2 * i]))
            sens.append(np.float(freq_sens[2 * i + 1]))

        nfreq = len(freq)
        #   Find nearest frequency entry for each obs_freq
        rms_noise = []
        for spw in obs_freq:
            findex_min = 0
            fval_min = 1.0E20
            for i in range(0, nfreq):
                if np.abs(freq[i] - spw) < fval_min:
                    fval_min = np.abs(freq[i] - spw)
                    findex_min = i

            rms_noise.append(sens[findex_min])
        norm_rms_noise = np.max(rms_noise)
        return norm_rms_noise

    def getDate(self, date_temp):
        t_yr = date_temp / 10000.0
        date_yr = np.int(t_yr)
        t_mon = date_temp - date_yr * 10000.0
        date_mon = np.int(t_mon / 100.0)
        date_day = date_temp - date_yr * 10000.0 - date_mon * 100.0
        date_time = date_yr + (date_mon-1.0)/12.0 + date_day/365.0
        return date_time


def calc_center(ra, dec):
    X = []
    Y = []
    Z = []
    c = 0
    for lon in ra:
        X.append(np.cos(np.deg2rad(dec[c])) * np.cos(np.deg2rad(lon)))
        Y.append(np.cos(np.deg2rad(dec[c])) * np.sin(np.deg2rad(lon)))
        Z.append(np.sin(np.deg2rad(dec[c])))
        c += 1
    x = np.mean(X)
    y = np.mean(Y)
    z = np.mean(Z)

    ra1 = math.atan2(y, x)
    hyp = math.sqrt(x * x + y * y)
    dec1 = math.atan2(z, hyp)
    if ra1 < 0:
        ra1 += 2 * eph.pi

    return np.rad2deg(ra1), np.rad2deg(dec1)