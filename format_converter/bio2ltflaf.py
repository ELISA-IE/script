import codecs
import argparse
import xml.dom.minidom
import xml.etree.ElementTree as ET


def bio2ltflaf(bio_str, doc_id, delimiter=' '):
    bio_sents = bio_str.split('\n\n')
    sents = []
    tags = []
    for sent in bio_sents:
        s = []
        t = []
        for line in sent.splitlines():
            token = line.split(' ')[0]
            tag = line.split(' ')[1]
            s.append(token)
            t.append(tag)
        sents.append(s)
        tags.append(t)

    doc_text = '\n'.join([delimiter.join(sent) for sent in sents])

    # ltf xml root
    ltf_root = ET.Element('LCTL_TEXT')
    ltf_doc_element = ET.Element('DOC', {'id': doc_id})
    ltf_text_element = ET.Element('TEXT')
    ltf_root.append(ltf_doc_element)
    ltf_doc_element.append(ltf_text_element)

    # laf xml root
    laf_root = ET.Element('LCTL_ANNOTATIONS')
    laf_doc_element = ET.Element('DOC', {'id': doc_id})
    laf_root.append(laf_doc_element)

    prev_seg_end = -2
    for i in range(len(sents)):
        # ======== generate ltf file
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

        ltf_text_element.append(seg_element)

        # ======= generate laf file
        # get annotations
        annotations = []
        tmp_ann_start = -1
        for j in range(len(sents[i])):
            if tags[i][j].startswith('B'):
                if tmp_ann_start != -1:
                    tmp_ann_end = j - 1
                    e_type = tags[i][tmp_ann_end].split('-')[1]
                    annotations.append((tmp_ann_start, tmp_ann_end, e_type))
                tmp_ann_start = j
            elif tags[i][j].startswith('O'):
                if tmp_ann_start != -1:
                    tmp_ann_end = j - 1
                    e_type = tags[i][tmp_ann_end].split('-')[1]
                    annotations.append((tmp_ann_start, tmp_ann_end, e_type))
                tmp_ann_start = -1
            elif j == len(sents[i]) - 1:
                if tmp_ann_start != -1:
                    tmp_ann_end = j
                    e_type = tags[i][tmp_ann_end].split('-')[1]
                    annotations.append((tmp_ann_start, tmp_ann_end, e_type))
        # map offsets to annotation
        for j, ann in enumerate(annotations):
            start_index = int(ann[0])
            end_index = int(ann[1])
            e_type = ann[2]

            if e_type not in ["PER", "ORG", "LOC"]:
                continue
            if e_type == 'LOC':
                e_type = 'GPE'

            annotation_text = ' '.join(sents[i][start_index:end_index+1])
            start_offset = len(' '.join(sents[i][:start_index+1])) - len(sents[i][start_index]) + seg_start_char
            end_offset = len(' '.join(sents[i][:end_index+1])) + seg_start_char - 1
            assert doc_text[start_offset:end_offset+1] == annotation_text
            ann_id = '%s-ann-%d' % (doc_id, j)
            annotation_element = ET.Element('ANNOTATION', {'id': ann_id,
                                                           'task': 'NE',
                                                           'type': e_type})
            extent_element = ET.Element('EXTENT', {'start_char': str(start_offset),
                                                   'end_char': str(end_offset)})
            extent_element.text = annotation_text
            annotation_element.append(extent_element)
            laf_doc_element.append(annotation_element)

    return ltf_root, laf_root


def write2file(ltf_root, laf_root, ltf_fp, laf_fp):
    ltf_xml_str = ET.tostring(ltf_root, 'utf-8')
    ltf_xml = xml.dom.minidom.parseString(ltf_xml_str)
    f = codecs.open(ltf_fp, 'w', 'utf-8')
    f.write(ltf_xml.toprettyxml(indent='\t'))
    f.close()

    laf_xml = xml.dom.minidom.parseString(ET.tostring(laf_root, 'utf-8'))
    f = codecs.open(laf_fp, 'w', 'utf-8')
    f.write(laf_xml.toprettyxml(indent='\t'))
    f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('bio_fp', type=str,
                        help='input bio file path.')
    parser.add_argument('ltf_fp', type=str,
                        help='output ltf file path.')
    parser.add_argument('laf_fp', type=str,
                        help='output laf file path.')

    args = parser.parse_args()

    bio_str = codecs.open(args.bio_fp, 'r', 'utf-8').read()

    doc_id = args.bio_fp.split('/')[-1].replace('.bio', '')

    ltf_root, laf_root = bio2ltflaf(bio_str, doc_id)

    write2file(ltf_root, laf_root, args.ltf_fp, args.laf_fp)
