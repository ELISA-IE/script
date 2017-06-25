import argparse
import codecs
import xml.etree.ElementTree as ET
import os


def ltftab2bio(ltf_root, tab_str):
    res = []
    doc_tokens, doc_text, doc_id = load_ltf(ltf_root)
    labels = parse_label(tab_str)

    # check label offset
    for l in labels:
        try:
            mention, start_char, end_char, mention_type = l
            assert doc_text[start_char:end_char+1] == mention, \
                "mention offset error in %s %s" % (doc_id, l)
        except AssertionError as e:
            print(e)

    # create annotation mapping table
    label_offset_mapping = dict()
    for l in labels:
        start_char = l[1]
        end_char = l[2]
        for i in range(start_char, end_char + 1):
            label_offset_mapping[i] = l

    for i, sent_tokens in enumerate(doc_tokens):
        sent_res = []
        for token in sent_tokens:
            t_text = token[0]
            t_start_char = int(token[1])
            t_end_char = int(token[2])

            # get token bio tag
            tag = ''
            if t_start_char in label_offset_mapping.keys():
                entity_type = label_offset_mapping[t_start_char][3]
                if t_start_char == label_offset_mapping[t_start_char][1]:
                    tag = '%s-%s' % ('B', entity_type)
                else:
                    tag = '%s-%s' % ('I', entity_type)
            if not tag:
                tag = 'O'

            sent_res.append(' '.join([t_text,
                                      '%s:%d-%d' % (doc_id,
                                                    t_start_char,
                                                    t_end_char),
                                      tag]))

        res.append('\n'.join(sent_res))

    return '\n\n'.join(res)


def write2file(bio_str, bio_file):
    with codecs.open(bio_file, 'w', 'utf-8') as f:
        f.write(bio_str+'\n')


def load_ltf(ltf_root):
    doc_tokens = []
    doc_id = ltf_root.find('DOC').get('id')
    doc_text = ''
    prev_seg_end = 1
    for seg in ltf_root.find('DOC').find('TEXT').findall('SEG'):
        sent_tokens = []
        seg_text = seg.find('ORIGINAL_TEXT').text
        seg_start = int(seg.get('start_char'))
        seg_end = int(seg.get('end_char'))
        seg_id = seg.get('id')

        doc_text += '\n' * (seg_start - prev_seg_end - 1) + seg_text
        prev_seg_end = seg_end
        assert doc_text[seg_start:seg_end+1] == seg_text, \
            'seg offset error in %s-%s' % (doc_id, seg_id)

        for token in seg.findall('TOKEN'):
            token_id = token.get('id')
            token_text = token.text
            start_char = int(token.get('start_char'))
            end_char = int(token.get('end_char'))

            assert doc_text[start_char:end_char + 1] == token_text, \
                "token offset assertion error in %s-%s" % (doc_id, token_id)

            sent_tokens.append((token_text, start_char, end_char))
        doc_tokens.append(sent_tokens)

    return doc_tokens, doc_text, doc_id


def parse_label(tab_str):
    labels = []
    for line in tab_str.splitlines():
        try:
            line = line.strip()
            if not line:
                continue
            line = line.split('\t')
            mention = line[2]
            doc_id, offset = line[3].split(':')
            start_char, end_char = offset.split("-")
            mention_type = line[5]

            labels.append((mention, int(start_char),
                           int(end_char), mention_type))
        except:
            print("parse label error in %s" % line)

    return labels


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ltf")
    parser.add_argument("tab")
    parser.add_argument("bio_file")
    parser.add_argument("-d", action="store_true", default=False,
                        help="process directory")

    args = parser.parse_args()

    num_doc_added = 0
    if args.d:
        combined_bio = []
        for fn in os.listdir(args.ltf):
            try:
                if not fn.endswith(".ltf.xml"):
                    continue
                ltf_file = os.path.join(args.ltf, fn)
                tab_file = os.path.join(args.tab,
                                        fn.replace(".ltf.xml", '.tab'))
                if not os.path.exists(ltf_file) or not os.path.exists(tab_file):
                    continue

                ltf_root = ET.parse(ltf_file)
                tab_str = codecs.open(tab_file, 'r', 'utf-8').read()

                bio_str = ltftab2bio(ltf_root, tab_str)

                combined_bio.append(bio_str)

                num_doc_added += 1
            except AssertionError as e:
                print(e)

        write2file('\n\n'.join(combined_bio), args.bio_file)

        num_ltf_files = len([fn for fn in os.listdir(args.ltf)
                             if fn.endswith('.ltf.xml')])
        num_tab_files = len([fn for fn in os.listdir(args.tab)
                             if fn.endswith('.tab')])

    else:
        ltf_root = ET.parse(args.ltf)
        tab_str = codecs.open(args.tab, 'r', 'utf-8').read()

        bio_str = ltftab2bio(ltf_root, tab_str)

        write2file(bio_str, args.bio_file)

        num_doc_added = 1
        num_ltf_files = 1
        num_tab_files = 1

    print('%d ltf files parsed.' % num_ltf_files)
    print('%d tab files parsed.' % num_tab_files)
    print('%d documents added to bio.' % num_doc_added)



