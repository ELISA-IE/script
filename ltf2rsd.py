import os
import codecs
import argparse
import xml.etree.ElementTree as ET


def ltf2rsd(ltf_str):
    root = ET.fromstring(ltf_str)
    doc = root.find('DOC')
    rsd = ''
    prev_sent_end = -1
    for seg in doc.findall('.//SEG'):
        seg_start = int(seg.get('start_char'))
        seg_end = int(seg.get('end_char'))
        seg_text = seg.find('ORIGINAL_TEXT').text
        rsd += '\n' * (seg_start - prev_sent_end - 1) + seg_text
        prev_sent_end = seg_end

        assert rsd[seg_start:seg_end+1] == seg_text

    return rsd


def ltf2rsd_batch(input_ltf, output_rsd):
    ltf_fns = os.listdir(input_ltf)
    for fn in ltf_fns:
        if '.ltf.xml' not in fn:
            continue
        ltf_file = os.path.join(input_ltf, fn)

        ltf_str = codecs.open(ltf_file, 'r', 'utf-8').read()

        rsd_str = ltf2rsd(ltf_str)

        rsd_file = os.path.join(output_rsd, fn.replace('.ltf.xml', '.rsd.txt'))

        write2file(rsd_str, rsd_file)


def write2file(rsd_str, rsd_file):
    with codecs.open(rsd_file, 'w', 'utf-8') as f:
        f.write(rsd_str)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', action='store_true', default=False, dest='is_dir',
                        help='Batch processing. When turned on, input and output are dirs.')
    parser.add_argument('ltf_input', type=str,
                        help='input ltf file path or directory.')
    parser.add_argument('rsd_output', type=str,
                        help='output rsd file path or directory.')

    args = parser.parse_args()

    input_ltf = args.ltf_input
    output_rsd = args.rsd_output

    if args.is_dir:
        ltf2rsd_batch(input_ltf, output_rsd)
    else:
        ltf_str = codecs.open(input_ltf, 'r', 'utf-8').read()
        rsd_str = ltf2rsd(ltf_str)
        write2file(rsd_str, output_rsd)