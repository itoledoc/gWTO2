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
        'DBMS_LOB.substr(T_REC_VAL), DBMS_LOB.substr(T_SYS_VAL),'
        'SYSCAL_TYPE_ENUMV, DBMS_LOB.substr(POLARIZATION_TYPES_VAL),'
        'DBMS_LOB.substr(SB_GAIN_VAL), DBMS_LOB.substr(FREQUENCY_RANGE_VAL),'
        'START_VALID_TIME '
        'FROM SCHEDULING_AOS.ASDM_CALATMOSPHERE '
        'WHERE START_VALID_TIME > %d' % (day * 1E9))
    print(sql)
    print("Executing QUERY, please wait...")
    cursor.execute(sql)
    df = pd.DataFrame(
        cursor.fetchall(),
        columns=['UID', 'ANTENNA', 'BAND', 'BB', 'SCAN_ID', 'TREC_VAL',
                 'TSYS_VAL', 'CALTYPE', 'POL_VAL', 'SBGAIN_VAL',
                 'FREQ_RANGE_VAL', 'START_VALID_TIME'])
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

    table.to_excel('day_atmosphere.xls')

    exit()

if __name__ == '__main__':
    main()