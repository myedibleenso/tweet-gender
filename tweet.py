from __future__ import unicode_literals, division # the pains of Python 2.X
from textwrap import wrap # for printing Tweet objects
from collections import defaultdict, Counter
from processor import processor
import json
import re

class UniqueCounter(Counter):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def not_in(self, other):
        return {k for k in self.keys() if k not in other}

    def overlap_with(self, other):
        return {k for k in self.keys() if k in other}

    def remove_items(self, to_remove):
        return UniqueCounter({k:v for (k,v) in self.iteritems() if k not in to_remove})


class Tweet(object):
    '''
    '''
    def __init__(self, kwargs, tag_tweet = False):
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
        self.tags = None if tag_tweet == False else self.get_tags() # tagging is expensive...

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


##########################################################
##########################################################

if __name__ == "__main__":
    do_tag = False
    print "processing tweets ({0})...".format("without PoS tagging" if not do_tag else "with PoS tagging")
    tweets = [Tweet(json.loads(line), tag_tweet=do_tag) for line in open("tweets_by_gender.txt", "r")]
    male = filter(lambda t: t.gender == "male", tweets)
    female = filter(lambda t: t.gender == "female", tweets)
