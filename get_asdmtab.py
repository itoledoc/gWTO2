#!/usr/bin/env python
__author__ = 'itoledo'

import numpy as np
import pandas as pd
import optparse
import asdmCal as Cal
c = Cal.open_conn()
import DataBase as DaB

import os
import shutil


def main():

    usage = "usage: %prog arg1 [options]\n\targ1 must be the EB uid"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(
        '-c', '--clean', dest='clean', default=False, action='store_true',
        help="Force clean up of APA QA0 cache")
    parser.add_option('-p', '--path', default='/.wto',
                      help="Path for cache")
    (options, args) = parser.parse_args()

    if len(args) == 0:
        print("Please specify EB UID")
        return None
    uid = args[0]

    datas = DaB.Database(verbose=False, forcenew=options.clean, path='/.qa0')
    datas.process_sbs()
    datas.do_summarize_sb()

    caldata = Cal.query_last_day(c).sort('TIME', ascending=False)
    eb = caldata.groupby('UID').agg(
        {'SCAN': np.max, 'TIME': np.min}).sort('TIME', ascending=False)
    eb.columns = pd.Index(['START_TIME', u'NUM_SCAN'], dtype='object')
    eb.index.name = 'EB_UID'
    slt = Cal.query_stl(c, '2015-05-15 00:00:00')
    slt_eb = pd.merge(
        eb, slt[
            ['SE_ID', 'SE_SUBJECT', 'SE_PROJECT_CODE', 'SE_SB_ID', 'SE_EB_UID',
             'SE_STATUS', 'SE_ARRAYENTRY_ID', 'SE_SB_CODE']],
        left_index=True, right_on='SE_EB_UID')
    slt_eb = pd.merge(
        slt_eb, slt[
            ['SE_ID', 'SE_ARRAYNAME', 'SE_ARRAYTYPE', 'SE_ARRAYFAMILY',
             'SE_CORRELATORTYPE']],
        left_on='SE_ARRAYENTRY_ID', right_on='SE_ID')
    slt_eb = slt_eb.set_index('SE_EB_UID', drop=False)[
        ['SE_EB_UID', 'START_TIME', 'NUM_SCAN', 'SE_STATUS', 'SE_SB_ID',
         'SE_SB_CODE', 'SE_PROJECT_CODE', 'SE_ARRAYNAME', 'SE_ARRAYFAMILY',
         'SE_CORRELATORTYPE', 'SE_ID_y', 'SE_SUBJECT']
    ].sort('START_TIME', ascending=False)

    print slt_eb
    print slt_eb.query('SE_EB_UID == @uid')
    timeu = slt_eb.ix[uid, 'START_TIME']
    tmjd = timeu.strftime('%Y-%m-%dT%H:%M:%S.%s')
    point_eb = Cal.query_point(c, uid, q1=True)
    dfph = Cal.query_phase(c, uid)
    dfatm = Cal.query_atm(c, uid)
    dfant = Cal.query_antennas(c, uid)
    dfflag = Cal.query_flags(c, uid)
    dfflag.delta = dfflag.apply(lambda x: x['delta'].total_seconds(), axis=1)
    dfscan = Cal.query_scans(c, uid)
    # dfsta = Cal.query_station(c, uid)
    dfsubs = Cal.query_subscans(c, uid)
    dffoc = Cal.query_focus(c, tmjd)
    dfdel = Cal.query_delay(c, tmjd)
    dfield = Cal.query_field(c, uid)
    dfmain = Cal.query_main(c, uid)
    dfwvr = Cal.query_wvr(c, uid)
    dfcal = Cal.query_caldata(c, uid)
    ssys = ['Mars', 'Venus', 'Jupiter', 'Uranus', 'Neptune', 'Titan', 'Ceres',
            'Ganymede', 'Callisto', 'Pallas']
    calamp = dfscan.query(
        "SCAN_INTENT in ['CALIBRATE_AMPLITUDE', 'CALIBRATE_AMPLI'] "
        "and FIELD_NAME not in @ssys").FIELD_NAME.unique()

    if len(calamp) > 0:
        cou = 0
        for ca in calamp:
            sql_names = 'SELECT * FROM sourcecatalogue.names WHERE ' \
                        'SOURCE_NAME = \'%s\'' % ca
            c.execute(sql_names)
            names = pd.DataFrame(
                c.fetchall(),
                columns=[rec[0] for rec in c.description])

            name_id = names.NAME_ID.values[0]

            sql_sourcename = 'SELECT * FROM sourcecatalogue.source_name ' \
                             'WHERE NAME_ID = \'%s\'' % name_id
            c.execute(sql_sourcename)
            source_name = pd.DataFrame(
                c.fetchall(), columns=[rec[0] for rec in c.description])
            source_id = source_name.SOURCE_ID.values[0]
            c.execute('SELECT * FROM SOURCECATALOGUE.MEASUREMENTS WHERE '
                      'SOURCE_ID = \'%s\'' % source_id)
            measurements_df = pd.DataFrame(
                c.fetchall(),
                columns=[rec[0] for rec in c.description])
            if cou == 0:
                cal_amp = measurements_df.query('FREQUENCY < 1.40e11').sort(
                    'DATE_OBSERVED', ascending=False).head(1)
                cal_amp = cal_amp.append(
                    measurements_df.query('FREQUENCY > 2.00e11').sort(
                        'DATE_OBSERVED', ascending=False).head(1))
                cou = 1
            else:
                cal_amp = cal_amp.append(
                    measurements_df.query('FREQUENCY > 2.00e11').sort(
                        'DATE_OBSERVED', ascending=False).head(1))
                cal_amp = cal_amp.append(
                    measurements_df.query('FREQUENCY < 1.40e11').sort(
                        'DATE_OBSERVED', ascending=False).head(1))
    else:
        cal_amp = pd.DataFrame([(0,0)], columns=['MEASUREMENT_ID', 'CAT_ID'])
    dire = '_'.join(uid.split('/')[-2:])

    try:
        os.mkdir('/users/aod/data/' + dire)
    except OSError:
        shutil.rmtree('/users/aod/data/' + dire)
        os.mkdir('/users/aod/data/' + dire)

    point_eb[0].to_csv('/users/aod/data/' + dire + '/point_qa0.csv', index=False)
    antenas = dfant.ANTENNA.unique()
    point_eb[1].query('ANTENNA in @antenas').to_csv(
        '/users/aod/data/' + dire + '/point_qa1.csv', index=False)
    dfant.to_csv('/users/aod/data/' + dire + '/antennas.csv', index=False)
    try:
        dfph.to_csv('/users/aod/data/' + dire + '/phase.csv', index=False)
    except:
        print("No Phase DATA. FAIL this SB if there wasn't actually any "
              "phase data")

    dfwvr.to_csv('/users/aod/data/' + dire + '/wvr.csv', index=False)
    try:
        dfscan.to_csv('/users/aod/data/' + dire + '/scan.csv', index=False)
    except:
        print("No scan data! Can't perform QA0 for you in EB %s, sorry!!" % uid)

    dfatm.to_csv('/users/aod/data/' + dire + '/atmosphere.csv', index=False)
    dfdel.query('ANTENNA in @antenas').to_csv(
        '/users/aod/data/' + dire + '/delay.csv', index=False)
    dfmain.to_csv('/users/aod/data/' + dire + '/main.csv', index=False)
    dfield.to_csv('/users/aod/data/' + dire + '/field.csv', index=False)
    dffoc.query('ANTENNA in @antenas').to_csv(
        '/users/aod/data/' + dire + '/focus.csv', index=False)
    dfsubs.to_csv('/users/aod/data/' + dire + '/subscans.csv', index=False)
    dfflag.to_csv('/users/aod/data/' + dire + '/flags.csv', index=False)
    dfcal.to_csv('/users/aod/data/' + dire + '/caldata.csv', index=False)
    slt_eb.query('SE_EB_UID == @uid').to_csv(
        '/users/aod/data/' + dire + '/slt.csv', index=False)
    sbuid = slt_eb.query('SE_EB_UID == @uid').SE_SB_ID.values[0]
    datas.summary_sb.query("SB_UID == @sbuid").to_csv(
        '/users/aod/data/' + dire + '/sbsum.csv', index=False)
    scpar = datas.scienceparam.query('SB_UID == @sbuid').paramRef.unique()
    otar = datas.orederedtar.query('SB_UID == @sbuid').targetId.unique()
    tar = datas.target.query(
        'SB_UID == @sbuid and paramRef in @scpar and targetId in @otar'
    ).fieldRef.unique()
    pd.merge(datas.fieldsource.query(
        'SB_UID == @sbuid and @tar in fieldRef'),
        datas.target.query(
            'SB_UID == @sbuid and paramRef in @scpar and targetId in @otar'
        )[['fieldRef', 'paramRef']], on='fieldRef').to_csv(
        '/users/aod/data/' + dire + '/fieldsource.csv', index=False)
    datas.scienceparam.query('SB_UID == @sbuid').to_csv(
        '/users/aod/data/' + dire + '/scienceparam.csv', index=False)
    cal_amp.to_csv('/users/aod/data/' + dire + '/cal_amp.csv', index=False)

    uidout = uid.replace('uid://A002/','').replace('/','_')

    os.system("sed \'s/^dire.*/dire <- \"%s\/\"/g\' /users/aod/data/QAOrep.Rmd > /users/aod/data/QA0rep.Rmd" % uidout)
    os.system("Rscript -e \"library(knitr); knit(\'/users/aod/data/QA0rep.Rmd\', output=\'/users/aod/data/QA0rep.md\')\"")
    os.system('/usr/lib/rstudio-server/bin/pandoc/pandoc /users/aod/data/QA0rep.md --to latex --from markdown+autolink_bare_uris+ascii_identifiers+tex_math_single_backslash --output /users/aod/data/QA0rep.tex --template /data1/home/aod/R/x86_64-redhat-linux-gnu-library/3.1/rmarkdown/rmd/latex/default.tex --number-sections --highlight-style tango --latex-engine pdflatex')
    os.system('/usr/lib/rstudio-server/bin/pandoc/pandoc /users/aod/data/QA0rep.md --to latex --from markdown+autolink_bare_uris+ascii_identifiers+tex_math_single_backslash --output /users/aod/data/QA0rep.pdf --template /data1/home/aod/R/x86_64-redhat-linux-gnu-library/3.1/rmarkdown/rmd/latex/default.tex --number-sections --highlight-style tango --latex-engine pdflatex')

if __name__ == '__main__':
    main()
