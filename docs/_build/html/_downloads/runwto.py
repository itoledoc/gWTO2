__author__ = 'itoledo'


def runwto(pwv, array_name=None, d=None, num_ant=34):
    datas.query_arrays()
    if array_name == 'default':
        array_name = None
        datas.set_bl_prop(array_name)
    else:
        array_name = datas.bl_arrays.AV1.values[0]
        datas.set_bl_prop(array_name)
        datas.array_ar = 61800 / (100. * datas.ruv.max())
    if d == None:
        d = ephem.now()
    if num_ant != 34:
        datas.num_ant = num_ant
    datas.array_name = array_name
    datas.update()
    datas.date = d
    datas.pwv = pwv
    datas.selector('12m')
    datas.scorer('12m')
    print datas.score12m.sort(
        'score', ascending=False).query(
        'band != "ALMA_RB_04" and band '
        '!= "ALMA_RB_08" and isPolarization == False')[
        ['score','CODE','SB_UID','name','SB_state','band','maxPWVC', 'HA',
         'elev','etime', 'execount','Total','arrayMinAR','arcorr',
         'arrayMaxAR','tsysfrac', 'blfrac','frac','sb_array_score',
         'sb_cond_score', 'DEC','RA', 'isTimeConstrained',
         'integrationTime', 'PRJ_ARCHIVE_UID']].head(25)
    datas.num_ant_user = 34