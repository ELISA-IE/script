#-*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import sys
import os
from bs4 import BeautifulSoup

def laf2tab(xml, out):
    soup = BeautifulSoup(open(xml).read(), 'html.parser')
    docid = soup.doc['id']
    for ann in soup.find_all('annotation'):
        try:
            ann_type = ann['type']  # LDC laf format.
        except KeyError:
            ann_type = ann.tag.string  # LDC CRF tagger format

        if ann_type not in ['PER', 'ORG', 'LOC']:
            continue

        tab = '%s\t%s\t%s\t%s:%s-%s\t%s\t%s\t%s\t%s\n'
        out.write(tab % ('GOLD', ann['id'], ann.extent.string, docid,
                         ann.extent['start_char'], ann.extent['end_char'],
                         'NIL', ann_type, 'NAM', '1.0'))

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'USAGE: python laf2tab.py <input dir> <output dir>'
    else:
        indir = sys.argv[1]
        outdir = sys.argv[2]
        out = open(outdir, 'w')
        for i in os.listdir(indir):
            if i.endswith('.laf.xml'):
                laf2tab('%s/%s' % (indir, i), out)
