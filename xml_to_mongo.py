__author__ = 'itoledo'


def uyuy(r, l1=dict()):
    l = l1
    for d in r.iterchildren():
        if d.countchildren() > 0:
            if len(d) > 1:
                l[d.tag.split('}')[1]] = []
                for c in range(len(d)):
                    temp = {}
                    if len(d[c].attrib) > 0:
                        for a in d[c].attrib:
                            temp[a] = d[c].attrib[a]
                    l[d.tag.split('}')[1]].append(uyuy(d[c], temp))
            else:
                temp = {}
                if len(d.attrib) > 0:
                    for a in d.attrib:
                        temp[a] = d.attrib[a]
                l[d.tag.split('}')[1]] = uyuy(d, temp)
        else:
            l[d.tag.split('}')[1]] = d.pyval
            if len(d.attrib) > 0:
                for a in d.attrib:
                    l[d.tag.split('}')[1] + '_' + a] = d.attrib[a]

    return l


for k in t.keys():
    if (('Param' in k) and ('expert' not in k)) or (k in ['SpectralSpec', 'ObservingGroup', 'FieldSource', 'Target']):
        if type(t[k]) == type(list()):
            for c in t[k]:
                db[k].insert(c)
            t.pop(k)
        else:
            db[k].insert(c)
            t.pop(k)
db['sb'].insert(t)

for f in lx:
    print f
    io_file = open('/home/itoledo/.wto/sbxml/' + f, 'r')
    tree = objectify.parse(io_file)
    io_file.close()
    data = tree.getroot()

    t = {}
    t = uyuy(data, {})
    for k in t.keys():
        if (('Param' in k) and ('expert' not in k)) or (k in ['SpectralSpec', 'ObservingGroup', 'FieldSource', 'Target']):
            if type(t[k]) == type(list()):
                for c in t[k]:
                    db[k].insert(c)
                t.pop(k)
            else:
                db[k].insert(c)
                t.pop(k)
    print db['sb'].insert(t)
