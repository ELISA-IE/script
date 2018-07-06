import tweepy
import sys
import argparse
from collections import defaultdict
import os


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('pbio', type=str, help='path to bio')
    parser.add_argument('outdir', type=str, help='output dir')
    args = parser.parse_args()

    usernames = defaultdict(int)
    hashtags = defaultdict(int)
    with open(args.pbio, 'r') as f:
        for line in f:
            tmp = line.split()
            if not tmp:
                continue
            tok = tmp[0]
            if tok.startswith('@'):
                usernames[tok] += 1
            if tok.startswith('#'):
                hashtags[tok] += 1

    print('# of usernames: %s' % len(usernames))
    print('# of hastagss: %s' % len(hashtags))

    os.makedirs(args.outdir, exist_ok=True)
    with open('%s/usernmaes' % args.outdir, 'w') as fw:
        for i, c in sorted(usernames.items(), key=lambda x: x[1], reverse=True):
            fw.write('%s\t%s\thttps://twitter.com/%s\n' % (i, c, i[1:]))
    with open('%s/hashtags' % args.outdir, 'w') as fw:
        for i, c in sorted(hashtags.items(), key=lambda x: x[1], reverse=True):
            fw.write('%s\t%s\thttps://twitter.com/hashtag/%s\n' % (i, c, i[1:]))
