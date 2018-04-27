import argparse
import codecs
import xml
import xml.etree.ElementTree as ET
import os


def ltflaf2bio(ltf_root, laf_root):
    res = []
    doc_tokens, doc_text, doc_id = load_ltf(ltf_root)
    labels = load_laf(laf_root)

    # check label offset
    for l in labels:
        try:
            mention, start_char, end_char, mention_type = l
            assert doc_text[start_char:end_char+1] == mention, \
                "mention offset error in %s %s" % (doc_id, l)
        except AssertionError as e:
            counter['mention_offset_error'] += 1
            print(e)

    # create annotation mapping table
    label_offset_mapping = dict()
    for l in labels:
        start_char = l[1]
        end_char = l[2]
        for i in range(start_char, end_char + 1):
            label_offset_mapping[i] = l

    #
    # add label to bio
    #
    b_tags = set()
    for i, sent_tokens in enumerate(doc_tokens):
        sent_res = []

        retok_sent_tokens = []

        # re-tokenize token based on labels in tab
        for token in sent_tokens:
            t_text = token[0]
            t_start_char = int(token[1])
            t_end_char = int(token[2])

            char_labels = []
            for t_char in range(t_start_char, t_end_char + 1):
                if t_char not in label_offset_mapping:
                    char_labels.append('O')
                if t_char in label_offset_mapping:
                    char_labels.append(label_offset_mapping[t_char])

            char_index = []
            current_char_index = []
            current_label = None
            for j, char_label in enumerate(char_labels):
                if char_label != current_label:
                    if current_char_index:
                        char_index.append(current_char_index)
                    current_char_index = [j]
                    current_label = char_label
                elif char_label == current_label:
                    current_char_index.append(j)
                if j == len(char_labels)-1:
                    char_index.append(current_char_index)

            retok_tokens = []
            for index in char_index:
                start = t_start_char + index[0]
                end = t_start_char + index[-1]
                text = t_text[start-t_start_char:end-t_start_char+1]
                assert doc_text[start:end+1] == text, 'retok token offset error'
                retok_tokens.append((text, start, end))

            assert ''.join([item[0] for item in retok_tokens]) == t_text, \
                'join of retok tokens not match original text in %s-%d' % \
                (doc_id, i)

            retok_sent_tokens += retok_tokens

            if len(char_index) > 1:
                counter['num_retok_token'] += 1

        # add label to bio
        for j, token in enumerate(retok_sent_tokens):
            t_text = token[0]
            t_start_char = int(token[1])
            t_end_char = int(token[2])

            # get token bio tag
            if t_start_char in label_offset_mapping.keys():
                entity_type = label_offset_mapping[t_start_char][3]
                if t_start_char == label_offset_mapping[t_start_char][1] or j == 0:
                    tag = '%s-%s' % ('B', entity_type)
                    b_tags.add(t_start_char)
                else:
                    tag = '%s-%s' % ('I', entity_type)
            else:
                tag = 'O'

            sent_res.append(' '.join([t_text,
                                      '%s:%d-%d' % (doc_id,
                                                    t_start_char,
                                                    t_end_char),
                                      tag]))

        res.append('\n'.join(sent_res))

    if len(b_tags) != len(labels):
        print('number of B tags and number of labels do not match in %s (%d/%d)'
              % (doc_id, len(b_tags), len(labels)))
        for l in labels:
            start = l[1]
            if start not in b_tags:
                print('  %s %d-%d' % (l[0], l[1], l[2]))

    counter['num_b_tag'] += len(b_tags)

    return '\n\n'.join(res)


def write2file(bio_str, bio_file):
    with codecs.open(bio_file, 'w', 'utf-8') as f:
        f.write(bio_str+'\n')


def load_ltf(ltf_root):
    doc_tokens = []
    doc_id = ltf_root.find('DOC').get('id')
    doc_text = ''
    prev_seg_end = -1
    for seg in ltf_root.find('DOC').find('TEXT').findall('SEG'):
        sent_tokens = []
        seg_text = seg.find('ORIGINAL_TEXT').text
        # ignore empty sentence
        if not seg_text:
            continue
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
            if not token_text.strip():
                continue
            start_char = int(token.get('start_char'))
            end_char = int(token.get('end_char'))

            assert doc_text[start_char:end_char + 1] == token_text, \
                "token offset assertion error in %s-%s" % (doc_id, token_id)

            sent_tokens.append((token_text, start_char, end_char))
        doc_tokens.append(sent_tokens)

    return doc_tokens, doc_text, doc_id


