from __future__ import unicode_literals, division # the pains of Python 2.X
from nltk.tokenize import RegexpTokenizer # why reinvent the wheel?i
from nltk.tag import pos_tag
import re

class Processor(object):
    '''
    '''
    modifier_pattern = re.compile(ur'''RB|JJ''', re.U)
    verb_pattern = re.compile(ur'''^VB''', re.U)

    boundary = "_"

    def __init__(self):
        self.emoticons_pattern = re.compile(ur'''[<>]?[:;=8][\-o\*\']?[\)\]\(\[dDpP/\:\}\{@\|\\]''',re.I|re.U)
        self.emoticons_reversed_pattern = re.compile(ur'''[\)\]\(\[dDpP/\:\}\{@\|\\][\-o\*\']?[:;=8][<>]?''', re.I|re.U)
        self.username_pattern = re.compile(ur'''@+[\w_]+''', re.I|re.U)
        self.hashtag_pattern = re.compile(ur'''\#+[\w_]+[\w\'_\-]*[\w_]+''', re.I|re.U)
        self.url_pattern = re.compile(ur'''https?\://([^ ,;:()`'"])+''', re.I|re.U)
        self.currency_pattern = re.compile(ur'''\$?\d+(\.\d+)?%?''', re.I|re.U)
        self.elipsis_pattern = re.compile(ur'''\.\.\.''', re.I|re.U)
        self.abbreviation_pattern = re.compile(ur'''([A-Z]\.)+''', re.I|re.U)
        self.word_pattern = re.compile(ur'''(\w+[a-z0-9_-]*)*''', re.I|re.U)

        self.token_pattern = re.compile(ur'''(?xui)       # case insenstive, unicode, verbose
                    https?\://([^ ,;:()`'"])+   # URLs
                    | [<>]?[:;=8][\-o\*\']?[\)\]\(\[dDpP/\:\}\{@\|\\]   # emoticons
                    | [\)\]\(\[dDpP/\:\}\{@\|\\][\-o\*\']?[:;=8][<>]?   # emoticons (reverse orientation)
                    | ([A-Z]\.)+                # abbreviations
                    | \w+(-\w+)*                # words with (optional) hyphens
                    | \$?\d+(\.\d+)?%?          # currency and percentages
                    | \.\.\.                    # ellipsis
                    | @+[\w_]+                  # user names
                    | \#+[\w_]+[\w\'_\-]*[\w_]+ # hashtags
                    | [.,;"'?():-_`]            # separate tokens
                    ''')

        self.tokenizer = RegexpTokenizer(self.token_pattern)
        self.tagger = pos_tag

    def tokenize(self, text):
        return self.tokenizer.tokenize(text)

    def tag(self, tokens):

        def clean_tags(tagged):
            """
            Correct POS tags for twitter-specific categories
            """
            clean = list()
            for i, (w, t) in enumerate(tagged):
                #make lowercase
                w = w.lower()
                if re.search(self.url_pattern, w):
                    clean.append("URL")
                elif w[0] == "#":
                    clean.append("H_TAG")
                elif w[0] == "@":
                    clean.append("U_NAME")
                elif w == "rt":
                    clean.append("RT")
                # stupid NER / tag cleanup
                elif w[0].isupper() and re.match("^V|N", t) and i != 0:
                    clean.append("ENTITY")
                else:
                    clean.append(t)
            return clean

        return clean_tags(self.tagger(tokens))

    def filter_by_pos_pattern(self, words, tags, pattern = None):
        pattern = pattern or self.modifier_pattern
        return (words[i] for (i, t) in enumerate(tags) if re.match(pattern, t))

    def character_ngrams(self, text, n, lc=True):
        '''
        returns generator of character ngrams with word boundary tokens
        '''
        text = "{0}{1}{0}".format(self.boundary, text)
        text = text.lower() if lc == True else text
        for i in xrange(len(text) - n + 1):
            yield text[i:i+n]

    def ngrams(self, tokens, n, lc=True):
        '''
        returns generator of character ngrams with word boundary tokens
        '''
        tokens = [self.boundary] + tokens + [self.boundary]
        for i in xrange(len(tokens) - n + 1):
            ngram = ' '.join(tokens[i:i+n])
            yield ngram.lower() if lc else ngram


####our instance of Processor####
processor = Processor()

##########################################################
##########################################################

if __name__ == "__main__":
    pass
