__author__ = 'ignacio'

import numpy as np
import subprocess
import glob
from lxml import etree
import cx_Oracle
import pickle
import readEPT
import datetime
import SBParser
import ephem
import math


val = '{Alma/ValueTypes}'
prj = '{Alma/ObsPrep/ObsProject}'
sbl = '{Alma/ObsPrep/SchedBlock}'


def checkaots(sb_database, date):
    sb_databaseB = np.copy(sb_database)
    # path = './schedBlocks' + num
    # if path in glob.glob(path):
    #     subprocess.call("rm -rf %s" % path, shell=True)
    # subprocess.call('mkdir %s' % path, shell=True)

    targets_dat = {}

    if glob.glob("SBxml").__len__() == 0:
            subprocess.call("mkdir SBxml", shell=True)
            print "We will grab the SB xml files from the archive for the first" \
                  "time, this will take some extra-time"
            versions = {}
    else:
        if glob.glob("versions.dat").__len__() != 0:
            fn = open('versions.dat')
            versions = pickle.load(fn)
            fn.close()
        else:
            versions = {}
    conx_strin = 'almasu/alma4dba@ALMA_ONLINE.OSF.CL'
    connection = cx_Oracle.connect(conx_strin)
    #dns_tns = cx_Oracle.makedsn('oraosf.osf.alma.cl', 1521, 'ALMA1')
    #connection = cx_Oracle.connect('almasu', 'alma4dba', dns_tns)
    cursor = connection.cursor()
    for pc in np.unique(sb_database['projCode']):
        score, rank, grade, version = getObsProjecInfo(pc, cursor)
        sub_arr = sb_database[sb_database['projCode'] == pc]
        for sched in sub_arr:
            if pc in versions.keys():
                if version == versions[pc]:
                    xmlname = sched['schedUid'].replace("uid://", "").replace('/', '_')
                    filena = './SBxml/' + xmlname + '.xml'
                else:
                    print "Project %s has an updated version. Grabbing new SB xml files." % pc
                    xmlname = sched['schedUid'].replace("uid://", "").replace('/', '_')
                    filena = './SBxml/' + xmlname + '.xml'
                    creaXML(sched['schedUid'], filena, cursor)
            else:
                xmlname = sched['schedUid'].replace("uid://", "").replace('/', '_')
                filena = './SBxml/' + xmlname + '.xml'
                creaXML(sched['schedUid'], filena, cursor)

            parser = etree.XMLParser()
            try:
                doc = etree.parse(filena, parser)
            except IOError:
                creaXML(sched['schedUid'], filena, cursor)
            root = doc.getroot()
            obsunit = root.findall('.//' + prj + 'ObsUnitControl')[0]
            reqExec = int(root.find('.//' + sbl + 'executionCount').text)
            schedConst = root.findall('.//' + sbl + 'SchedulingConstraints')[0]
            repFreq_xml = schedConst.find(sbl + 'representativeFrequency')
            repFreq = float(repFreq_xml.text)
            repFreqUnit = repFreq_xml.attrib['unit']
            repFreq = convertGHz(repFreq, repFreqUnit)
            pwv = root.find('.//' + sbl + 'Preconditions/' + prj + 'WeatherConstraints/' + prj + 'maxPWVC').text
            arrayReq = root.find('.//' + prj + 'ObsUnitControl'
                                         ).attrib['arrayRequested']
            modeName = root.find('.//' + sbl + 'modeName').text
            sbname_or = root.find('.//' + prj + 'name').text
            sbname = sbname_or.replace(" ", "_")
            sbname = sbname.replace(":", "_")
            sbname = sbname.replace("(", "")
            sbname = sbname.replace(")", "")
            sbname = sbname.replace("\'", "")
            sbname = sbname.replace("/", "-")
            basename = sched['projCode']
            sbname = "%s_%s_SB" % (basename, sbname)
            # subprocess.call("cp %s %s/%s.xml" % (filena, path, sbname), shell=True)
            targets_dat[sched['schedUid']] = SBParser.creacat(filena, date)
            if targets_dat[sched['schedUid']] is None:
                whynot = 'Ephemeris Outdated'
                RA = 0.
                DEC = 0.
            else:
                ra = []
                dec = []
                for s in targets_dat[sched['schedUid']]:
                    if s['fieldSource'] == 'ScienceParameters' and not s['isquery']:
                        ra.append(s['ra'])
                        dec.append(s['dec'])
                if len(ra) == 0:
                    RA = 0.
                    DEC = 0.
                elif len(ra) == 1:
                    RA = ra[0] / 15.
                    DEC = dec[0]
                else:
                    ram, decm = calc_center(ra, dec)
                    RA = ram / 15.
                    DEC = decm
                whynot = sched['whynot']
            for sbin in sb_databaseB:
                if sbin['schedUid'] == sched['schedUid']:
                    sbin['rank'] = rank
                    sbin['grade'] = grade
                    sbin['score'] = score
                    sbin['arrayReq'] = arrayReq
                    sbin['modeName'] = modeName
                    sbin['RA'] = RA
                    sbin['DEC'] = DEC
                    sbin['filename'] = sbname
                    sbin['repFreq'] = repFreq
                    sbin['reqExec'] = reqExec
                    sbin['sbname'] = sbname_or
                    sbin['whynot'] = whynot
                    sbin['pwv'] = np.float(pwv)

        versions[pc] = version
    fn = open('versions.dat', 'w')
    pickle.dump(versions, fn)
    fn.close()
    cursor.close()
    connection.close()
    return sb_databaseB, targets_dat, versions


