import xml.etree.ElementTree as ET
import zipfile
import argparse
import os
import codecs
import sys


def ltfzip2text(ltfzip, output_file):
    f_out = codecs.open(output_file, 'w', 'utf-8')

    num_sent = 0
    num_tokens = 0

    zip_file_path = []
    if os.path.isdir(ltfzip):
        for fn in os.listdir(ltfzip):
            if '.zip' not in fn:
                continue
            zip_file_path.append(os.path.join(ltfzip, fn))
    else:
        zip_file_path = [ltfzip]

    for file_path in zip_file_path:
        print("=> processing %s..." % file_path)
        zip_file = zipfile.ZipFile(file_path)
        info_list = zip_file.infolist()
        for ltf_fn in info_list:
            if '.ltf' not in ltf_fn.orig_filename:
                continue
            ltf_str = zip_file.read(ltf_fn)

            # parse ltf and generate tokenized plain text
            ltf_root = ET.fromstring(ltf_str)
            for seg in ltf_root.findall(".//SEG"):
                sent = []
                for token in seg.findall(".//TOKEN"):
                    sent.append(token.text)
                sent_text = ' '.join(sent)
                f_out.write(sent_text + "\n")
                num_sent += 1
                num_tokens += len(sent)

                sys.stdout.write("%d sentences processed. (%d tokens)\r" %
                                 (num_sent, num_tokens))
                sys.stdout.flush()

    print("%d sentences processed. (%d tokens)" %
          (num_sent, num_tokens))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("ltfzip")
    parser.add_argument("output_file", help='dat file path.')

    args = parser.parse_args()

    ltfzip2text(args.ltfzip, args.output_file)