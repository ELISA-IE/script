import argparse
import codecs
import xml.etree.ElementTree as ET
import gzip


def elisa2bio(elisa_file, output_file):
    doc_num = 0
    #
    # parse elisa file
    #
    print("parsing elisa file..."),
    if elisa_file.endswith('.gz'):
        with gzip.open(elisa_file, 'rb') as f:
            elisa_file_content = f.read()
        root = ET.fromstring(elisa_file_content)
    else:
        root = ET.parse(elisa_file)
    print("done")

    #
    # generate bio
    #
    bio_results = []
    for doc in root.findall('DOCUMENT'):
        doc_num += 1
        doc_id = doc.get('id')
        bio_resut = []
        for seg in doc.findall('SEGMENT'):
            try:
                seg_src = seg.find('SOURCE')
                seg_src_start_char = int(seg_src.get('start_char'))
                seg_src_end_char = int(seg_src.get('end_char'))
                seg_src_orig_raw = seg_src.find('ORIG_RAW_SOURCE').text
                # use orig_raw as tokenized text if not tokenization founds
                if not seg_src.find('LRLP_TOKENIZED_SOURCE'):
                    seg_src_tokenized = seg_src_orig_raw
                else:
                    seg_src_tokenized = seg_src.find('LRLP_TOKENIZED_SOURCE').text
                # ignore empty token here
                seg_src_tokenized = [item
                                     for item in seg_src_tokenized.split(' ')
                                     if item]
                seg_src_id = seg_src.find('ORIG_SEG_ID').text

                sent_indexer = 0
                token_offset = []
                for i in range(len(seg_src_tokenized)):
                    token = seg_src_tokenized[i]

                    while not seg_src_orig_raw[sent_indexer:].startswith(token) \
                            and sent_indexer < len(seg_src_orig_raw):
                        sent_indexer += 1

                    token_start_char = sent_indexer
                    token_end_char = token_start_char + len(token) - 1
                    assert seg_src_orig_raw[token_start_char:token_end_char+1] == token

                    token_offset.append((seg_src_start_char+token_start_char,
                                         seg_src_start_char+token_end_char))
                    sent_indexer = token_end_char + 1

                assert len(seg_src_tokenized) == len(token_offset)
                bio_resut.append('\n'.join(['%s %s:%d-%d' %
                                            (seg_src_tokenized[i],
                                             doc_id,
                                             token_offset[i][0],
                                             token_offset[i][1])
                                            for i in range(len(token_offset))]))
            except AssertionError:
                print('\tassertion error in %s of %s' % (seg_src_id, doc_id))
                continue

        bio_results.append('\n\n'.join(bio_resut))

        if doc_num % 100 == 0:
            print("%d documents processed." % doc_num)

    with codecs.open(output_file, 'w', 'utf-8') as f:
        f.write('\n\n'.join(bio_results)+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('elisa_file', type=str,
                        help='input elisa file path')
    parser.add_argument('output_file', type=str,
                        help='output bio file')

    args = parser.parse_args()

    elisa2bio(args.elisa_file, args.output_file)