def update_sbdata(sb_database, targets_dat, date, versions):
    # path = './schedBlocks' + num
    # if path in glob.glob(path):
    #     subprocess.call("rm -rf %s" % path, shell=True)
    # subprocess.call('mkdir %s' % path, shell=True)
    conx_strin = 'almasu/alma4dba@ALMA_ONLINE.OSF.CL'
    connection = cx_Oracle.connect(conx_strin)
    #dns_tns = cx_Oracle.makedsn('oraosf.osf.alma.cl', 1521, 'ALMA1')
    #connection = cx_Oracle.connect('almasu', 'alma4dba', dns_tns)
    cursor = connection.cursor()
    sb_databaseB = np.copy(sb_database)
    sb_databaseB = update_exec_status(cursor, sb_databaseB)

    for pc in np.unique(sb_database['projCode']):
        score, rank, grade, version = getObsProjecInfo(pc, cursor)
        print pc, version
        sub_arr = sb_database[sb_database['projCode'] == pc]
        for sched in sub_arr:
            update = False
            update_target = False
            sched['whynot'] = ''
            if pc in versions.keys():
                if version == versions[pc]:
                    xmlname = sched['schedUid'].replace("uid://", "").replace('/', '_')
                    filena = './SBxml/' + xmlname + '.xml'
                else:
                    print "Project %s has an updated version. Grabbing new SB xml files." % pc
                    xmlname = sched['schedUid'].replace("uid://", "").replace('/', '_')
                    filena = './SBxml/' + xmlname + '.xml'
                    creaXML(sched['schedUid'], filena, cursor)
                    update = True
            else:
                xmlname = sched['schedUid'].replace("uid://", "").replace('/', '_')
                filena = './SBxml/' + xmlname + '.xml'
                creaXML(sched['schedUid'], filena, cursor)
                update = True

            if sched['schedUid'] in targets_dat.keys():
                if targets_dat[sched['schedUid']] is None:
                    update_target = True
                else:
                    for dic in targets_dat[sched['schedUid']]:
                        if dic['intent'] == 'Science':
                            if dic['solarSystem'] != 'Unspecified':
                                update_target = True
                            else:
                                continue
                        else:
                            continue

            if update and grade != 'Z':
                parser = etree.XMLParser()
                try:
                    doc = etree.parse(filena, parser)
                except IOError:
                    creaXML(sched['schedUid'], filena, cursor)
                root = doc.getroot()
                obsunit = root.findall('.//' + prj + 'ObsUnitControl')[0]
                reqExec = int(obsunit.find(prj + 'aggregatedExecutionCount').text)
                schedConst = root.findall('.//' + sbl + 'SchedulingConstraints')[0]
                repFreq_xml = schedConst.find(sbl + 'representativeFrequency')
                repFreq = float(repFreq_xml.text)
                repFreqUnit = repFreq_xml.attrib['unit']
                repFreq = convertGHz(repFreq, repFreqUnit)
                arrayReq = root.find('.//' + prj + 'ObsUnitControl'
                                             ).attrib['arrayRequested']
                pwv = root.find('.//' + sbl + 'Preconditions/' + prj + 'WeatherConstraints/' + prj + 'maxPWVC').text
                modeName = root.find('.//' + sbl + 'modeName').text
                sbname_or = root.find('.//' + prj + 'name').text
                sbname = sbname_or.replace(" ", "_")
                sbname = sbname.replace(":", "_")
                sbname = sbname.replace("(", "")
                sbname = sbname.replace(")", "")
                sbname = sbname.replace("\'", "")
                sbname = sbname.replace("/", "-")
                basename = sched['projCode']
                sbname = "%s_%s_SB" % (basename, sbname)
                # subprocess.call("cp %s %s/%s.xml" % (filena, path, sbname), shell=True)
                if targets_dat[sched['schedUid']] is None:
                    whynot = 'Ephemeris Outdated'
                    RA = 0.
                    DEC = 0.
                else:
                    ra = []
                    dec = []
                    for s in targets_dat[sched['schedUid']]:
                        if s['fieldSource'] == 'ScienceParameters' and not s['isquery']:
                            ra.append(s['ra'])
                            dec.append(s['dec'])
                    if len(ra) == 0:
                        RA = 0.
                        DEC = 0.
                    elif len(ra) == 1:
                        RA = ra[0] / 15.
                        DEC = dec[0]
                    else:
                        ram, decm = calc_center(ra, dec)
                        RA = ram / 15.
                        DEC = decm
                    whynot = sched['whynot']
                for sbin in sb_databaseB:
                    if sbin['schedUid'] == sched['schedUid']:
                        sbin['rank'] = rank
                        sbin['grade'] = grade
                        sbin['score'] = score
                        sbin['arrayReq'] = arrayReq
                        sbin['modeName'] = modeName
                        sbin['RA'] = RA
                        sbin['DEC'] = DEC
                        sbin['filename'] = sbname
                        sbin['repFreq'] = repFreq
                        sbin['reqExec'] = reqExec
                        sbin['sbname'] = sbname_or
                        sbin['whynot'] = whynot
                        sbin['pwv'] = np.float(pwv)
            if update_target and grade != 'Z':
                targets_dat[sched['schedUid']] = SBParser.creacat(filena, date)
                if targets_dat[sched['schedUid']] is None:
                    for sbin in sb_databaseB:
                        if sbin['schedUid'] == sched['schedUid']:
                            sbin['whynot'] = 'Ephemeris Outdated'
            else:
                continue
        versions[pc] = version

    fn = open('versions.dat', 'w')
    pickle.dump(versions, fn)
    fn.close()
    cursor.close()
    connection.close()
    return sb_databaseB, targets_dat, versions


