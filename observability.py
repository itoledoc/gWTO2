__author__ = 'ignacio'


"""
[{'bandwidths': [2.0, 2.0, 2.0, 2.0],
  'channels': [128, 128, 128, 128],
  'fieldSource': 'AmplitudeCalParameters',
  'frequencies': [93.0000000001,
   94.9999999999,
   105.0000000001,
   106.9999999999],
  'intent': 'Amplitude',
  'isquery': True,
  'maxFlux': -1.0,
  'maxFrequency': -1.0,
  'maxSources': 40,
  'minFlux': -1.0,
  'minFrequency': -1.0,
  'npol': 2,
  'queryCenterLat': -5.90990098,
  'queryCenterLong': 83.85825795,
  'queryIntent': 'Phase',
  'searchRadius': 0.0,
  'source': '{Alma/ObsPrep/SchedBlock}QuerySource'},
 {'bandwidths': [2.0, 2.0, 2.0, 2.0],
  'channels': [128, 128, 128, 128],
  'fieldSource': 'BandpassCalParameters',
  'frequencies': [93.0000000001,
   94.9999999999,
   105.0000000001,
   106.9999999999],
  'intent': 'Bandpass',
  'isquery': True,
  'maxFlux': -1.0,
  'maxFrequency': -1.0,
  'maxSources': 40,
  'minFlux': -1.0,
  'minFrequency': -1.0,
  'npol': 2,
  'queryCenterLat': -5.90990098,
  'queryCenterLong': 83.85825795,
  'queryIntent': 'Phase',
  'searchRadius': 45.0,
  'source': '{Alma/ObsPrep/SchedBlock}QuerySource'},
 {'bandwidths': [2.0, 2.0, 2.0, 2.0],
  'channels': [128, 128, 128, 128],
  'fieldSource': 'PhaseCalParameters',
  'frequencies': [93.0000000001,
   94.9999999999,
   105.0000000001,
   106.9999999999],
  'intent': 'Phase',
  'isquery': True,
  'maxFlux': -1.0,
  'maxFrequency': -1.0,
  'maxSources': 40,
  'minFlux': -1.0,
  'minFrequency': -1.0,
  'npol': 2,
  'queryCenterLat': -5.90990098,
  'queryCenterLong': 83.85825795,
  'queryIntent': 'Phase',
  'searchRadius': 15.0,
  'source': '{Alma/ObsPrep/SchedBlock}QuerySource'}
"""

import ephem
import numpy as np
import SBParser as sbp
import datetime

SSO2 = ['Ceres', 'Pallas', 'Vesta', 'Juno']
SSO = ['Moon', 'Sun', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn',
       'Uranus', 'Neptune', 'Pluto']
MOON = ['Ganymede', 'Europa', 'Callisto', 'Io', 'Titan']

# Library of minor bodies not in ephem catalog
ephem.Ceres = ephem.readdb("Ceres,e,10.593979,80.327633,72.292128,2.76680728,"
                       "0,0.07579733,10.557582,11/4/2013,2000.0,3.34,0.12")
ephem.Pallas = ephem.readdb("Pallas,e,34.836245,173.102354,309.933755,2.77243389,"
                        "0,0.2315651,352.778998,11/4/2013,2000.0,4.13,0.11")
ephem.Juno = ephem.readdb("Juno,e,12.980573,169.877848,248.349895,2.67030537,"
                      "0,0.255287,302.768187,11/4/2013,2000.0,5.33,0.32")
ephem.Vesta = ephem.readdb("Vesta,e,7.140518,103.851567,151.199439,2.36138405,"
                       "0,0.08850238,272.215309,11/4/2013,2000.0,3.2,0.32")

# Create alma Observer instance for ALMA site
alma = ephem.Observer()
#noinspection PyPropertyAccess
alma.lat = '-23.0262015'
#noinspection PyPropertyAccess
alma.long = '-67.7551257'
alma.elev = 5060


