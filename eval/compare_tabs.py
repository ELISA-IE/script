import re
import sys
import argparse
import logging
import os
from collections import defaultdict


def read_tab(ptab):
    res = {}
    with open(ptab, 'r') as f:
        for line in f:
            tmp = line.rstrip('\n').split('\t')
            mention = tmp[2]
            mention = mention.replace('"', '')
            kbid = tmp[4]
            etype = tmp[5]
            mtype = tmp[6]
            m = re.match('(.+):(\d+)-(\d+)', tmp[3])
            docid = m.group(1)
            beg = int(m.group(2))
            end = int(m.group(3))
            if docid not in res:
                res[docid] = list()
            res[docid].append((mention, kbid, etype, beg, end))
    return res


def count(tab):
    n = 0
    for docid in tab:
        n += len(tab[docid])
    return n


def read_tab_m2t(ptab):
    m2t = {}
    with open(ptab, 'r') as f:
        for line in f:
            tmp = line.rstrip('\n').split('\t')
            mention = tmp[2]
            mention = mention.replace('"', '')
            kbid = tmp[4]
            etype = tmp[5]
            mtype = tmp[6]
            m = re.match('(.+):(\d+)-(\d+)', tmp[3])
            docid = m.group(1)
            beg = int(m.group(2))
            end = int(m.group(3))

            if mention not in m2t:
                m2t[mention] = {}
            if etype not in m2t[mention]:
                m2t[mention][etype] = 0
            m2t[mention][etype] += 1
    return m2t


def read_dic(pdic):
    RE_STRIP = r' \([^)]*\)|\<[^)]*\>|,|"|\.|\'|:|-'
    res = defaultdict(lambda : defaultdict(int))
    with open(pdic, 'r') as f:
        for line in f:
            src, trg = line.rstrip('\n').split('\t')
            # trg = ' '.join(re.sub(RE_STRIP, '', trg).strip().split())
            res[src][trg] += 1
    for i in res:
        res[i] = [x for x, y in sorted(res[i].items(),
                                       key=lambda x: x[1], reverse=True)]
    return res


def count_mention(mention):
    n = 0
    for t in mention:
        n += mention[t]
    return n


if __name__ == '__main__':
    logger = logging.getLogger()
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
    logging.root.setLevel(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('pa', type=str, help='path to tab a')
    parser.add_argument('pb', type=str, help='path to tab b')
    parser.add_argument('outdir', type=str, help='output dir')
    args = parser.parse_args()

    try:
        os.mkdir(args.outdir)
    except FileExistsError:
        pass

    tab_a = read_tab(args.pa)
    tab_b = read_tab(args.pb)

    logger.info('a: %s' % args.pa)
    logger.info('b: %s' % args.pb)
    logger.info('# docs:')
    logger.info('a: %s' % len(tab_a))
    logger.info('b: %s' % len(tab_b))
    logger.info('# tagged names:')
    logger.info('a: %s' % count(tab_a))
    logger.info('b: %s' % count(tab_b))

    m2t_a = read_tab_m2t(args.pa)
    m2t_b = read_tab_m2t(args.pb)
    names_a = set(m2t_a.keys())
    names_b = set(m2t_b.keys())

    with open('%s/a-b' % args.outdir, 'w') as fw:
        fw.write('a - b: %s\n' % len(names_a - names_b))
        for i in sorted(names_a - names_b,
                        key=lambda x: count_mention(m2t_a[x]),
                        reverse=True):
            fw.write('%s\t%s\n' % (i, m2t_a[i]))

    with open('%s/b-a' % args.outdir, 'w') as fw:
        fw.write('b - a: %s\n' % len(names_b - names_a))
        for i in sorted(names_b - names_a,
                        key=lambda x: count_mention(m2t_b[x]),
                        reverse=True):
            fw.write('%s\t%s\n' % (i, m2t_b[i]))

    with open('%s/a' % args.outdir, 'w') as fw:
        for i in sorted(m2t_a,
                        key=lambda x: count_mention(m2t_a[x]),
                        reverse=True):
            fw.write('%s\t%s\n' % (i, m2t_a[i]))

    with open('%s/b' % args.outdir, 'w') as fw:
        for i in sorted(m2t_b,
                        key=lambda x: count_mention(m2t_b[x]),
                        reverse=True):
            fw.write('%s\t%s\n' % (i, m2t_b[i]))

    for i in m2t_a:
        if i not in m2t_b:
            m2t_b[i] = {}
    for i in m2t_b:
        if i not in m2t_a:
            m2t_a[i] = {}
    with open('%s/ab' % args.outdir, 'w') as fw:
        fw.write('mention\tref\tsys\n')
        for i in sorted(m2t_a,
                        key=lambda x: \
                        count_mention(m2t_a[x])+count_mention(m2t_b[x]),
                        reverse=True):
            fw.write('%s\t%s\t%s\n' % (i, m2t_a[i], m2t_b[i]))