def priority(sb_database, arr='12m', pwv=1.25, conf='', tran=''):

    sb_databaseB = np.copy(sb_database)

    ptype = [('schedUid', 'a30'), ('sbname', 'a40'),
             ('priority', 'f4'), ('SBCP', 'f4'), ('PCP', 'f4'), ('POSP', 'f4'),
             ('ExecP', 'f4'), ('ConfP', 'f4'), ('BP', 'f4'), ('ScP', 'f4')]
    prio_arr = np.zeros(0, dtype=ptype)

    t_dat = calc_tau(pwv)

    for sb in sb_databaseB:
        if arr == '12m':
            arrNames = ['TWELVE-M']
        elif arr == '7m':
            arrNames = ['ACA', 'SEVEN-M']
            confPrio = 1.
        elif arr == 'TP':
            arrNames = ['TP-Array']
            confPrio = 1.
        else:
            arrNames = []

        if sb['sbStatus'] == 'Phase2Submitted':
            sb['whynot'] = 'SB in PhaseIISubmitted Status'
            continue

        if sb['sbStatus'] == 'FullyObserved':
            sb['whynot'] = 'SB in FullyObserved Status'
            continue

        sbCompletition = 1. * (sb['QA0_Pass'] + sb['QA0_Wait']) / sb['reqExec']
        if sbCompletition < 1.:
            sbCompletitionPrio = 6. - 5. * sbCompletition
        else:
            sb['whynot'] = 'QA0Pass count = ExEx count'
            continue

        if sb['grade'] == 'Z':
            sb['whynot'] = 'Check project Status'
            continue

        if sb['arrayReq'] not in arrNames:
            continue

        if conf != 'all' and conf != '' and arr == '12m':
            arrayconf = sb['arrayConf'].split(',')
            if conf not in arrayconf:
                sb['whynot'] = 'Array Configuration not allowed'
                confPrio = 100.
            elif len(arrayconf) == 1:
                confPrio = 1.
            elif arrayconf[0] == conf or len(arrayconf) <= 3:
                confPrio = 3.
            else:
                confPrio = 5.

        elif conf == 'all' and arr == '12m':
            arrayconf = sb['arrayConf'].split(',')
            if len(arrayconf) > 5:
                confPrio = 1.
            else:
                sb['whynot'] = 'Is not array config. independent'
                confPrio = 100.

        elif conf == '' and arr == '12m':
            confPrio = 1.

        proj = sb['projCode']

        if sb['priority'] == 'FILLER':
            fil = 50.
        else:
            fil = 0.

        projExpExec = sb_database[(sb_database['projCode'] == proj) & (sb_database['reqExec'] > 0)]['reqExec'].sum()
        projExeExec = sb_database[(sb_database['projCode'] == proj) & (sb_database['reqExec'] > 0)]['QA0_Pass'].sum()
        projExeExec += sb_database[(sb_database['projCode'] == proj) & (sb_database['reqExec'] > 0)]['QA0_Wait'].sum()
        projCompletition = projExeExec / projExpExec
        if projCompletition <= 1.:
            projCompletitionPrio = 1 + projCompletition * 5.
            projOverSubPrio = 1.
        else:
            projCompletitionPrio = 6
            projOverSubPrio = 1. + (projCompletition - 1.) * (5 / 3.)

        if sb['exec'] == 'EA':
            execPrio = 1.
        if sb['exec'] == 'EU':
            execPrio = 1.
        if sb['exec'] == 'NA':
            execPrio = 4.
        if sb['exec'] == 'CL':
            execPrio = 4.

        freq = sb['repFreq']
        for p in t_dat:
                if freq < p['freq']:
                    tran_par = p[1]
                    break
                else:
                    continue

        if tran == -1.:
            if pwv < 0.6:
                tLim = 0.5
                factor = 1 - tLim
            else:
                tLim = 0.7
                factor = 1 - tLim
        else:
            tLim = tran
            factor = 1 - tLim

        if tran_par < tLim:
            sb['whynot'] = 'Transmission low'
            sb['trans'] = tran_par
            bandPrio = 1000.
        else:
            bandPrio = (tran_par - tLim) * (5. / factor) + 1.
            sb['trans'] = tran_par

        if pwv > 2.1 * sb['pwv']:
            sb['whynot'] = 'PWV is 2 times higher than the pwv used in the SB'

        scienRank = sb['rank']
        if scienRank < 0:
            scienPrio = 6.
        else:
            scienPrio = 6. - 5. * (1. * (sb_database['rank'].max() - scienRank) /
                                   sb_database['rank'].max())

        if sbCompletitionPrio != -9:
            ranking = (0.3 * bandPrio + 0.05 * scienPrio + 0.1 * execPrio +
                       0.1 * projCompletitionPrio +
                       0.15 * sbCompletitionPrio +
                       0.05 * projOverSubPrio + 0.25 * confPrio + fil)
        else:
            continue

        ptemp = np.array([(sb['schedUid'], sb['sbname'], ranking,
                           sbCompletitionPrio, projCompletitionPrio,
                           projOverSubPrio, execPrio, confPrio,
                           bandPrio, scienPrio)], dtype=ptype)
        prio_arr = np.concatenate((prio_arr, ptemp))

    prio_arr.sort(order='priority')
    return prio_arr, sb_databaseB


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


