import re
import sys
import argparse
import logging
import os
from collections import defaultdict
import lxml.etree as ET


logger = logging.getLogger()
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
logging.root.setLevel(level=logging.INFO)


def read_tab(ptab):
    res = defaultdict(list)
    with open(ptab, 'r') as f:
        for line in f:
            tmp = line.rstrip('\n').split('\t')
            mention = tmp[2]
            kbid = tmp[4]
            etype = tmp[5]
            mtype = tmp[6]
            m = re.match('(.+):(\d+)-(\d+)', tmp[3])
            docid = m.group(1)
            beg = int(m.group(2))
            end = int(m.group(3))
            res[docid].append((beg, end))
    return res


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('ptab', type=str, help='path to tab')
    parser.add_argument('ltf_dir', type=str, help='ltf dir')
    args = parser.parse_args()

    tab = read_tab(args.ptab)
    logger.info('# of docs: %s' % len(tab))
    logger.info('checking offset...')
    n = 0
    for docid in tab:
        path = '%s/%s.ltf.xml' % (args.ltf_dir, docid)
        root = ET.parse(path)
        assert root.find('DOC').get('id') == docid
        begs = set()
        ends = set()
        for seg in root.find('DOC').find('TEXT').findall('SEG'):
            for tok in seg.findall('TOKEN'):
                begs.add(int(tok.get('start_char')))
                ends.add(int(tok.get('end_char')))
        for beg, end in tab[docid]:
            assert beg in begs
            assert end in ends
            n += 1
    logger.info('%s mentions checked' % n)
