__author__ = 'itoledo'
from lxml import objectify
import pandas as pd
prj = '{Alma/ObsPrep/ObsProject}'

'''
obsprojects = datas.projects.obsproj.values
for i in obsprojects:
    sb = i.assoc_sched_blocks()
    if sb is None:
        continue
    for k in sb.keys():
        bl = sb[k][0]
        if len(bl) == 0:
            continue
        rp.get_schedblocks(bl)


sgoals = conf_table.SG_ID.tolist()
for sg in sgoals:
    q = conf_table.query('SG_ID == sg')
    if len(q) != 2:
        continue
    ar = []
    for i in q.index.tolist():
        ar.append(q.ix[i, 'minAR'])
    if ar[0] != ar[1]:
        conf_table.ix[q.ix[q.index.tolist()[0], 'SB_UID'], 'sb12m'] = 2
        conf_table.ix[q.ix[q.index.tolist()[1], 'SB_UID'], 'sb12m'] = 2

'''


def configuration_check(datas):
    codes = datas.projects.index.tolist()
    c = 0
    ok = False
    while not ok:
        start = codes[c]
        sbs_start = datas.projects.ix[start, 'obsproj'].assoc_sched_blocks()
        if len(sbs_start) == 0:
            ok = False
            c += 1
            continue
        for k in sbs_start.keys():
            if len(sbs_start[k][0]) == 0:
                ok = False
                continue
            ok = True
        if not ok:
            c += 1

    sgoalids = sbs_start.keys()
    first = True
    for sgoalid in sgoalids:
        if len(sbs_start[sgoalid][0]) == 0:
            continue
        sblist = sbs_start[sgoalid][0]
        for sb in sblist:
            row = get_data(sgoalid, sb,
                           obspro=datas.projects.ix[start, 'obsproj'])
            print row
            if first:
                conf_table = pd.DataFrame(
                    [row],
                    columns=['CODE', 'SG_ID', 'prj_status', 'arraySB', 'SB_UID',
                             'sb_name', 'AR', 'LAS', 'repFreqSG', 'repFreqSB',
                             'useACA', 'sb12m','minAR', 'maxAR'],
                    index=[sb])
                print conf_table
                first = False
            else:
                conf_table.loc[sb] = row
                print conf_table

    for code in codes[c+1:]:
        sbs = datas.projects.ix[code, 'obsproj'].assoc_sched_blocks()
        sgoalids = sbs.keys()
        for sgoalid in sgoalids:
            if len(sbs[sgoalid][0]) == 0:
                continue
            sblist = sbs[sgoalid][0]
            for sb in sblist:
                row = get_data(sgoalid, sb,
                               obspro=datas.projects.ix[code, 'obsproj'])
                if row is None:
                    continue
                conf_table.loc[sb] = row

    return conf_table.query('arraySB == "TWELVE-M"')


def get_data(sgoalid, sb, obspro, path='./'):

    try:
        for sg in obspro.ObsProgram.ScienceGoal:
            if sg.ObsUnitSetRef.attrib['partId'] == sgoalid:
                scgoal = sg
    except AttributeError:
        print obspro.ObsProgram.base
        return None

    io_file = open(path + sb.replace('://', '___').replace('/', '_') + '.xml')
    tree = objectify.parse(io_file)
    schedblock = tree.getroot()
    io_file.close()

    arraySb = schedblock.findall(
        './/' + prj + 'ObsUnitControl')[0].attrib['arrayRequested']
    sb_uid = schedblock.SchedBlockEntity.attrib['entityId']
    sb_name = schedblock.findall('.//' + prj +'name')[0].pyval
    AR = scgoal.PerformanceParameters.desiredAngularResolution.pyval
    LAS = scgoal.PerformanceParameters.desiredLargestScale.pyval
    repFreqSG = scgoal.PerformanceParameters.representativeFrequency.pyval
    repFreqSB = schedblock.SchedulingConstraints.representativeFrequency.pyval
    useACA = scgoal.PerformanceParameters.useACA.pyval
    sb12m = 1
    minAR = schedblock.SchedulingConstraints.minAcceptableAngResolution.pyval
    maxAR = schedblock.SchedulingConstraints.maxAcceptableAngResolution.pyval

    return (obspro.code.pyval, sgoalid, obspro.status, arraySb, sb_uid, sb_name,
            AR, LAS, repFreqSG, repFreqSB, useACA, sb12m, minAR, maxAR)