def creaXML(suid, filena, cursor):
    sql = "SELECT XMLTYPE.getClobVal(xml) from ALMA.xml_schedblock_entities where archive_uid = '%s'" % suid
    cursor.execute(sql)
    h = cursor.fetchall()
    text = h[0][0].read()
    fn = open(filena, 'w')
    fn.write(text)
    fn.close()
    return 0


def update_exec_status(cursor, sb_dat):
    sb_datB = np.copy(sb_dat)
    d = datetime.date.today() - datetime.timedelta(1)
    sql = "SELECT domain_entity_id from ALMA.state_changes " \
          "where timestamp >= to_date('%s', 'YYYY-MM-DD') " % d.isoformat()
    cursor.execute(sql)
    entries = cursor.fetchall()
    for s in sb_datB:
        if (s['schedUid'],) in entries:
            qa0_pass, qa0_fail, qa0_wait, status = readEPT.count_exec_status(cursor, s['schedUid'])
            s['sbStatus'] = status
            s['QA0_Pass'] = qa0_pass
            s['QA0_Fail'] = qa0_fail
            s['QA0_Wait'] = qa0_wait
        else:
            continue
    return sb_datB


def getObsProjecInfo(pcode, cursor):
    sql = "select science_score, science_rank, science_grade, version from SCHEDULING_AOS.obsproject where code = '%s'" % pcode
    cursor.execute(sql)
    try:
        h = cursor.fetchall()[0]
    except:
        sql = "select science_score, science_rank, science_grade, version from SCHEDULING_AOS.obsproject where code = '%s'" % pcode
        cursor.execute(sql)
        try:
            h = cursor.fetchall()[0]
        except Exception, e:
            print "check project %s, not in the SCHEDULING_AOS (%s)" % (pcode, e)
            return -1, -1, 'Z', 0
    return h[0], h[1], h[2], h[3]


def calc_tau(pwv):
    fn = open('/users/aod/AIV/science/gWTO/pwvdatos.dat')
    #fn = open('/home/ignacio/Work/hplots2/src/gWTO/pwvdatos.dat')
    dat = pickle.load(fn)
    fn.close()
    values = np.float_(dat.dtype.names[1:])
    values.sort()
    for v in values:
        if pwv <= v:
            return dat[['freq', str(v)]]


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
        ra1 += 2 * ephem.pi

    return np.rad2deg(ra1), np.rad2deg(dec1)
