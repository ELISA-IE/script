#-*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os
import xml.etree.ElementTree as ET

def laf2tab(laf):
    res = list()
    xobj = ET.parse(laf)
    xdoc = xobj.find('DOC')
    docid = xdoc.get('id')
    for xann in xdoc.findall('ANNOTATION'):
        annid = xann.get('id')
        task = xann.get('task')
        assert task == 'NE'
        anntype = xann.get('type')
        extent = xann.find("EXTENT")
        beg = extent.get('start_char')
        end = extent.get('end_char')
        head = extent.text
        tab = '%s\t%s\t%s\t%s:%s-%s\t%s\t%s\t%s\t%s\n'
        res.append(tab % ('GOLD', annid, head, docid, beg, end,
                          'NIL', anntype, 'NAM', '1.0'))
    return res

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'USAGE: python laf2tab.py <input dir> <output tab path>'
        sys.exit()
    else:
        indir = sys.argv[1]
        outpath = sys.argv[2]
        res = list()
        for i in os.listdir(indir):
            if i.endswith('.laf.xml'):
                try:
                    res += laf2tab('%s/%s' % (indir, i))
                except:
                    print 'Unexpected error %s: %s' % (i, sys.exc_info())
                    continue
        out = open(outpath, 'w')
        for i in res:
            out.write('%s\n' % i)
