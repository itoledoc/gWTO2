__author__ = 'ignacio'

"""
Routines to read SB xml files, extract sources, create .cat catalogue files.
"""

from lxml import etree
import ephem
import numpy as np
import glob
import subprocess as subp
from datetime import datetime


def expSB(uid):
    subp.call('asdmExport %s' % uid, shell=True)
    uid = uid.replace('://', '___').replace('/', '_')
    check = subp.Popen('grep sbl:SchedBlockEntity %s/ASDM.xml' % uid,
                       stdout=subp.PIPE, shell=True).communicate()[0]
    if 'SchedBlockEntity' in check:
        filename = "%s/ASDM.xml" % uid
        return uid, filename
    else:
        return None
        # print "This uid is not in the archive or is not an SB"


def creacat(filename, date):

    val = '{Alma/ValueTypes}'
    sbl = '{Alma/ObsPrep/SchedBlock}'

    parser = etree.XMLParser()
    xmlfile = etree.parse(filename, parser)
    root = xmlfile.getroot()

    catalog = []
    ephemNo = False
    for og in root.findall('.//' + sbl + 'ObservingGroup'):
        index = og.find(sbl + 'index').text
        ordtarget = og.findall(sbl + 'OrderedTarget/' + sbl + 'TargetRef')
        for oid in ordtarget:
            otid = oid.attrib['partId']
            tsrc = source(root, otid, index, sbl, val, date)
            if tsrc == 10:
                print('Something is missing in the ObsPar for one Target of %s'
                      % filename)
                continue
            if tsrc != 0 and tsrc is not None:
                catalog.append(tsrc)
            if tsrc is None:
                ephemNo = True
    if ephemNo:
        return None
    return catalog


