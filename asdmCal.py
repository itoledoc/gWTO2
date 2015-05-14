import cx_Oracle
import pandas as pd
import ephem
from astropy.time import Time


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

    try:
        df = pd.DataFrame(
            pd.np.array(df),
            columns=['UID', 'CALDATA_ID', 'TIME', 'CAL_TYPE', 'SCAN']
        )
    except ValueError:
        print "No data for the last day"
        return None

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

    try:
        df = pd.DataFrame(
            pd.np.array(df),
            columns=['UID', 'ANTENNA', 'BAND', 'BB', 'CALDATA_ID', 'TREC_VAL',
                     'TSYS_VAL', 'CALTYPE', 'POL_VAL', 'SBGAIN_VAL',
                     'FREQ_RANGE_VAL', 'START_VALID_TIME'])
    except ValueError:
        return None

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
    for _ in namepol:
        trec.append(float(rec[c]))
        tsys.append(float(sys[c]))
        sbgain.append(float(gain[c]))
        c += 1
    freqmin = float(df_at.FREQ_RANGE_VAL.split()[3]) * 1E-9
    freqmax = float(df_at.FREQ_RANGE_VAL.split()[4]) * 1E-9
    date = to_timestamp(df_at.START_VALID_TIME)

    out = [df_at.UID, df_at.ANTENNA, df_at.BAND, df_at.BB,
           df_at.CALDATA_ID, freqmin, freqmax,
           date]
    out.extend(trec)
    out.extend(tsys)
    out.extend(sbgain)
    names = ['UID', 'ANTENNA', 'BAND', 'BB', 'CALDATA_ID', 'FREQMIN', 'FREQMAX',
             'TIME']
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

    try:
        df = pd.DataFrame(
            pd.np.array(df),
            columns=['UID', 'BB', 'BAND', 'ATM_CORR', 'CALDATA_ID',
                     'DIRECTION',
                     'FREQ_RANGE_VAL', 'ANTENNAS', 'BLLENGTH', 'AMPLI_VAL',
                     'PHASERMS_VAL', 'POL_VAL', 'DECORR_VAL', 'NBASEL', 'NPOL',
                     'PHASE_VAL', 'TIME'])
    except ValueError:
        return None

    rows = df.apply(lambda row: trans_phase(row), axis=1)
    tab = []
    for r in rows:
        for r2 in r:
            tab.append(r2)

    table = pd.DataFrame(
        pd.np.array(tab),
        columns=['UID', 'TIME', 'CALDATA_ID', 'POL', 'BB', 'BAND', 'AZ', 'EL',
                 'ATM_CORR', 'FREQ_MIN', 'FREQ_MAX', 'ANT1', 'ANT2',
                 'BLLENGTH', 'PHASE_RMS', 'AMP', 'DECORR', 'PHASE']
    )

    return table


