import readProjects as rp
import cx_Oracle
conx_strin = 'almasu/alma4dba@ALMA_ONLINE.OSF.CL'
connection = cx_Oracle.connect(conx_strin)
cursor = connection.cursor()


list10 = ["2013.1.00033.S", "2013.1.00034.S", "2013.1.00088.S", "2013.1.00159.S", "2013.1.00170.S", "2013.1.00293.S",
          "2013.1.00437.S", "2013.1.00468.S", "2013.1.00526.S", "2013.1.00668.S", "2013.1.00803.S", "2013.1.00861.S",
          "2013.1.00879.S", "2013.1.00952.S", "2013.1.00976.S", "2013.1.00989.S", "2013.1.01194.S", "2013.1.01202.S",
          "2013.1.01312.S", "2013.1.01366.T", "2013.1.00099.S", "2013.1.00229.S", "2013.1.00280.S", "2013.1.00362.S",
          "2013.1.00366.S", "2013.1.00403.S", "2013.1.00487.S", "2013.1.00518.S", "2013.1.00524.S", "2013.1.00663.S",
          "2013.1.00815.S", "2013.1.00828.S", "2013.1.00988.S", "2013.1.01035.S", "2013.1.01113.S", "2013.1.01268.S"]

array = ['SEVEN-M', 'TWELVE-M', 'TP-Array']
confarray = [' ', 'C34', ' ']

datas = rp.DataBase(list10)

for i in datas.projects.index:
    sched = datas.projects.ix[i].obsproj.assoc_sched_blocks()
    c = 0
    for s in sched:
        if s.__len__() == 0:
            c += 1
            continue
        for s2 in s:
            sql = "SELECT SB_NAME, ARCHIVE_UID, RECEIVER_BAND, FREQUENCY, " \
                  "REQUESTEDARRAY FROM ALMA.BMMV_SCHEDBLOCK " \
                  "WHERE ARCHIVE_UID = '%s'" % s2
            cursor.execute(sql)
            datos = cursor.fetchall()[0]
            print "%s\t%s\t%s\t%s\t%s\t%.2f\t%s\t%s\t%s\t%s\t%s" % \
                  (i, datas.projects.ix[i].PRJ_ARCHIVE_UID, datos[0], datos[1],
                   datos[2], float(datos[3]), array[c], "OTHER", 100, 100,
                   confarray[c])
        c += 1

connection.close()