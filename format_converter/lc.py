import sys


if __name__ == '__main__':
    inpath = sys.argv[1]
    outpath = inpath + '.lc'

    with open(outpath, 'w') as fw:
        fw.write(open(inpath).read().lower())