def trans_phase(row):

    l = []
    pol = row.POL_VAL.split()
    numpol = int(pol[2])
    namepol = []
    for i in range(numpol):
        nombre = pol[i + 3].split('</value>')[0]
        namepol.append(nombre)

    date = to_timestamp(row.TIME)
    nbl = int(row.NBASEL)

    az = pd.np.rad2deg(float(strip_val(row.DIRECTION)[2]))
    el = pd.np.rad2deg(float(strip_val(row.DIRECTION)[3]))
    freq_min = float(strip_val(row.FREQ_RANGE_VAL)[2]) * 1E-9
    freq_max = float(strip_val(row.FREQ_RANGE_VAL)[3]) * 1E-9

    ant_list = strip_val(row.ANTENNAS)[3:]
    bllength = strip_val(row.BLLENGTH)
    phaserms_val = strip_val(row.PHASERMS_VAL)
    ampli_val = strip_val(row.AMPLI_VAL)
    decorr_val = strip_val(row.DECORR_VAL)
    phase_val = strip_val(row.PHASE_VAL)

    for b in range(nbl):
        ant1 = ant_list[b * 2].replace('\"', '')
        ant2 = ant_list[b * 2 + 1].replace('\"', '')
        bll = float(bllength[2 + b])
        for p in range(numpol):
            phrms = pd.np.rad2deg(
                float(phaserms_val[(3 + b) + p * nbl]))
            amp = float(ampli_val[(3 + b) + p * nbl])
            decorr = float(decorr_val[(3 + b) + p * nbl])
            phase = pd.np.rad2deg(
                float(phase_val[(3 + b) + p * nbl]))
            l.append([row.UID, date, row.CALDATA_ID, namepol[p], row.BB,
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
            columns=['UID', 'ANTENNA', 'ATM_CORR', 'BB', 'BAND', 'CALDATA_ID',
                     'REF_ANT', 'DELAY_OFF', 'POL_T', 'TIME', 'NUM_RECEP',
                     'NUM_SB', 'DELAY_ERR'])
    except ValueError:
        return None

    return df.apply(lambda row: trans_delay(row), axis=1)


def trans_delay(row):
    pol = row.POL_T.replace('</value>', '').replace('<value>', '').split()
    namepol = pol[2:]

    delay = strip_val(row.DELAY_OFF)[int(pol[0]) + 1:]
    error = strip_val(row.DELAY_ERR)[int(pol[0]) + 1:]
    delay_l = []
    error_l = []
    c = 0
    for _ in namepol:
        delay_l.append(float(delay[c]))
        error_l.append(float(error[c]))
        c += 1

    out = [row.UID, row.ANTENNA, row.ATM_CORR, row.BB,
           row.BAND, row.CALDATA_ID, row.REF_ANT, to_timestamp(row.TIME)]

    out.extend(delay_l)
    out.extend(error_l)

    names = ['UID', 'ANTENNA', 'ATM_CORR', 'BB', 'BAND', 'CALDATA_ID',
             'REF_ANT', 'TIME']
    for n in ['delay_', 'error_']:
        for p in namepol:
            names.append(n + p)

    return pd.Series(out, index=names)


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
    df.START_TIME = df.apply(
        lambda row: to_timestamp(row['START_TIME']), axis=1)
    df.END_TIME = df.apply(
        lambda row: to_timestamp(row['END_TIME']), axis=1)

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
        columns=['UID', 'CALDATA_ID', 'SCAN', 'CAL_INTENT', 'TIME']
    )

    df.SCAN = df.apply(lambda row: int(row['SCAN'].split()[-2]), axis=1)
    df.TIME = df.apply(lambda row: to_timestamp(row['TIME']), axis=1)

    return df


def query_point(cursor, uid, q1=False):

    sql = str(
        'SELECT ARCHIVE_UID, CAL_DATA_ID, ANTENNA_NAME, RECEIVER_BAND_ENUMV,'
        'COLL_OFFSET_ABSOLUTE_VAL, COLL_OFFSET_RELATIVE_VAL, COLL_ERROR_VAL,'
        'POLARIZATION_TYPES_VAL, BEAM_WIDTH_VAL, FREQUENCY_RANGE_VAL,'
        'START_VALID_TIME, DIRECTION_VAL '
        'FROM SCHEDULING_AOS.ASDM_CALPOINTING '
        'WHERE ARCHIVE_UID = \'%s\'' % uid
    )

    print(sql)
    print("Executing QUERY, please wait...")
    cursor.execute(sql)
    df = []
    for value in cursor:
        r = list(value)
        for i in [4, 5, 6, 7, 8, 9, 11]:
            r[i] = value[i].read()
        df.append(r)

    df = pd.DataFrame(
        pd.np.array(df),
        columns=['UID', 'CALDATA_ID', 'ANTENNA', 'BAND', 'OFFSET_ABS',
                 'OFFSET_REL', 'OFFSET_ERR', 'POL', 'BEAMWIDTH', 'FREQ',
                 'TIME', 'DIRECTION']
    )

    if q1:
        t = df.TIME.astype(int).max()
        sql = str(
            'SELECT ARCHIVE_UID, CAL_DATA_ID, ANTENNA_NAME,'
            'RECEIVER_BAND_ENUMV,COLL_OFFSET_ABSOLUTE_VAL, '
            'COLL_OFFSET_RELATIVE_VAL, COLL_ERROR_VAL,'
            'POLARIZATION_TYPES_VAL, BEAM_WIDTH_VAL, FREQUENCY_RANGE_VAL,'
            'START_VALID_TIME, DIRECTION_VAL '
            'FROM SCHEDULING_AOS.ASDM_CALPOINTING '
            'WHERE START_VALID_TIME > %d' % (t - 5 * 3600. * 1E9)
        )

        print(sql)
        print("Executing QUERY for QA1, please wait...")
        cursor.execute(sql)

        dfq1 = []

        for value in cursor:
            r = list(value)
            for i in [4, 5, 6, 7, 8, 9, 11]:
                r[i] = value[i].read()
            dfq1.append(r)

        dfq1 = pd.DataFrame(
            pd.np.array(dfq1),
            columns=['UID', 'CALDATA_ID', 'ANTENNA', 'BAND', 'OFFSET_ABS',
                     'OFFSET_REL', 'OFFSET_ERR', 'POL', 'BEAMWIDTH', 'FREQ',
                     'TIME', 'DIRECTION']
        )

        return [df.apply(lambda row: trans_point(row), axis=1),
                dfq1.apply(lambda row: trans_point(row), axis=1)]

    else:
        return df.apply(lambda row: trans_point(row), axis=1)


