#encoding=utf-8
import os
import jieba
import nltk
import unicodedata as ud


class Tokenizer(object):
    def __init__(self, seg_option="linebreak", tok_option="unitok"):
        self.segmenters = {'linebreak': self.seg_linebreak,
                           'nltk': self.seg_nltk,
                           'cmn': self.seg_cmn
                           }
        self.tokenizers = {'unitok': self.tok_unitok,
                           'regexp': self.tok_regexp,
                           'nltk_wordpunct': self.tok_nltk_wordpunct,
                           'space': self.tok_space,
                           'char': self.tok_char,
                           'jieba': self.tok_jieba,
                           }

        self.root_dir = os.path.dirname(os.path.abspath(__file__))

        self.seg_option = seg_option
        self.tok_option = tok_option

    def run_segmenter(self, plain_text):
        # right strip plain text
        plain_text = plain_text.rstrip()

        # run segmenter
        sents = self.segmenters[self.seg_option](plain_text)
        return sents

    def run_tokenizer(self, sents):
        # right strip each sent
        for i in range(len(sents)):
            sents[i] = sents[i].rstrip()

        # run tokenizer
        tokenized_sents = self.tokenizers[self.tok_option](sents)

        return tokenized_sents

    #
    # segmenters
    #
    def seg_linebreak(self, plain_text):
        """
        use "\n" as delimiter
        :param plain_text:
        :return:
        """
        result = [item.strip() for item in plain_text.split('\n')]

        return result

    def seg_nltk(self, plain_text):
        """
        use nltk default segmenter
        :param plain_text:
        :return:
        """
        result = [item.strip() for item in nltk.sent_tokenize(plain_text)]

        return result

    def seg_cmn(self, plain_text):
        """
        use Chinese punctuation as delimiter
        :param plain_text:
        :return:
        """
        res = []
        sent_end_char = [u'。', u'！', u'？']
        current_sent = ''
        for i, char in enumerate(list(plain_text)):
            if char in sent_end_char or i == len(list(plain_text)) - 1:
                res.append(current_sent + char)
                current_sent = ''
            else:
                current_sent += char

        return [item.strip() for item in res]

    #
    # tokenizers
    #
    def tok_unitok(self, sents):
        res = []
        for s in sents:
            s = unitok_tokenize(s).split()
            res.append(s)

        return res

    def tok_regexp(self, sents):
        result = []
        for s in sents:
            tokenizer = nltk.tokenize.RegexpTokenizer('\w+|\$[\d\.]+|\S+')
            tokenization_out = tokenizer.tokenize(s)
            result.append(tokenization_out)

        return result

    def tok_nltk_wordpunct(self, sents):
        result = []
        for s in sents:
            tokenizer = nltk.tokenize.WordPunctTokenizer()
            tokenization_out = tokenizer.tokenize(s)
            result.append(tokenization_out)
        return result

    def tok_space(self, sents):
        result = []
        for s in sents:
            tokenization_out = s.split(' ')
            result.append(tokenization_out)
        return result

    def tok_char(self, sents):
        result = []
        for s in sents:
            tokenization_out = list(s)
            result.append(tokenization_out)
        return result

    def tok_jieba(self, sents):
        result = []
        for s in sents:
            raw_tokenization_out = list(jieba.cut(s))
            result.append(raw_tokenization_out)
        return result


# by Jon May
def unitok_tokenize(data):
    toks = []
    for offset, char in enumerate(data):
        cc = ud.category(char)
        # separate text by punctuation or symbol
        if cc.startswith("P") or cc.startswith("S"):
            toks.append(' ')
            toks.append(char)
            toks.append(' ')
        else:
            toks.append(char)

    toks = [item for item in ''.join(toks).split() if item]

    return ' '.join(toks)