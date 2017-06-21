import io
import argparse
import xml.dom.minidom
import xml.etree.ElementTree as ET


def bio2ltf(bio_str):
    bio_sents = bio_str.split('\n\n')
    sents = []
    for sent in bio_sents:
        s = []
        for line in sent.splitlines():
            token = line.split(' ')[0]
            s.append(token)
        sents.append(s)

    doc_text = '\n'.join([' '.join(sent) for sent in sents])

    doc_id = bio_fp.split('/')[-1].replace('.bio', '')

    root = ET.Element('LCTL_TEXT')
    doc_element = ET.Element('DOC', {'id': doc_id})
    text_element = ET.Element('TEXT')
    root.append(doc_element)
    doc_element.append(text_element)

    prev_seg_end = -2
    for i in range(len(sents)):
        seg_text = ' '.join(sents[i])
        seg_start_char = prev_seg_end + 2  # '\n' between segs
        seg_end_char = seg_start_char + len(seg_text) - 1
        prev_seg_end = seg_end_char

        seg_id = '%s-%s' % (doc_id, str(i))

        seg_element = ET.Element('SEG', {'id': seg_id,
                                         'start_char': str(seg_start_char),
                                         'end_char': str(seg_end_char)})
        original_text_element = ET.Element('ORIGINAL_TEXT')
        original_text_element.text = seg_text
        seg_element.append(original_text_element)

        pre_tok_end = seg_start_char - 2
        for j in range(len(sents[i])):
            token_id = '%s-%s' % (seg_id, str(j))
            tok_text = sents[i][j]
            tok_start_char = pre_tok_end + 2
            tok_end_char = tok_start_char + len(tok_text) - 1
            pre_tok_end = tok_end_char

            assert doc_text[tok_start_char:tok_end_char+1] == tok_text

            token_element = ET.Element('TOKEN', {'id': token_id,
                                                 'start_char': str(tok_start_char),
                                                 'end_char': str(tok_end_char)})
            token_element.text = tok_text
            seg_element.append(token_element)

        text_element.append(seg_element)

    root = ET.ElementTree(root)

    return root


def write2file(root, ltf_fp):
    root.write(ltf_fp)

    # pretty print xml
    f_xml = xml.dom.minidom.parse(
        ltf_fp)  # or xml.dom.minidom.parseString(xml_string)
    pretty_xml_as_string = f_xml.toprettyxml()
    f = io.open(ltf_fp, 'w', -1, 'utf-8')
    f.write(pretty_xml_as_string)
    f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('bio_fp', type=str,
                        help='input bio file path.')
    parser.add_argument('ltf_fp', type=str,
                        help='output ltf file path.')

    args = parser.parse_args()

    bio_str = io.open(args.bio_fp, 'r', -1, 'utf-8').read()

    root = bio2ltf(bio_str)

    write2file(root, args.ltf_fp)