def source(root, ordTarId, index, sbl, val, date):
    ephemeris = True
    BW = []
    channels = []
    oparams = root.findall('.//' + sbl + 'AmplitudeCalParameters') +\
        root.findall('.//' + sbl + 'PointingCalParameters') +\
        root.findall('.//' + sbl + 'BandpassCalParameters') +\
        root.findall('.//' + sbl + 'AtmosphericCalParameters') +\
        root.findall('.//' + sbl + 'PhaseCalParameters') +\
        root.findall('.//' + sbl + 'ScienceParameters') +\
        root.findall('.//' + sbl + 'DelayCalParameters')

    targets = root.findall('.//' + sbl + 'Target')
    fieldSourceRef = None
    obsParamRef = None
    specParamRef = None
    while fieldSourceRef is None and len(targets) > 0:
        ttemp = targets.pop()
        fieldSourceRef = (ttemp.find(sbl + 'FieldSourceRef') if ordTarId ==
                          ttemp.attrib['entityPartId'] else None)
        obsParamRef = (ttemp.find(sbl + 'ObservingParametersRef') if
                       ordTarId == ttemp.attrib['entityPartId'] else None)
        specParamRef = (ttemp.find(sbl + 'AbstractInstrumentSpecRef') if
                        ordTarId == ttemp.attrib['entityPartId'] else None)
    fieldSourceRef_id = fieldSourceRef.attrib['partId']
    fieldSource = None

    obsParamRef_id = obsParamRef.attrib['partId']
    obsParam = None

    specParamRef_id = specParamRef.attrib['partId']
    specParam = None

    fsources = root.findall('.//' + sbl + 'FieldSource')
    specDefs = root.findall('.//' + sbl + 'SpectralSpec')

    freqs = [0]
    npol = 0
    while fieldSource is None and len(fsources) > 0:
        ttemp = fsources.pop()
        fieldSource = (ttemp if ttemp.attrib['entityPartId'] ==
                       fieldSourceRef_id else None)

    while obsParam is None and len(oparams) > 0:
        ttemp = oparams.pop()
        obsParam = (ttemp if ttemp.attrib['entityPartId'] ==
                    obsParamRef_id else None)
    if obsParam is None:
        return 10

    while specParam is None and len(specDefs) > 0:
        ttemp = specDefs.pop()
        specParam = (ttemp if ttemp.attrib['entityPartId'] ==
                     specParamRef_id else None)
        if specParam is None:
            continue

        freqs = specParam.findall(sbl + 'FrequencySetup/' + sbl +
                                  'BaseBandSpecification/' + sbl +
                                  'centerFrequency')

        spw = specParam.findall(sbl + 'BLCorrelatorConfiguration/' + sbl +
                                'BLBaseBandConfig/' + sbl +
                                'BLSpectralWindow')
        # Deal with ACA and TP sbs
        if len(spw) == 0:
            spw = specParam.findall(sbl + 'ACACorrelatorConfiguration/' + sbl +
                                    'ACABaseBandConfig/' + sbl +
                                    'ACASpectralWindow')

        pol = spw[0].attrib['polnProducts']
        npol = len(pol.split(','))
        BW = []
        channels = []
        for i in spw:
            BWunit = i.find(sbl + 'effectiveBandwidth').attrib['unit']
            BWval = convertGHz(float(i.find(sbl + 'effectiveBandwidth').text),
                               BWunit)
            BW.append(BWval)
            channels.append(int(i.find(sbl + 'effectiveNumberOfChannels').text))
    freqList = []
    for f in freqs:
        tfreq = float(f.text)
        tfreqUnit = f.attrib['unit']
        cfreq = convertGHz(tfreq, tfreqUnit)
        freqList.append(cfreq)

    refFreq = obsParam.findall(sbl + 'representativeFrequency')
    if len(refFreq) > 0:
        refFreq_unit = refFreq[0].attrib['unit']
        refFreq_val = float(refFreq[0].text)
        freq = convertGHz(refFreq_val, refFreq_unit)
    else:
        freq = np.mean(freqList)
    querySourceL = fieldSource.findall(sbl + 'QuerySource')
    # Routines to read JPL ephemeris from SB. Based on pyephem example code
    solarSystem = fieldSource.attrib['solarSystemObject']
    if solarSystem == 'Ephemeris':
        sEphem = fieldSource.find(sbl + 'sourceEphemeris')
        in_data = False
        now = date
        month_ints = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
        for line in sEphem.text.split('\n'):
            if line.startswith('$$SOE'):
                in_data = True
                c = 0
            elif line.startswith('$$EOE'):
                if not found:
                    # print "NO EPHEMERIS FOR CURRENT DATE. Setting RA=0, DEC=0"
                    ra = ephem.hours('00:00:00')
                    dec = ephem.degrees('00:00:00')
                    ephemeris = False
                    break
            elif in_data:
                datestr = line[1:6] + str(month_ints[line[6:9]]) + line[9:18]
                date = datetime.strptime(datestr, '%Y-%m-%d %H:%M')
                if now.datetime() > date:
                    data = line
                    found = False
                    c += 1
                else:
                    if c == 0:
                        #print("NO EPHEMERIS FOR CURRENT DATE. Setting RA=0,"
                        #      " DEC=0")
                        ra = ephem.hours('00:00:00')
                        dec = ephem.degrees('00:00:00')
                        ephemeris = False
                        break
                    ra = ephem.hours(data[23:34].strip().replace(' ', ':'))
                    dec = ephem.degrees(data[35:46].strip().replace(' ', ':'))
                    break
    # END of ephemeris reading CONTROL
    else:
        if len(querySourceL) == 1:
            qSourceCenter = querySourceL[0].find(sbl + 'queryCenter')
            ra = qSourceCenter.find(val + 'longitude')
            ra_unit = ra.attrib['unit']
            ra = ephem.hours(np.radians(convertDeg(float(ra.text), ra_unit)))
            dec = qSourceCenter.find(val + 'latitude')
            dec_unit = dec.attrib['unit']
            dec = ephem.degrees(np.radians(convertDeg(float(dec.text),
                                                      dec_unit)))
            radius = querySourceL[0].find(sbl + 'searchRadius')
        else:
            ra = fieldSource.find(sbl + 'sourceCoordinates/' + val +
                                  'longitude')
            ra = ephem.hours(np.radians(convertDeg(float(ra.text),
                                                   ra.attrib['unit'])))
            dec = fieldSource.find(sbl + 'sourceCoordinates/' + val +
                                   'latitude')
            dec = ephem.degrees(np.radians(convertDeg(float(dec.text),
                                                      dec.attrib['unit'])))
    try:
    	name = fieldSource.find(sbl + 'name').text.replace(' ', '_')
    except:
        print ordTarId
        name = 'unknown'
    sysVelocity = fieldSource.find(
        sbl + 'sourceVelocity').attrib['referenceSystem']
    velocity = fieldSource.find(
        sbl + 'sourceVelocity/' + val + 'centerVelocity').text

    try:
        cal = obsParam.tag.replace(sbl, '')
    except Exception, e:
        print "obsParam tag was not found, continuing (%s)" % e
        return 0
    src1 = 0
    if len(querySourceL) == 1:
        querySource = querySourceL[0]
        queryIntended = querySource.attrib['intendedUse']
        queryCenter = querySource.find(sbl + 'queryCenter')
        queryCenterLong = queryCenter.find(val + 'longitude')
        queryCenterLongUnit = queryCenterLong.attrib['unit']
        queryCenterLongVal = convertDeg(float(queryCenterLong.text),
                                        queryCenterLongUnit)
        queryCenterLat = queryCenter.find(val + 'latitude')
        queryCenterLatUnit = queryCenterLat.attrib['unit']
        queryCenterLatVal = convertDeg(float(queryCenterLat.text),
                                       queryCenterLatUnit)
        searchRadiusUnit = querySource.find(sbl + 'searchRadius').attrib['unit']
        searchRadius = convertDeg(
            float(querySource.find(sbl + 'searchRadius').text),
            searchRadiusUnit)
        # noinspection PyBroadException
        try:
            minFreqUnit = querySource.find(sbl + 'minFrequency').attrib['unit']
            minFreq = convertGHz(float(querySource.find(sbl +
                                                        'minFrequency').text),
                                 minFreqUnit)
            maxFreqUnit = querySource.find(sbl + 'maxFrequency').attrib['unit']
            maxFreq = convertGHz(float(querySource.find(sbl +
                                                        'maxFrequency').text),
                                 maxFreqUnit)
            minFluxUnit = querySource.find(sbl + 'minFlux').attrib['unit']
            minFlux = convertJy(float(querySource.find(sbl + 'minFlux').text),
                                minFluxUnit)
            maxFluxUnit = querySource.find(sbl + 'maxFlux').attrib['unit']
            maxFlux = convertJy(float(querySource.find(sbl + 'maxFlux').text),
                                maxFluxUnit)
        except Exception:
            minFreq = -1.
            maxFreq = -1.
            minFlux = -1.
            maxFlux = -1.
        maxSources = int(querySource.find(sbl + 'maxSources').text)

        qsrc = {'source': querySource.tag,
                'fieldSource': cal,
                'queryIntent': queryIntended,
                'intent': name,
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
                'isquery': True,
                'npol': npol}
        name = 'query_Center'
        t = 1
    else:
        name = fieldSource.find(sbl + 'sourceName').text.replace(' ', '_')
        pointings = fieldSource.findall(sbl + 'PointingPattern/' + sbl + 'phaseCenterCoordinates')
        mosaicF = fieldSource.find(sbl + 'PointingPattern/' + sbl + 'isMosaic')
        if mosaicF is not None:
            mosaic = mosaicF.text
        else:
            mosaic = 'false'
        src1 = {
            'source': name,
            'ra': ra * 180. / ephem.pi,
            'dec': dec * 180. / ephem.pi,
            'sysVel': sysVelocity,
            'vel': velocity,
            'frequency': freq,
            'intent': cal[:-10],
            'index': index,
            'solarSystem': solarSystem,
            'isquery': False,
            'fieldSource': cal,
            'ismosaic': mosaic,
            'pointings': len(pointings)}
        t = 2

    if t == 1 and ephemeris:
        # noinspection PyUnboundLocalVariable
        return qsrc
    elif t == 2 and ephemeris:
        return src1
    elif not ephemeris:
        # This means that a source which is a solar system objects have
        # outdated or no ephemeris
        return None
    else:
        return 0


def convertGHz(freq, unit):
    value = freq
    if unit == 'GHz':
        value = value
    elif unit == 'MHz':
        value *= 1e-3
    elif unit == 'kHz':
        value *= 1e-6
    elif unit == 'Hz':
        value *= 1e-9
    return value


def convertmJy(flux, unit):
    value = flux
    if unit == 'Jy':
        value *= 1e3
    elif unit == 'mJy':
        value = value
    return value


def convertJy(flux, unit):
    value = flux
    if unit == 'Jy':
        value = value
    elif unit == 'mJy':
        value /= 1000.
    return value


def convertDeg(angle, unit):
    value = angle
    if unit == 'mas':
        value /= 3600000.
    elif unit == 'arcsec':
        value /= 3600.
    elif unit == 'arcmin':
        value /= 60.
    elif unit == 'rad':
        value = value * ephem.pi / 180.
    elif unit == 'hours':
        value *= 15.
    return value
