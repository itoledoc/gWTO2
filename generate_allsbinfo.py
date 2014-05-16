array =['SEVEN-M', 'TWELVE-M', 'TP-Array']

for i in datas.projects.index:
    sched = datas.projects.ix[i].obsproj.assoc_sched_blocks()
    c = 0
    for s in sched:
        if s.__len__() == 0:
            c += 1
            continue
        for s2 in s:
	    sql = "SELECT SB_NAME, ARCHIVE_UID, RECEIVER_BAND, FREQUENCY, REQUESTEDARRAY FROM ALMA.BMMV_SCHEDBLOCK WHERE ARCHIVE_UID = '%s'" % s2
	    cursor.execute(sql)
	    datos = cursor.fetchall()[0]
	    print "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (i, datas.projects.ix[i].prj_uid, datos[0], datos[1], datos[2], datos[3], array[c], "OTHER", 100, 100, "C32-1,C32-2,C32-3,C32-4,C32-5,C32-6")
        c += 1
