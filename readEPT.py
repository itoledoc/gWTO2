__author__ = 'ignacio'

import numpy as np
import csv
import cx_Oracle
import pandas as pd
from lxml import objectify

val = '{Alma/ValueTypes}'
prj = '{Alma/ObsPrep/ObsProject}'
sbl = '{Alma/ObsPrep/SchedBlock}'
conx_strin = 'almasu/alma4dba@ALMA_ONLINE.OSF.CL'

filler = ['2012.1.00003.S',
          '2012.1.00014.S',
          '2012.1.00019.S',
          '2012.1.00022.S',
          '2012.1.00039.S',
          '2012.1.00047.S',
          '2012.1.00056.S',
          '2012.1.00058.S',
          '2012.1.00060.S',
          '2012.1.00073.S',
          '2012.1.00110.S',
          '2012.1.00112.S',
          '2012.1.00120.S',
          '2012.1.00154.S',
          '2012.1.00155.S',
          '2012.1.00157.S',
          '2012.1.00171.S',
          '2012.1.00181.S',
          '2012.1.00204.S',
          '2012.1.00238.S',
          '2012.1.00248.S',
          '2012.1.00261.S',
          '2012.1.00271.S',
          '2012.1.00280.S',
          '2012.1.00305.S',
          '2012.1.00313.S',
          '2012.1.00322.S',
          '2012.1.00323.S',
          '2012.1.00333.S',
          '2012.1.00335.S',
          '2012.1.00338.S',
          '2012.1.00339.S',
          '2012.1.00351.S',
          '2012.1.00357.S',
          '2012.1.00358.S',
          '2012.1.00387.S',
          '2012.1.00391.S',
          '2012.1.00398.S',
          '2012.1.00405.S',
          '2012.1.00440.S',
          '2012.1.00451.S',
          '2012.1.00454.S',
          '2012.1.00461.S',
          '2012.1.00470.S',
          '2012.1.00503.S',
          '2012.1.00517.S',
          '2012.1.00526.S',
          '2012.1.00532.S',
          '2012.1.00534.S',
          '2012.1.00536.S',
          '2012.1.00545.S',
          '2012.1.00564.S',
          '2012.1.00566.S',
          '2012.1.00567.S',
          '2012.1.00571.S',
          '2012.1.00577.S',
          '2012.1.00608.S',
          '2012.1.00632.S',
          '2012.1.00640.S',
          '2012.1.00681.S',
          '2012.1.00698.S',
          '2012.1.00709.S',
          '2012.1.00726.S',
          '2012.1.00731.S',
          '2012.1.00753.S',
          '2012.1.00759.S',
          '2012.1.00764.S',
          '2012.1.00800.S',
          '2012.1.00807.S',
          '2012.1.00817.S',
          '2012.1.00848.S',
          '2012.1.00849.S',
          '2012.1.00919.S',
          '2012.1.00927.S',
          '2012.1.00934.S',
          '2012.1.00947.S',
          '2012.1.00952.S',
          '2012.1.00955.S',
          '2012.1.00959.S',
          '2012.1.00995.S',
          '2012.1.01012.S',
          '2012.1.01025.S',
          '2012.1.01060.S',
          '2012.1.01080.S',
          '2012.1.01087.S',
          '2012.1.01092.S',
          '2012.1.01111.S',
          '2012.1.01116.S',
          '2012.1.01159.S',
          '2012.1.01161.S',
          '2012.1.01162.S',
          '2012.1.01165.S',
          '2012.1.01173.S']

time_critical = {
    'uid://A002/X5a279f/X1': 'Oct 14 2013 to March 27 2014.',
    'uid://A002/X5a279f/X2': 'Oct 14 2013 to March 27 2014.',
    'uid://A002/X5a9a13/X6f4': 'ToO',
    'uid://A002/X5a9a13/X6f5': 'ToO',
    'uid://A002/X5a9a13/X6f6': 'ToO',
    'uid://A002/X5a9a13/X704': 'ToO',
    'uid://A002/X5a9a13/X787': 'ToO',
    'uid://A002/X5a9a13/X788': 'ToO',
    'uid://A002/X5a9a13/X789': 'ToO',
    'uid://A002/X5a9a13/X78a': 'ToO',
    'uid://A002/X5a9a13/X78b': 'ToO',
    'uid://A002/X5a9a13/Xdd': 'All SB within 5 hours',
    'uid://A002/X5a9a13/Xde': 'All SB within 5 hours',
    'uid://A002/X5a9a13/Xdf': 'All SB within 5 hours',
    'uid://A002/X5a9a13/Xe0': 'All SB within 5 hours',
    'uid://A002/X5a9a13/Xe1': 'All SB within 5 hours',
    'uid://A002/X5d7935/X17b': '2013-Aug-12T17:55 to 2013-Aug-17T00:30',
    'uid://A002/X609170/Xf2': 'All within one day',
    'uid://A002/X609170/Xf3': 'All within one day',
    'uid://A002/X609170/Xf4': 'All within one day',
    'uid://A002/X609170/Xf5': 'All within one day',
    'uid://A002/X609170/Xf6': 'All within one day',
    'uid://A002/X6444ba/X134': 'Aug',
    'uid://A002/X6444ba/X135': 'Sep',
    'uid://A002/X6444ba/X136': 'Oct',
    'uid://A002/X6444ba/X137': 'Oct/Nov',
    'uid://A002/X6444ba/X138': 'Nov/Dec',
    'uid://A002/X6444ba/X139': 'Jan',
    'uid://A002/X6444ba/X13a': 'Feb',
    'uid://A002/X6444ba/X13b': 'Mar',
    'uid://A002/X6802f4/Xc': 'Late Sept - Oct 2013',
    'uid://A002/X6f9b0f/X152': 'DDT',
    'uid://A002/X6f9b0f/X153': 'DDT',
    'uid://A002/X6f9b0f/X154': 'DDT'
}


