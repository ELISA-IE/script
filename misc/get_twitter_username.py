import tweepy
import sys
import argparse
from collections import defaultdict


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('pkey', type=str, help='path to api key')
    parser.add_argument('inpath', type=str, help='path to inpath')
    parser.add_argument('outpath', type=str, help='path to output')
    args = parser.parse_args()

    key = open(args.pkey).read().split('\n')
    assert len(key) == 4
    consumer_key, consumer_secret, access_token, access_token_secret = key

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    usernames = defaultdict(int)
    with open(args.inpath, 'r') as f:
        for line in f:
            tmp = line.split()
            if not tmp:
                continue
            tok = tmp[0]
            if tok.startswith('@'):
                usernames[tok] += 1

    print('# of usernames: %s' % len(usernames))
    n = 0
    with open(args.outpath, 'w') as fw:
        for i, c in sorted(usernames.items(), key=lambda x: x[1], reverse=True):
            username = i[1:]
            try:
                user = api.get_user(username.strip('…|,|:'))
            except Exception as e:
                print(username, e)
                continue
            n += 1
            fw.write('@%s\t%s\n' % (username, user.name))

    print('found %s pairs' % n)
