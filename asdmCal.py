import cx_Oracle
import pandas as pd
import ephem
from astropy.time import Time
import datetime as dt


def open_conn():

    conx_string = 'almasu/alma4dba@ALMA_ONLINE.OSF.CL'
    connection = cx_Oracle.connect(conx_string)
    cursor = connection.cursor()

    return cursor


def query_last_day(cursor):

    site = ephem.Observer()
    day = Time(ephem.date(site.date - 3.).datetime(), format='datetime',
               scale='utc').mjd * 24 * 3600
    print('%d' % (day * 1E9))

    sql = str(
        'SELECT ARCHIVE_UID, CAL_DATA_ID, START_TIME_OBSERVED, '
        'CAL_TYPE_ENUMV, SCAN_SET_VAL '
        'FROM SCHEDULING_AOS.ASDM_CALDATA '
        'WHERE START_TIME_OBSERVED > %d' % (day * 1E9))
    print(sql)
    print("Executing QUERY, please wait...")
    cursor.execute(sql)
    df = []
    for value in cursor:
        r = list(value)
        for i in [4]:
            r[i] = value[i].read()
        df.append(r)

    df = pd.DataFrame(
        pd.np.array(df),
        columns=['UID', 'CAL_DATA_ID', 'TIME', 'CAL_TYPE', 'SCAN']
    )

    df.SCAN = df.apply(lambda row: int(row['SCAN'].split()[-2]), axis=1)
    df.TIME = df.apply(lambda row: to_timestamp(row['TIME']), axis=1)

    return df


def to_timestamp(d):

    datet = Time(float(d) * 1E-9 / 3600 / 24, format='mjd')
    return datet.datetime


def query_atm(cursor, uid):

    sql = str(
        'SELECT ARCHIVE_UID, ANTENNA_NAME, RECEIVER_BAND_ENUMV,'
        'baseband_name_enumv, CAL_DATA_ID,'
        'T_REC_VAL, T_SYS_VAL,'
        'SYSCAL_TYPE_ENUMV, POLARIZATION_TYPES_VAL,'
        'SB_GAIN_VAL, FREQUENCY_RANGE_VAL,'
        'START_VALID_TIME '
        'FROM SCHEDULING_AOS.ASDM_CALATMOSPHERE '
        'WHERE ARCHIVE_UID = \'%s\'' % uid)
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
        columns=['UID', 'ANTENNA', 'BAND', 'BB', 'CAL_DATA_ID', 'TREC_VAL',
                 'TSYS_VAL', 'CALTYPE', 'POL_VAL', 'SBGAIN_VAL',
                 'FREQ_RANGE_VAL', 'START_VALID_TIME'])

    return df.apply(lambda row: trans_atm(row), axis=1)


def trans_atm(df_at):

    pol = df_at.POL_VAL.split()
    numpol = int(pol[2])
    namepol = []
    for i in range(numpol):
        nombre = pol[i + 3].split('</value>')[0]
        namepol.append('_' + nombre)
    rec = df_at.TREC_VAL.split()[3:]
    sys = df_at.TSYS_VAL.split()[3:]
    gain = df_at.SBGAIN_VAL.split()[3:]
    trec = []
    tsys = []
    sbgain = []
    c = 0
    for p in namepol:
        trec.append(float(rec[c]))
        tsys.append(float(sys[c]))
        sbgain.append(float(gain[c]))
        c += 1
    freqmin = float(df_at.FREQ_RANGE_VAL.split()[3]) * 1E-9
    freqmax = float(df_at.FREQ_RANGE_VAL.split()[4]) * 1E-9
    date = to_timestamp(df_at.START_VALID_TIME)

    out = [df_at.UID, df_at.ANTENNA, df_at.BAND, df_at.BB,
           df_at.CAL_DATA_ID, freqmin, freqmax,
           date]
    out.extend(trec)
    out.extend(tsys)
    out.extend(sbgain)
    names = ['UID', 'ANTENNA', 'BAND', 'BB', 'SCAN_ID', 'FREQMIN', 'FREQMAX',
             'DATE']
    for n in ['trec', 'tsys', 'sbgain']:
        for p in namepol:
            names.append(n + p)

    return pd.Series(out, index=names)