def read_data():
    """
    Reads SB and project information from Andreas' all.sbinfo file, and queries the
    archive for SB status and shiftlog entries related to the SB execution to get the
    number of qa0 pass, qa0 fail and qa0 wait statuses
    :return: an sbarr structured array, with schedUid, projUid, projCode,
    """
    print "Reading all.sbinfo file and querying archive for SBs status"
    print "This might take some time"
    conx_string = "almasu/alma4dba@ALMA_ONLINE.OSF.CL"
    connection = cx_Oracle.connect(conx_string)
    #dns_tns = cx_Oracle.makedsn('oraosf.osf.alma.cl', 1521, 'ALMA1')
    #connection = cx_Oracle.connect('almasu', 'alma4dba', dns_tns)
    cursor = connection.cursor()

    sbtype = [('schedUid', 'a30'), ('projUid', 'a30'), ('projCode', 'a30'),
              ('band', 'i2'), ('priority', 'a10'), ('rank', 'i2'),
              ('exec', 'a4'), ('reqExec', 'i2'), ('QA0_Pass', 'i2'),
              ('QA0_Wait', 'i2'), ('QA0_Fail', 'i2'),
              ('grade', 'a2'), ('score', 'f4'), ('sbname', 'a40'),
              ('sbStatus', 'a20'), ('arrayConf', 'a50'),
              ('arrayReq', 'a15'), ('modeName', 'a30'), ('pwv', 'f4'), ('RA', 'f4'),
              ('DEC', 'f4'), ('filename', 'a90'), ('tc', 'a40'), ('repFreq', 'f4'),
              ('whynot', 'a50'), ('trans', 'f4'), ('time-stamp', 'f4'), ('rise_LST', 'a10'), ('set_LST', 'a10')]

    httpfile = open('/data/Cycle1/daily-backup/all.sbinfo')
    #httpfile = open('/data1/home/alundgre/test/all.sbinfo') #Andreas 2014-01-28
    datab = csv.reader(httpfile, delimiter='\t')
    sbarr = np.zeros(0, dtype=sbtype)
    for i in datab:
        try:
            sbuid = i[3].strip()
            qa0_pass, qa0_fail, qa0_wait, status = count_exec_status(cursor, sbuid)
            try:
                arr_conf = i[10].strip().split(',')
                arr_conf = filter(None, arr_conf)
                arr_conf = ','.join(arr_conf)
            except Exception:
                arr_conf = ''
            sbname = i[2].strip()
            if (('eleted' in sbname) or
               ('not use' in sbname) or
               ('Do Not' in sbname) or
               ('DO NOT' in sbname) or
               ('DO_NOT' in sbname) or
               ('DELET' in sbname) or
               ('Do not' in sbname)):
               # print i[0], i[2], i[3]
                continue
            if i[0].strip() in filler:
                priority = 'FILLER'
            else:
                priority = 'HIGHEST'
                
            if sbuid in time_critical.keys():
                tc = time_critical[sbuid]
            else:
                tc = 'False'
            sbtemp = np.array(
                [(sbuid, i[1].strip(), i[0].strip(),
                  int(i[4].strip()[-2:]), priority, 0, i[7].strip(),
                  0, qa0_pass, qa0_wait, qa0_fail,
                  '', -99, i[2].strip(), status, arr_conf,
                  i[6].strip(), '', 0., 0., 0., '', tc, 1000, 'Available', 0., 0., '00:00:00', '00:00:00')],
                dtype=sbtype)
            sbarr = np.concatenate((sbarr, sbtemp))
        except Exception, e:
            print e
            continue
    cursor.close()
    connection.close()
    httpfile.close()
    return sbarr


def count_exec_status(cursor, sbuid):
    # print "querying for %s info..." % sbuid
    sql = "SELECT * from ALMA.shiftlog_entries " \
          "where se_project_code is not null " \
          "and (se_location = 'OSF-AOS' or se_location = 'TST-AOS2' " \
          "or se_location = 'OSF-AOS2') " \
          "and SE_SB_ID = '%s'" % sbuid
    sql2 = "SELECT domain_entity_state from ALMA.sched_block_status " \
           "where domain_entity_id = '%s'" % sbuid
    cursor.execute(sql)
    entries = cursor.fetchall()
    if len(entries) == 0:
        cursor.execute(sql2)
        status = cursor.fetchall()
        return 0, 0, 0, status[0][0]
    else:
        qp = 0
        qw = 0
        qf = 0
        for e in entries:
            if e[-2] is None:
                qw += 1
            elif e[-2] == 'Pass':
                qp += 1
            elif e[-2] == 'Fail':
                qf += 1
            else:
                continue
        cursor.execute(sql2)
        status = cursor.fetchall()
        return qp, qf, qw, status[0][0]