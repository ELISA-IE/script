import argparse
import codecs


def bio2dat(bio_str):
    dat = []
    for sent in bio_str.strip().split('\n\n'):
        if not sent.strip():
            continue
        tokens = [line.split()[0] for line in sent.strip().splitlines()]
        dat.append(' '.join(tokens))

    return '\n'.join(dat)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('bio_file')
    parser.add_argument('dat_file')
    parser.add_argument('--lower', action='store_true',
                        help='lowercase')
    args = parser.parse_args()

    bio_str = codecs.open(args.bio_file, 'r', 'utf-8').read()

    dat = bio2dat(bio_str)
    if args.lower:
        dat = dat.lower()

    with open(args.dat_file, 'w') as f:
        f.write(dat)
