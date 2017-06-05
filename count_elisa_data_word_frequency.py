#!/usr/bin/env python3
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import gzip
from lxml import etree
from collections import defaultdict
import sys


def process(pdata, outpath):
    res = defaultdict(int)
    data = gzip.open(pdata, 'rb')
    context = etree.iterparse(data, events=('end',),
                              tag='LRLP_TOKENIZED_SOURCE')
    for event, elem in context:
        toks = elem.text.split()
        for tok in toks:
            res[tok] += 1

        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    del context

    out = open(outpath, 'w')
    for w, c in sorted(res.items(), key=lambda x: x[1], reverse=True):
        out.write('%s\t%s\n' % (w, c))
    out.close()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('USAGE: <path to elisa.*.xml.gz> <output path>')
        exit()

    pdata = sys.argv[1]
    outpath = sys.argv[2]
    process(pdata, outpath)