def query_phase(cursor, uid):

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
        'WHERE ARCHIVE_UID = \'%s\'' % uid)
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
        columns=['UID', 'BB', 'BAND', 'ATM_CORR', 'CAL_DATA_ID', 'DIRECTION',
                 'FREQ_RANGE_VAL', 'ANTENNAS', 'BLLENGTH', 'AMPLI_VAL',
                 'PHASERMS_VAL', 'POL_VAL', 'DECORR_VAL', 'NBASEL', 'NPOL',
                 'PHASE_VAL', 'TIME'])

    rows = df.apply(lambda row: trans_phase(row), axis=1)
    tab = []
    for r in rows:
        for r2 in r:
            tab.append(r2)

    table = pd.DataFrame(
        pd.np.array(tab),
        columns=['UID', 'TIME', 'CAL_ID', 'POL', 'BB', 'BAND', 'AZ', 'EL',
                 'ATM_CORR', 'FREQ_MIN', 'FREQ_MAX', 'ANT1', 'ANT2',
                 'BLLENGTH', 'PHASE_RMS', 'AMP', 'DECORR', 'PHASE']
    )

    return table


def trans_phase(row):

    l = []
    pol = row.POL_VAL.split(' ')
    numpol = int(pol[2])
    namepol = []
    for i in range(numpol):
        nombre = pol[i + 3].split('</value>')[0]
        namepol.append(nombre)

    date = to_timestamp(row.TIME)
    nbl = int(row.NBASEL)

    az = pd.np.rad2deg(float(row.DIRECTION.split()[3]))
    el = pd.np.rad2deg(float(row.DIRECTION.split()[4]))
    freq_min = float(row.FREQ_RANGE_VAL.split()[3]) * 1E-9
    freq_max = float(row.FREQ_RANGE_VAL.split()[4]) * 1E-9

    ant_list = row.ANTENNAS.split()[4:-1]
    for b in range(nbl):
        ant1 = ant_list[b * 2].replace('\"', '')
        ant2 = ant_list[b * 2 + 1].replace('\"', '')
        bll = float(row.BLLENGTH.split()[3 + b])
        for p in range(numpol):
            phrms = pd.np.rad2deg(
                float(row.PHASERMS_VAL.split()[(4 + b) + p * nbl]))
            amp = float(row.AMPLI_VAL.split()[(4 + b) + p * nbl])
            decorr = float(row.DECORR_VAL.split()[(4 + b) + p * nbl])
            phase = pd.np.rad2deg(
                float(row.PHASE_VAL.split()[(4 + b) + p * nbl]))
            l.append([row.UID, date, row.CAL_DATA_ID, namepol[p], row.BB,
                      row.BAND, az, el, row.ATM_CORR, freq_min, freq_max, ant1,
                      ant2, bll, phrms, amp, decorr, phase])
    return l


def query_delay(cursor, uid):

    sql = str(
        'SELECT ARCHIVE_UID, ANTENNA_NAME, ATM_PHASE_CORRECTION_ENUMV,'
        'BASEBAND_NAME_ENUMV, RECEIVER_BAND_ENUMV, CAL_DATA_ID,'
        'REF_ANTENNA_NAME,'
        'DELAY_OFFSET_VAL, POLARIZATION_TYPES_VAL,'
        'START_VALID_TIME, NUM_RECEPTOR, NUM_SIDEBAND, DELAY_ERROR_VAL '
        'FROM SCHEDULING_AOS.ASDM_CALDELAY '
        'WHERE ARCHIVE_UID = \'%s\'' % uid)
    print(sql)
    print("Executing QUERY, please wait...")
    cursor.execute(sql)
    df = []
    for value in cursor:
        r = list(value)
        for i in [7, 8, 12]:
            r[i] = value[i].read()
        df.append(r)
    try:
        df = pd.DataFrame(
            pd.np.array(df),
            columns=['UID', 'ANTENNA', 'ATM_CORR', 'BB', 'BAND', 'SCAN',
                     'REF_ANT', 'DELAY_OFF', 'POL_T', 'TIME', 'NUM_RECEP',
                     'NUM_SB', 'DELAY_ERR'])
    except ValueError:
        return None

    return df


def trans_delay(row):

    pass


def query_antennas(cursor, uid):

    sql = str(
        'SELECT ARCHIVE_UID, ANTENNA_ID, POSITION_VAL, NAME, STATION_ID '
        'FROM SCHEDULING_AOS.ASDM_ANTENNA '
        'WHERE ARCHIVE_UID = \'%s\'' % uid
    )

    print(sql)
    print("Executing QUERY, please wait...")
    cursor.execute(sql)
    df = []
    for value in cursor:
        r = list(value)
        for i in [2]:
            r[i] = value[i].read()
        df.append(r)

    df = pd.DataFrame(
        pd.np.array(df),
        columns=['UID', 'ANTENNA_ID', 'POSITION_VAL', 'ANTENNA', 'PAD_ID'])

    return df


