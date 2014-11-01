from __future__ import unicode_literals, division
from textwrap import wrap
from nltk.tokenize import RegexpTokenizer
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

class Processor(object):
    '''
    '''

    def __init__(self):
        self.emoticons_pattern = r'''[<>]?[:;=8][\-o\*\']?[\)\]\(\[dDpP/\:\}\{@\|\\]'''
        self.emoticons_reversed_pattern = r'''[\)\]\(\[dDpP/\:\}\{@\|\\][\-o\*\']?[:;=8][<>]?'''
        self.username_pattern = r'''@+[\w_]+'''
        self.hashtag_pattern = r'''\#+[\w_]+[\w\'_\-]*[\w_]+'''
        self.url_pattern = r'''https?\://([^ ,;:()`'"])+'''

        self.token_pattern = r'''(?x)              # verbose regex
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
                    '''
        self.tokenizer = RegexpTokenizer(token_pattern)

    def process(self, text):
        return [w.lower() for w in self.tokenizer.tokenize(text)]

    def clean_tags(tagged):
	"""
	Correct POS tags for twitter-specific categories
	"""
	clean = list()
	for (w, t) in tagged:
		#make lowercase
		w = w.lower()
		if re.search(url_pattern, w):
			clean.append((w, "URL"))
		elif w[0] == "#":
			clean.append((w, "H_TAG"))
		elif w[0] == "@":
			clean.append((w, "U_NAME"))
		elif w == "rt":
			clean.append((w, "RT"))
		else:
			clean.append((w, t))
	return clean


class Tweet(object):
    '''
    '''
    def __init__(self, kwargs):
        self.default_val = "UNKNOWN"

        self.name = kwargs.get("name", self.default_val)
        self.username = kwargs.get("screen_name", self.default_val)
        self.gender = kwargs.get("gender", self.default_val)
        self.text = kwargs.get("text", None)
        self.RT = True if self.text.startswith("RT") else False

        self.processed_text = self.process_text()
        self.hashtags = self.get_hashtags()

    def __repr__(self):
        return """
                  name: {0}
              username: {1}
                gender: {2}
               retweet: {3}
                  text: {4}""".format(self.name, self.username, self.gender, self.RT,"\n\t\t\t".join(wrap(self.text, 50)))

    def get_hashtags(self):
        pass

    def process_text(self):
        pass


if __name__ == "__main__":
 tweets = [Tweet(json.loads(line)) for line in open("tweets_by_gender.txt", "r")]