def trans_point(row):

    abs_off_x = tosec(strip_val(row.OFFSET_ABS)[3])
    rel_off_x = tosec(strip_val(row.OFFSET_REL)[3])
    err_off_x = tosec(strip_val(row.OFFSET_ERR)[3])
    beam_x = tosec(strip_val(row.BEAMWIDTH)[3])
    abs_off_y = tosec(strip_val(row.OFFSET_ABS)[4])
    rel_off_y = tosec(strip_val(row.OFFSET_REL)[4])
    err_off_y = tosec(strip_val(row.OFFSET_ERR)[4])
    beam_y = tosec(strip_val(row.BEAMWIDTH)[4])
    az = pd.np.rad2deg(float(strip_val(row.DIRECTION)[2]))
    el = pd.np.rad2deg(float(strip_val(row.DIRECTION)[3]))

    mean_freq = pd.np.mean([float(strip_val(row.FREQ)[2]),
                            float(strip_val(row.FREQ)[3])])

    out = [row.UID, row.ANTENNA, row.BAND, to_timestamp(row.TIME),
           row.CALDATA_ID, mean_freq, az, el, rel_off_x, rel_off_y,
           abs_off_x, abs_off_y, err_off_x, err_off_y,
           beam_x, beam_y]

    names = ['UID', 'ANTENNA', 'BAND', 'TIME', 'CALDATA_ID', 'FREQ_MEAN',
             'AZ', 'EL', 'REL_OFF_X', 'REL_OFF_Y', 'ABS_OFF_X', 'ABS_OFF_Y',
             'ERR_X', 'ERR_Y', 'BW_X', 'BW_Y']

    return pd.Series(out, index=names)


def query_stl(cursor):

    sql = str(
        'SELECT SE_ID, SE_SUBJECT, SE_TIMESTAMP, SE_START, SE_ARRAYENTRY_ID,'
        'SE_ARRAYNAME, SE_ARRAYTYPE, SE_ARRAYFAMILY, SE_CORRELATORTYPE, '
        'SE_PROJECT_CODE, SE_SB_ID, SE_EB_UID, SE_STATUS, SE_TYPE, SE_SB_CODE '
        'FROM ALMA.SHIFTLOG_ENTRIES '
        'WHERE SE_TIMESTAMP >  '
        'to_date(\'2015-04-01 00:00:00\', \'YYYY-MM-DD HH24:MI:SS\') '
        'AND SE_LOCATION = \'OSF-AOS\''
    )
    print(sql)
    print("Executing QUERY for QA1, please wait...")
    cursor.execute(sql)

    return pd.DataFrame(cursor.fetchall(),
                        columns=[rec[0] for rec in cursor.description])


def strip_val(s):

    return s.replace('</value>', '').replace('<value>', '').split()


def tosec(val):

    return pd.np.rad2deg(float(val)) * 3600.