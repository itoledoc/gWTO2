#!/usr/bin/env python
__author__ = 'itoledo'

import cx_Oracle
import pandas as pd
import optparse

conx_string = 'almasu/alma4dba@ALMA_ONLINE.OSF.CL'
connection = cx_Oracle.connect(conx_string)
cursor = connection.cursor()


def query_atm(uid):

    sql = str(
        'SELECT ARCHIVE_UID, ANTENNA_NAME, RECEIVER_BAND_ENUMV,'
        'baseband_name_enumv, CAL_DATA_ID,'
        'DBMS_LOB.substr(T_REC_VAL), DBMS_LOB.substr(T_SYS_VAL),'
        'SYSCAL_TYPE_ENUMV, DBMS_LOB.substr(POLARIZATION_TYPES_VAL),'
        'DBMS_LOB.substr(SB_GAIN_VAL), DBMS_LOB.substr(FREQUENCY_RANGE_VAL) '
        'FROM SCHEDULING_AOS.ASDM_CALATMOSPHERE '
        'WHERE ARCHIVE_UID = \'%s\'' % uid)
    print sql
    print "Executing QUERY, please wait..."
    cursor.execute(sql)
    df = pd.DataFrame(
        cursor.fetchall(),
        columns=['UID', 'ANTENNA', 'BAND', 'BB', 'SCAN_ID', 'TREC_VAL',
                 'TSYS_VAL', 'CALTYPE', 'POL_VAL', 'SBGAIN_VAL',
                 'FREQ_RANGE_VAL'])
    return df


def extract_val(ser):

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
    out = [ser.UID, ser.ANTENNA, ser.BAND, ser.BB, ser.SCAN_ID, freqmin,
           freqmax]
    out.extend(trec)
    out.extend(tsys)
    out.extend(sbgain)
    names = ['UID', 'ANTENNA', 'BAND', 'BB', 'SCAN_ID', 'FREQMIN', 'FREQMAX']
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

    usage = "usage: %prog sb_uid\n"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(
        '-f', '--format', dest='filet', default='xls',
        help="Select xls or csv as file output")

    (options, args) = parser.parse_args()

    if len(args) == 0:
        print("Please specify sb uid")
        return None

    if options.filet not in ['csv', 'xls']:
        print "-f must be csv or xls"
        exit()
    df = query_atm(args[0])
    if len(df) == 0:
        print "The specified SB was not found on the archive"
        exit()

    table = df.apply(lambda r: extract_val(r), axis=1)

    if options.filet == 'xls':
        table.to_excel(
            '%s_atmosphere.xls' %
            args[0].replace('uid://', '').replace('/', '_'))
    else:
        table.to_csv(
            '%s_atmosphere.xls' %
            args[0].replace('uid://', '').replace('/', '_'),
            sep=',')
    exit()

if __name__ == '__main__':
    main()