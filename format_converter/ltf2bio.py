import codecs
import os
import argparse
import xml.etree.ElementTree as ET


def ltf2bio(ltf_str):
    doc_tokens = load_ltf(ltf_str)

    bio = []
    for sent in doc_tokens:
        sent_res = []
        for token in sent:
            t_text = token[0]
            if t_text is None:
                t_text = ''
            t_doc_id = token[1]
            t_start_char = int(token[2])
            t_end_char = int(token[3])

            # get token bio tag
            sent_res.append(' '.join([t_text,
                                      '%s:%s-%s' % (t_doc_id,
                                                    t_start_char,
                                                    t_end_char)]))
        bio.append('\n'.join(sent_res))

    return '\n\n'.join(bio)


def load_ltf(ltf_str):
    doc_tokens = []
    root = ET.fromstring(ltf_str)
    doc_id = root.find('DOC').get('id')
    for seg in root.find('DOC').find('TEXT').findall('SEG'):
        sent_tokens = []
        for token in seg.findall('TOKEN'):
            token_text = token.text
            start_char = token.get('start_char')
            end_char = token.get('end_char')
            sent_tokens.append((token_text, doc_id, start_char, end_char))
        doc_tokens.append(sent_tokens)

    return doc_tokens


def write2file(bio_str, out_file):
    with codecs.open(out_file, 'w', 'utf-8') as f:
        f.write(bio_str)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('ltf_dp', type=str,
                        help='ltf file directory path')
    parser.add_argument('output_fp', type=str,
                        help='output file path')
    parser.add_argument('--ltf_filelist_fp', type=str,
                        help='ltf filelist path')

    args = parser.parse_args()

    if args.ltf_filelist_fp:
        ltf_filelist = open(args.ltf_filelist_fp).read().splitlines()
        doc_ids = [item.replace('.ltf.xml', '')
                   for item in ltf_filelist]
    else:
        doc_ids = [item.replace('.ltf.xml', '')
                   for item in os.listdir(args.ltf_dp) if 'ltf' in item]

    res = []
    for d_id in doc_ids:
        ltf_fp = os.path.join(args.ltf_dp, d_id+'.ltf.xml')
        assert os.path.exists(ltf_fp)

        ltf_str = codecs.open(ltf_fp, 'r', 'utf-8').read()
        res.append(ltf2bio(ltf_str))

    write2file('\n\n'.join(res), args.output_fp)

    print('%d files converted.' % len(res))