def load_laf(laf_root):
    labels = []
    if not laf_root:
        return labels

    num_overlap_label = 0
    doc_id = ''
    char_offset = set()
    for ann in laf_root.find('DOC').findall('ANNOTATION'):
        try:
            task = ann.get('task')
            if task and task != 'NE':
                continue
            extent = ann.find('EXTENT')
            mention = extent.text
            doc_id = laf_root.find('DOC').get('id')
            start_char = int(extent.get('start_char'))
            end_char = int(extent.get('end_char'))
            mention_type = ann.get('type')
            if not mention_type:
                mention_type = ann.find('TAG').text

            # check overlap labels
            overlapped_chars = char_offset.intersection(
                set(range(start_char, end_char + 1))
            )

            # pick the longest name if there are overlapped labels.
            if overlapped_chars:
                num_overlap_label += 1
                for i, l in enumerate(labels):
                    if not set(range(l[1], l[2] + 1)).intersection(
                            overlapped_chars):
                        continue
                    if l[2] - l[1] + 1 < end_char - start_char + 1:
                        tmp = (mention, start_char, end_char, mention_type)
                        labels[i] = tmp
                        char_offset = char_offset.union(
                            set(range(start_char,
                                      end_char + 1)))
                continue
            else:
                char_offset = char_offset.union(set(range(start_char,
                                                          end_char + 1)))

            labels.append((mention, start_char, end_char, mention_type))

            counter['num_labels'] += 1
        except Exception as e:
            print(e, "; parse label error in %s" % doc_id)

    if num_overlap_label:
        print('%d overlapped labels found in %s' % (num_overlap_label, doc_id))

    # make sure each entry is unique
    labels = set(labels)

    # check overlap labels again
    assert len(set([l[1] for l in labels])) == len(labels), \
        'overlap name found in parsed names.'

    return labels


counter = dict()
counter['num_labels'] = 0
counter['num_b_tag'] = 0
counter['num_retok_token'] = 0
counter['mention_offset_error'] = 0
counter['num_doc_added'] = 0
counter['num_ltf_files'] = 0
counter['num_laf_files'] = 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ltf")
    parser.add_argument("laf")
    parser.add_argument("bio_file")
    parser.add_argument("-d", action="store_true", default=False,
                        help="the ltf and laf are directory path")

    args = parser.parse_args()

    if args.d:
        combined_bio = []
        ltf_files = [fn for fn in os.listdir(args.ltf) if fn.endswith('.ltf.xml')]
        laf_files = [fn for fn in os.listdir(args.laf) if fn.endswith('.laf.xml')]
        counter['num_ltf_files'] = len(ltf_files)
        counter['num_laf_files'] = len(laf_files)
        valid_docid = []
        for fn in ltf_files:
            docid = fn.replace('.ltf.xml', '')
            if docid + '.laf.xml' in laf_files:
                valid_docid.append(docid)

        for docid in valid_docid:
            try:
                ltf_file = os.path.join(args.ltf, docid+'.ltf.xml')
                laf_file = os.path.join(args.laf, docid+'.laf.xml')
                assert os.path.exists(ltf_file) and os.path.exists(laf_file)

                ltf_root = ET.parse(ltf_file)
                laf_root = ET.parse(laf_file)

                bio_str = ltflaf2bio(ltf_root, laf_root)

                combined_bio.append(bio_str)

                counter['num_doc_added'] += 1
            except AssertionError as e:
                print('ERROR:', ltf_file, e)
            except xml.etree.ElementTree.ParseError as e:
                print('ERROR: ', ltf_file, e)

        write2file('\n\n'.join(combined_bio), args.bio_file)

    else:
        ltf_root = ET.parse(args.ltf)
        laf_root = ET.parse(args.laf)

        bio_str = ltflaf2bio(ltf_root, laf_root)

        write2file(bio_str, args.bio_file)

        counter['num_doc_added'] = 1
        counter['num_ltf_files'] = 1
        counter['num_laf_files'] = 1

    print('\n=> ltflaf2bio stats:')
    print('%d ltf files are parsed.' % counter['num_ltf_files'])
    print('%d laf files are parsed.' % counter['num_laf_files'])
    print('%d valid documents are processed.' % counter['num_doc_added'])
    print('%d names are parsed in laf file.' % counter['num_labels'])
    print('%d B tags are added to bio.' % counter['num_b_tag'])
    print('%d tokens are re-tokenized.' % counter['num_retok_token'])
    print('%d mention offset errors.' % counter['mention_offset_error'])
