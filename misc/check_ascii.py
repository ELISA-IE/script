import re
import string
import sys
import argparse
from collections import defaultdict


def is_ascii(s):
    return all(ord(c) < 128 for c in s)


def is_valid(s):
    pattern = re.compile("[\d{}]+$".format(re.escape(string.punctuation)))
    if pattern.match(s):
        return False
    if re.search('http', s):
        return False
    if re.search('.+\.jpg', s):
        return False
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('pbio', type=str, help='path to input bio')
    parser.add_argument('outpath', type=str, help='outpath path')
    args = parser.parse_args()

    count = defaultdict(int)
    with open(args.pbio, 'r') as f:
        for line in f:
            tmp = line.rstrip('\n').split(' ')
            if len(tmp) == 1:
                continue
            tok = tmp[0]
            if is_ascii(tok) and is_valid(tok):
                count[tok] += 1

    for i in sorted(count.items(), key=lambda x: x[1], reverse=True):
        print(i)
