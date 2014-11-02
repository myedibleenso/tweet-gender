from __future__ import unicode_literals, division # the pains of Python 2.X
from textwrap import wrap # for printing Tweet objects
from nltk.tokenize import RegexpTokenizer # why reinvent the wheel?i
from nltk.tag import pos_tag
from collections import defaultdict, Counter
import json
import re


'''
men:
    objects
    words that identify or determine nouns (a, the, that)
    words that quantify (one, two, more)
women:
    relationships
    more pronouns (I, you, she, their, myself)
'''

class UniqueCounter(Counter):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def not_in(self, other):
        return {k for k in self.keys() if k not in other}

    def overlap_with(self, other):
        return {k for k in self.keys() if k in other}

    def remove_items(self, to_remove):
        return UniqueCounter({k:v for (k,v) in self.iteritems() if k not in to_remove})


class Processor(object):
    '''
    '''
    modifier_pattern = re.compile(ur'''RB|JJ''', re.U)
    verb_pattern = re.compile(ur'''^VB''', re.U)

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
                #elif w[0].isupper() and re.match("^V|N", t) and i != 0:
                #    clean.append("ENTITY")
                else:
                    clean.append(t)
            return clean

        return clean_tags(self.tagger(tokens))

    def filter_by_pos_pattern(self, words, tags, pattern = None):
        pattern = pattern or self.modifier_pattern
        return (words[i] for (i, t) in enumerate(tags) if re.match(pattern, t))


####our instance of Processor####
processor = Processor()

class Tweet(object):
    '''
    '''
    def __init__(self, kwargs):
        self.default_val = "UNKNOWN"

        self.name = kwargs.get("name", self.default_val)
        self.firstname = self.name.split()[0].lower()
        self.username = kwargs.get("screen_name", self.default_val)
        self.gender = kwargs.get("gender", self.default_val)
        self.text = kwargs.get("text", None)
        self.RT = self.check_rt() # username retweeted if RT else False

        self.hashtags = self.get_hashtags()
        # linguistic information
        self.words = self.get_tokens()
        self.tags = self.get_tags()

    def __repr__(self):
        return """
                  name: {0}
            first name: {1}
              username: {2}
                gender: {3}
               retweet: {4}
              hashtags: {5}
                  text: {6}""".format(self.name,
                                      self.firstname,
                                      self.username,
                                      self.gender,
                                      self.RT,
                                      " ".join(self.hashtags),
                                      "\n\t\t\t".join(wrap(self.text, 50)))

    def check_rt(self):
        rt_pattern = re.compile("RT.*?(\@[^\s:]+)", re.I)
        try:
            return re.search(rt_pattern, self.text).group(1)
        except:
            return False

    def get_hashtags(self):
        hashtag_pattern = re.compile(r"#[A-Z0-9_]+",re.I)
        return re.findall(hashtag_pattern, self.text) or None

    # these methods communicate with an instance of Processor
    def get_tokens(self):
        return processor.tokenize(self.text)

    def get_tags(self):
        return processor.tag(self.words)

######################################
def character_ngrams(text, n, lc=True):
    '''
    returns generator of character ngrams with word boundary tokens
    '''
    boundary = "#"
    text = "{0}{1}{0}".format(boundary, text)
    text = text.lower() if lc == True else text
    for i in xrange(len(text) - n + 1):
        yield text[i:i+n]
#######################################

def get_name_character_ngrams(male, female, n=3):
    '''
    retrieve character ngrams of first names
    '''
    m_ngrams = UniqueCounter()
    f_ngrams = UniqueCounter()
    for m in male:
        m_ngrams.update(list(character_ngrams(m.firstname, n)))
    for f in female:
        f_ngrams.update(list(character_ngrams(f.firstname, n)))
    return (m_ngrams, f_ngrams)

class FeatureExtractor(object):

    def __init__(self):

        tweets = [Tweet(json.loads(line)) for line in open("tweets_by_gender.txt", "r")]
        male = filter(lambda t: t.gender == "male", tweets)
        female = filter(lambda t: t.gender == "female", tweets)
        rt_pattern = re.compile("RT.*?(\@[^\s:]+)", re.I) # to retweeted username
        retweeted = [re.search(rt_pattern, t.text) for t in male if t.RT]

        male_name_ngrams, female_name_ngrams = get_name_character_ngrams(male, female, n=4)
        # find overlap
        overlap = male_name_ngrams.overlap_with(female_name_ngrams)


if __name__ == "__main__":
    tweets = [Tweet(json.loads(line)) for line in open("tweets_by_gender.txt", "r")]
    male = filter(lambda t: t.gender == "male", tweets)
    female = filter(lambda t: t.gender == "female", tweets)
    rt_pattern = re.compile("RT.*?(\@[^\s:]+)", re.I) # to retweeted username
    retweeted = [re.search(rt_pattern, t.text) for t in male if t.RT]

    male_name_ngrams, female_name_ngrams = get_name_character_ngrams(male, female, n=4)
    # find overlap
    overlap = male_name_ngrams.overlap_with(female_name_ngrams)
