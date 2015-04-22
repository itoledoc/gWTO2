#!/usr/bin/env python
__author__ = 'itoledo'

import cx_Oracle
import pandas as pd
import optparse
import ephem
from astropy.time import Time


def query_atm(cursor):

    site = ephem.Observer()
    day = Time(ephem.date(site.date - 1.).datetime(), format='datetime',
               scale='utc').mjd * 24 * 3600
    print('%d' % (day * 1E9))
    sql = str(
        'SELECT ARCHIVE_UID, ANTENNA_NAME, RECEIVER_BAND_ENUMV,'
        'baseband_name_enumv, CAL_DATA_ID,'
        'T_REC_VAL, T_SYS_VAL,'
        'SYSCAL_TYPE_ENUMV, POLARIZATION_TYPES_VAL,'
        'SB_GAIN_VAL, FREQUENCY_RANGE_VAL,'
        'START_VALID_TIME '
        'FROM SCHEDULING_AOS.ASDM_CALATMOSPHERE '
        'WHERE START_VALID_TIME > %d' % (day * 1E9))
    print(sql)
    print("Executing QUERY, please wait...")
    cursor.execute(sql)

    df = []

    for value in cursor:
        r = list(value)
        for i in [5, 6, 8, 9, 10]:
            r[i] = value[i].read()
        df.append(r)

    df = pd.DataFrame(
        pd.np.array(df),
        columns=['UID', 'ANTENNA', 'BAND', 'BB', 'SCAN_ID', 'TREC_VAL',
                 'TSYS_VAL', 'CALTYPE', 'POL_VAL', 'SBGAIN_VAL',
                 'FREQ_RANGE_VAL', 'START_VALID_TIME'])
    return df


def query_phase(cursor):

    site = ephem.Observer()
    day = Time(ephem.date(site.date - 1.).datetime(), format='datetime',
               scale='utc').mjd * 24 * 3600
    print('%d' % (day * 1E9))
    sql = str(
        'SELECT ARCHIVE_UID, BASEBAND_NAME_ENUMV, RECEIVER_BAND_ENUMV,'
        'ATM_PHASE_CORRECTION_ENUMV, CAL_DATA_ID,'
        'DIRECTION_VAL, FREQUENCY_RANGE_VAL,'
        'ANTENNA_NAMES_VAL,'
        'BASELINE_LENGTHS_VAL, AMPLI_VAL,'
        'PHASE_R_M_S_VAL,'
        'POLARIZATION_TYPES_VAL, '
        'DECORRELATION_FACTOR_VAL,'
        'NUM_BASELINE, NUM_RECEPTOR,'
        'PHASE_VAL, START_VALID_TIME '
        'FROM SCHEDULING_AOS.ASDM_CALPHASE '
        'WHERE START_VALID_TIME > %d' % (day * 1E9))
    print(sql)
    print("Executing QUERY, please wait...")
    cursor.execute(sql)
    df = []
    for value in cursor:
        r = list(value)
        for i in [5, 6, 7, 8, 9, 10, 11, 12, 15]:
            r[i] = value[i].read()

        df.append(r)
    df = pd.DataFrame(
        pd.np.array(df),
        columns=['UID', 'BB', 'BAND', 'ATM_CORR', 'SCAN_ID', 'DIRECTION',
                 'FREQ_RANGE_VAL', 'ANTENNAS', 'BLLENGTH', 'AMPLI_VAL',
                 'PHASERMS_VAL', 'POL_VAL', 'DECORR_VAL', 'NBASEL', 'NPOL',
                 'PHASE_VAL', 'TIME'])
    return df


def query_delay(cursor):

    site = ephem.Observer()
    day = Time(ephem.date(site.date - 1.).datetime(), format='datetime',
               scale='utc').mjd * 24 * 3600
    print('%d' % (day * 1E9))
    sql = str(
        'SELECT ARCHIVE_UID, ANTENNA_NAME, ATM_PHASE_CORRECTION_ENUMV,'
        'BASEBAND_NAME_ENUMV, RECEIVER_BAND_ENUMV, CAL_DATA_ID,'
        'REF_ANTENNA_NAME,'
        'DELAY_OFFSET_VAL, POLARIZATION_TYPES_VAL,'
        'START_VALID_TIME, NUM_RECEPTOR, NUM_SIDEBAND, DELAY_ERROR_VAL '
        'FROM SCHEDULING_AOS.ASDM_CALDELAY '
        'WHERE START_VALID_TIME > %d' % (day * 1E9))
    print(sql)
    print("Executing QUERY, please wait...")
    cursor.execute(sql)
    df = []
    for value in cursor:
        r = list(value)
        for i in [7, 8, 12]:
            r[i] = value[i].read()
        df.append(r)

    df = pd.DataFrame(
        pd.np.array(df),
        columns=['UID', 'ANTENNA', 'ATM_CORR', 'BB', 'BAND', 'SCAN', 'REF_ANT',
                 'DELAY_OFF', 'POL_T', 'TIME', 'NUM_RECEP', 'NUM_SB',
                 'DELAY_ERR'])
    return df


def extract_atmval(ser):

    pol = ser.POL_VAL.split(' ')
    numpol = int(pol[2])
    namepol = []
    for i in range(numpol):
        nombre = pol[i + 3].split('</value>')[0]
        namepol.append('_' + nombre)
    rec = ser.TREC_VAL.split(' ')[3:]
    sys = ser.TSYS_VAL.split(' ')[3:]
    gain = ser.SBGAIN_VAL.split(' ')[3:]
    trec = []
    tsys = []
    sbgain = []
    c = 0
    for p in namepol:
        trec.append(float(rec[c]))
        tsys.append(float(sys[c]))
        sbgain.append(float(gain[c]))
        c += 1
    freqmin = float(ser.FREQ_RANGE_VAL.split(' ')[3]) * 1E-9
    freqmax = float(ser.FREQ_RANGE_VAL.split(' ')[4]) * 1E-9
    date = Time(ser.START_VALID_TIME * 1E-9 / 3600 / 24, format='mjd')

    out = [ser.UID, ser.ANTENNA, ser.BAND, ser.BB,
           int(ser.SCAN_ID.split('_')[-1]), freqmin, freqmax,
           date.datetime.isoformat().replace('T', ' ').split('.')[0]]
    out.extend(trec)
    out.extend(tsys)
    out.extend(sbgain)
    names = ['UID', 'ANTENNA', 'BAND', 'BB', 'SCAN_ID', 'FREQMIN', 'FREQMAX',
             'DATE']
    for n in ['trec', 'tsys', 'sbgain']:
        for p in namepol:
            names.append(n + p)
    return pd.Series(out, index=names)


def main():
    """
    Extrac CAL_ATMOSPHERE information from archive, and stores it as xls or csv
    file

    :return:
    """

    usage = "usage: %prog sb_uid"
    parser = optparse.OptionParser(usage=usage)
    (options, args) = parser.parse_args()
    conx_string = 'almasu/alma4dba@ALMA_ONLINE.OSF.CL'
    connection = cx_Oracle.connect(conx_string)
    cursor = connection.cursor()

    df = query_atm(cursor)
    cursor.close()
    connection.close()
    if len(df) == 0:
        print("The specified SB was not found on the archive")
        exit()

    table = df.apply(lambda r: extract_atmval(r), axis=1)

    table.to_csv('day_atmosphere.cvs')

    exit()

if __name__ == '__main__':
    main()