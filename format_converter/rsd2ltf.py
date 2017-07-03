#encoding=utf-8
import os
import argparse
import xml.dom.minidom
import xml.etree.ElementTree as ET
import codecs

from tokenizer import Tokenizer


def rsd2ltf(input_file, output_file, seg_option, tok_option):
    rsd_files = []
    output_files = []
    if os.path.isdir(input_file):
        assert os.path.isdir(output_file)

        for fn in os.listdir(input_file):
            if ".rsd.txt" not in fn:
                continue
            rsd_files.append(os.path.join(input_file, fn))
            output_files.append(os.path.join(output_file,
                                             fn.replace('rsd.txt', 'ltf.xml')))
    else:
        rsd_files = [input_file]
        output_files = [output_file]

    tokenizer = Tokenizer(seg_option, tok_option)
    for k, rsd_f in enumerate(rsd_files):
        try:
            f = codecs.open(rsd_f, 'r', 'utf-8').read()
            sents = tokenizer.run_segmenter(f)
            tokens = tokenizer.run_tokenizer(sents)

            # generate offset for sentences and tokens
            indexer = 0
            sent_offset = []
            for i, s in enumerate(sents):
                while not f[indexer:].startswith(s) and indexer < len(f):
                    indexer += 1
                if indexer < len(f):
                    sent_start = indexer
                    sent_end = sent_start + len(s) - 1
                    assert f[sent_start:sent_end+1] == s, \
                        "sentence offset not match %s-%d" % (rsd_f, i)
                    sent_offset.append((sent_start, sent_end))
                    indexer = sent_end + 1

            assert len(sent_offset) == len(sents), \
                "sentence segmentation offset error in: %s" % rsd_f
            token_offsets = []
            for i, tok in enumerate(tokens):
                sent_text = sents[i]
                indexer = 0
                t_offset = []
                for j, t in enumerate(tok):
                    while not sent_text[indexer:].startswith(t) and \
                                    indexer < len(sent_text):
                        indexer += 1
                    if indexer < len(sent_text):
                        t_start = indexer
                        t_end = t_start + len(t) - 1
                        assert sent_text[t_start:t_end+1] == t, \
                            "token offset not match %s-%d-%d" % (rsd_f, i, j)
                        t_offset.append((t_start, t_end))
                        indexer = t_end + 1
                token_offsets.append(t_offset)

                assert len(t_offset) == len(tok), \
                    "tokenization offset error in: %s-%d" % (rsd_f, i)

            # convert seg/tok result to ltf
            doc_id = os.path.basename(rsd_f).replace('.rsd.txt', '')

            root = ET.Element('LCTL_TEXT')
            doc_element = ET.Element('DOC', {'id': doc_id})
            text_element = ET.Element('TEXT')
            root.append(doc_element)
            doc_element.append(text_element)

            for i in range(len(sents)):
                seg_text = sents[i]
                seg_start_char = sent_offset[i][0]
                seg_end_char = sent_offset[i][1]

                seg_id = '%s-%s' % (doc_id, str(i))

                seg_element = ET.Element('SEG', {'id': seg_id,
                                                 'start_char': str(seg_start_char),
                                                 'end_char': str(seg_end_char)})
                original_text_element = ET.Element('ORIGINAL_TEXT')
                original_text_element.text = seg_text
                seg_element.append(original_text_element)

                for j in range(len(tokens[i])):
                    token_id = 'token-%d-%d' % (i, j)
                    tok_text = tokens[i][j]
                    if not tok_text:
                        continue
                    tok_start_char = int(token_offsets[i][j][0]) + seg_start_char
                    tok_end_char = int(token_offsets[i][j][1]) + seg_start_char

                    assert f[tok_start_char:tok_end_char+1] == tok_text

                    token_element = ET.Element('TOKEN',
                                               {'id': token_id,
                                                'start_char': str(tok_start_char),
                                                'end_char': str(tok_end_char)})
                    token_element.text = tok_text
                    seg_element.append(token_element)

                text_element.append(seg_element)

            # pretty print xml
            root_str = ET.tostring(root, 'utf-8')
            f_xml = xml.dom.minidom.parseString(root_str)
            pretty_xml_as_string = f_xml.toprettyxml(encoding="utf-8")
            f = open(output_files[k], 'wb')
            f.write(pretty_xml_as_string)
            f.close()
        except AssertionError as e:
            print(e)

        if (k + 1) % 50 == 0:
            print('%d files processed.' % (k + 1))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('rsd_input', type=str,
                        help='input rsd file path or directory.')
    parser.add_argument('ltf_output', type=str,
                        help='output ltf file path or directory.')
    t = Tokenizer()
    parser.add_argument('--seg_option', default='linebreak',
                        help="segmentation options: %s (default is linebreak)" %
                             ', '.join(t.segmenters.keys()))
    parser.add_argument('--tok_option', default='unitok',
                        help="tokenization options: %s (default is unitok)" %
                             ', '.join(t.tokenizers.keys()))

    args = parser.parse_args()

    input_rsd = args.rsd_input
    output_ltf = args.ltf_output

    rsd2ltf(input_rsd, output_ltf, args.seg_option, args.tok_option)