def query_flags(cursor, uid):

    sql = str('SELECT ARCHIVE_UID, FLAG_ID, NUM_ANTENNA, REASON,'
              'SPECTRAL_WINDOW_ID_VAL, ANTENNA_ID_VAL, START_TIME, END_TIME '
              'FROM SCHEDULING_AOS.ASDM_FLAG '
              'WHERE ARCHIVE_UID = \'%s\'' % uid)

    print(sql)
    print("Executing QUERY, please wait...")
    cursor.execute(sql)
    df = []
    for value in cursor:
        r = list(value)
        for i in [4, 5]:
            r[i] = value[i].read()
        df.append(r)

    df = pd.DataFrame(
        pd.np.array(df),
        columns=['UID', 'FLAG_ID', 'NUM_ANTENNA', 'REASON', 'SPW_ID',
                 'ANTENNA_ID', 'START_TIME', 'END_TIME']
    )

    return df


def query_subscans(cursor, uid):

    sql = str(
        'SELECT ARCHIVE_UID, SCAN_NUMBER, SUBSCAN_NUMBER, START_TIME, END_TIME,'
        'FIELD_NAME '
        'FROM SCHEDULING_AOS.ASDM_SUBSCAN '
        'WHERE ARCHIVE_UID = \'%s\'' % uid
    )

    print(sql)
    print("Executing QUERY, please wait...")
    cursor.execute(sql)
    df = []
    for value in cursor:
        r = list(value)
        df.append(r)

    df = pd.DataFrame(
        pd.np.array(df),
        columns=['UID', 'SCAN', 'SUBSCAN', 'START_TIME', 'END_TIME',
                 'FIELD_NAME']
    )

    return df


def query_station(cursor, uid):

    sql = str(
        'SELECT STATION_ID, ARCHIVE_UID, POSITION_VAL, NAME '
        'FROM SCHEDULING_AOS.ASDM_STATION '
        'WHERE ARCHIVE_UID = \'%s\'' % uid
    )

    print(sql)
    print("Executing QUERY, please wait...")
    cursor.execute(sql)
    df = []
    for value in cursor:
        r = list(value)
        for i in [2]:
            r[i] = value[i].read()
        df.append(r)

    df = pd.DataFrame(
        pd.np.array(df),
        columns=['PAD_ID', 'UID', 'POSITION', 'PAD_NAME']
    )

    return df


def query_scans(cursor, uid):

    sql = str(
        'SELECT ARCHIVE_UID, SCAN_NUMBER, NUM_SUBSCAN, NUM_FIELD, START_TIME,'
        'END_TIME, SCAN_INTENT_VAL, FIELD_NAME_VAL '
        'FROM SCHEDULING_AOS.ASDM_SCAN '
        'WHERE ARCHIVE_UID = \'%s\'' % uid
    )

    print(sql)
    print("Executing QUERY, please wait...")
    cursor.execute(sql)
    df = []
    for value in cursor:
        r = list(value)
        for i in [6, 7]:
            r[i] = value[i].read()
        df.append(r)

    df = pd.DataFrame(
        pd.np.array(df),
        columns=['UID', 'SCAN', 'NUM_SUBCAN', 'NUM_FIELD', 'START_TIME',
                 'END_TIME', 'SCAN_INTENT', 'FIELD_NAME']
    )

    df.SCAN = df.SCAN.astype(float)
    df.SCAN_INTENT = df.SCAN_INTENT.str.split().apply(
        lambda x: x[3].split('<')[0])
    df.FIELD_NAME = df.FIELD_NAME.str.split().apply(
        lambda x: x[3].replace('\"', ''))

    return df.sort('SCAN')


def query_caldata(cursor, uid):

    sql = str(
        'SELECT ARCHIVE_UID, CAL_DATA_ID, SCAN_SET_VAL, CAL_TYPE_ENUMV,'
        'START_TIME_OBSERVED '
        'FROM SCHEDULING_AOS.ASDM_CALDATA '
        'WHERE ARCHIVE_UID = \'%s\'' % uid
    )

    print(sql)
    print("Executing QUERY, please wait...")
    cursor.execute(sql)
    df = []
    for value in cursor:
        r = list(value)
        for i in [2]:
            r[i] = value[i].read()
        df.append(r)

    df = pd.DataFrame(
        pd.np.array(df),
        columns=['UID', 'CAL_DATA_ID', 'SCAN', 'CAL_INTENT', 'START_TIME']
    )

    return df