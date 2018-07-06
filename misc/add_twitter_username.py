import tweepy
import sys
import argparse
from collections import defaultdict


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('pkey', type=str, help='path to api key')
    parser.add_argument('inpath', type=str, help='path to inpath')
    # parser.add_argument('outpath', type=str, help='path to output')
    args = parser.parse_args()

    key = open(args.pkey).read().split('\n')
    assert len(key) == 4
    consumer_key, consumer_secret, access_token, access_token_secret = key

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    n = 0
    outpath = args.inpath + '.name'
    with open(outpath, 'w') as fw:
        with open(args.inpath, 'r') as f:
            for line in f:
                tmp = line.rstrip('\n').split('\t')
                userid = tmp[0][1:]
                name = ''
                try:
                    user = api.get_user(userid.rstrip('…|,|:'))
                    name = user.name
                    n += 1
                except Exception as e:
                    print(userid, e)
                tmp.append(name)
                fw.write('\t'.join(tmp) + '\n')

    print('found %s pairs' % n)