def observable(targets, prio, date, ALMA=alma, horizon='20'):
    ALMA.date = date
    ALMA.horizon = horizon
    observability = {}
    for t in targets:
        if t in prio['schedUid'] and targets[t] is not None:
            elev = []
            ra = []
            dec = []
            remaining = []
            lstr = []
            lsts = []
            tlist = targets[t]
            for s in tlist:
                if s['intent'] == 'Science' and s['solarSystem'] in SSO and s['solarSystem'] == s['source']:
                    ALMA.date = date
                    ALMA.horizon = horizon
                    obj = eval('ephem.' + s['solarSystem'] + '()')
                    obj.compute(ALMA)
                    ra.append(obj.ra)
                    dec.append(obj.dec)
                    elev.append(obj.alt)
                    if obj.alt > ephem.degrees(horizon):
                        try:
                            sets = ALMA.next_setting(obj)
                            rise = ALMA.previous_rising(obj)
                            remaining.append(sets.datetime() - ALMA.date.datetime())
                            ALMA.date = rise
                            lstr.append(ALMA.sidereal_time())
                            ALMA.date = sets
                            lsts.append(ALMA.sidereal_time())
                        except ephem.AlwaysUpError:
                            remaining.append(datetime.timedelta(1))
                            lstr.append(ephem.hours('0'))
                            lsts.append(ephem.hours('0'))
                    else:
                        rise = ALMA.next_rising(obj)
                        sets = ALMA.next_setting(obj)
                        remaining.append(ALMA.date.datetime() - rise.datetime())
                        ALMA.date = rise
                        lstr.append(ALMA.sidereal_time())
                        ALMA.date = sets
                        lsts.append(ALMA.sidereal_time())
                elif s['intent'] == 'Science' and s['solarSystem'] in MOON and s['solarSystem'] == s['source']:
                    ALMA.date = date
                    ALMA.horizon = horizon
                    obj = eval('ephem.' + s['solarSystem'] + '()')
                    obj.compute(ALMA)
                    ra.append(obj.ra)
                    dec.append(obj.dec)
                    elev.append(obj.alt)
                    obj.radius = 0.
                    if obj.alt > ephem.degrees(horizon):
                        try:
                            sets = ALMA.next_setting(obj)
                            rise = ALMA.previous_rising(obj)
                            remaining.append(sets.datetime() - ALMA.date.datetime())
                            ALMA.date = rise
                            lstr.append(ALMA.sidereal_time())
                            ALMA.date = sets
                            lsts.append(ALMA.sidereal_time())
                        except ephem.AlwaysUpError:
                            remaining.append(datetime.timedelta(1))
                            lstr.append(ephem.hours('0'))
                            lsts.append(ephem.hours('0'))
                    else:
                        rise = ALMA.next_rising(obj)
                        sets = ALMA.next_setting(obj)
                        remaining.append(ALMA.date.datetime() - rise.datetime())
                        ALMA.date = rise
                        lstr.append(ALMA.sidereal_time())
                        ALMA.date = sets
                        lsts.append(ALMA.sidereal_time())
                elif s['intent'] == 'Science':
                    ALMA.date = date
                    ALMA.horizon = horizon
                    obj = ephem.FixedBody()
                    obj._ra = np.deg2rad(s['ra'])
                    obj._dec = np.deg2rad(s['dec'])
                    obj.compute(ALMA)
                    ra.append(obj.ra)
                    dec.append(obj.dec)
                    elev.append(obj.alt)
                    if obj.alt > ephem.degrees(horizon):
                        if not obj.circumpolar:
                            sets = ALMA.next_setting(obj)
                            rise = ALMA.previous_rising(obj)
                            remaining.append(sets.datetime() - ALMA.date.datetime())
                            ALMA.date = rise
                            lstr.append(ALMA.sidereal_time())
                            ALMA.date = sets
                            lsts.append(ALMA.sidereal_time())
                        else:
                            remaining.append(datetime.timedelta(1))
                            lstr.append(ephem.hours('0'))
                            lsts.append(ephem.hours('0'))
                    else:
                        if obj.neverup:
                            remaining.append(datetime.timedelta(0))
                            ALMA.horizon = '0'
                            obj.compute(ALMA)
                            print obj.transit_alt, t
                            lstr.append(ephem.hours('0'))
                            lsts.append(ephem.hours('0'))
                        else:
                            rise = ALMA.next_rising(obj)
                            sets = ALMA.next_setting(obj)
                            remaining.append(ALMA.date.datetime() - rise.datetime())
                            ALMA.date = rise
                            lstr.append(ALMA.sidereal_time())
                            ALMA.date = sets
                            lsts.append(ALMA.sidereal_time())
                else:
                    continue
            emin = ephem.degrees('90')
            remain = datetime.timedelta(0)
            count = 0
            RA = ephem.hours('0')
            DEC = ephem.degrees('0')
            LSTR = ephem.hours('0')
            LSTS = ephem.hours('0')
            for el in elev:
                if el < emin:
                    emin = el
                    remain = remaining[count]
                    RA = ra[count]
                    DEC = dec[count]
                    LSTR = lstr[count]
                    LSTS = lsts[count]
                count += 1
            if LSTR == ephem.hours('0'):
                print "no LSTR nor LSRS calculated for % s" % t
            ALMA.date = date
            observability[t] = [emin, remain, ALMA.sidereal_time(), RA, DEC, str(LSTR), str(LSTS)]
    return observability




def freq_hpbw(freq):
    """
    Calculates Beam width in arcsec given a frequency in GHz
    @param freq:
    @return:
    """
    const = 1.22 * 2.99792 * 1e8 * 3600.0 * 180.0 / np.pi
    hpbw = const / (12. * freq * 1E9)
    return hpbw
