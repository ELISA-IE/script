import sys
import re
import logging
from collections import defaultdict


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('USAGE: <path to bio>')
        exit()

    logger = logging.getLogger()
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
    logging.root.setLevel(level=logging.INFO)

    inpath = sys.argv[1]
    data = re.split('\n\s*\n', open(inpath).read())
    tag_count = defaultdict(int)
    mention_count = defaultdict(int)
    docids = set()
    for i in data:
        prev_beg = 0
        prev_end = 0
        sent = i.split('\n')
        for line in sent:
            if not line:
                continue
            try:
                assert not line.startswith(' ')
            except AssertionError:
                logger.info('line starts with space:')
                logger.info(repr(line))

            ann = line.split(' ')
            try:
                assert len(ann) >= 2
            except AssertionError:
                logger.info('line is less than two columns')
                logger.info(repr(line))

            tok = ann[0]
            tag = ann[-1]
            if len(ann) > 2:
                offset = ann[1]
                m = re.match('(.+):(\d+)-(\d+)', offset)
                docid = m.group(1)
                docids.add(docid)
                beg = int(m.group(2))
                end = int(m.group(3))
                try:
                    assert end >= beg
                except AssertionError:
                    logger.info('end is less than beg')
                    logger.info(repr(line))

                try:
                    assert beg > prev_end
                except AssertionError:
                    logger.info('beg is less than the previous end')
                    logger.info(repr(line))
            tag_count[tag] += 1

    logger.info('# of docs: %s' % (len(docids)))
    logger.info('# of sentences: %s' % (len(data)))
    logger.info('tag stats:')
    for t, c in sorted(tag_count.items(), key=lambda x: x[0], reverse=True):
        logger.info('    %s: %s' % (t, c))
    logger.info('done.')
