from __future__ import unicode_literals, division # the pains of Python 2.X
from processor import processor
from nltk.classify import *
from tweet import *
from os.path import expanduser
import re
try:
   import cPickle as pickle
except:
   import pickle

class FeatureExtractor(object):

    def __init__(self, verbose=False):
        self.verbose = verbose

    def mumble(self, sometext):
        if self.verbose:
            print sometext

    def prepare_training_data(self):
        tweets = [Tweet(json.loads(line)) for line in open("tweets_by_gender.txt", "r")]
        return [self.training_tweet(tweet) for tweet in tweets]
        #self.male = filter(lambda t: t.gender == "male", self.tweets)
        #self.female = filter(lambda t: t.gender == "female", self.tweets)
        #male_name_ngrams, female_name_ngrams = self.get_name_character_ngrams(self.male, self.female, n=4)
        # find overlap
        #overlap = male_name_ngrams.overlap_with(female_name_ngrams)


    def tweet2features(self, tweet):

        features = dict()
        # get character_ngrams
        char_n = 3
        token_n = 2

        # not sure what will be available during test...
        # check character n-grams of first name
        try:
            features.update(self.label_features(label="firstname-{0}grams-contain".format(char_n), featuredict=UniqueCounter(list(processor.character_ngrams(tweet.firstname, char_n)))))
        except:
            self.mumble("char ngram failed")

        # check token n-grams of tweet text
        try:
            features.update(self.label_features(label="token-{0}grams-contain".format(token_n), featuredict=UniqueCounter(list(processor.ngrams(tweet.words, token_n)))))
        except:
            self.mumble("token ngram failed")

        # is it a retweet?
        try:
            features.update({"is-retweet":True if tweet.RT else False})
        except:
            self.mumble("retweet test failed")

        # hashtags
        try:
            if tweet.hashtags:
                features.update({"has-hashtag({0})".format(ht):True for ht in tweet.hashtags})
            features.update({"has-hashtag":True if tweet.hashtags else False})
        except:
            self.mumble("hashtag test failed")

        # contains a url
        try:
            features.update({"has-url":True if re.search(processor.url_pattern, tweet.text) else False})
        except:
            self.mumble("url test failed")

        # modifiers ****
            # features.update()

        # expletive count ****
            # features.update()

        # contains emoticon ****
        try:
            features.update({"has-emoticon":self.has_emoticons(tweet)})
        except:
            self.mumble("emoticon test failed")

        # sentiment score ****
            # features.update()

        # number of determiners
            # features.update()

        return features

    def has_emoticons(self, tweet):
        # first remove urls
        cleaned = re.sub(processor.url_pattern, "", tweet.text)
        cleaned = re.sub(processor.username_pattern, "", cleaned)
        cleaned = re.sub(processor.hashtag_pattern, "", cleaned)
        return True if (re.search(processor.emoticons_pattern, cleaned) or re.search(processor.emoticons_reversed_pattern, cleaned)) else False

    def label_features(self, label, featuredict):
        '''
        prepend label to feature
        '''
        return {"{0}({1})".format(label,k):v for (k,v) in featuredict.iteritems()}

    def training_tweet(self, tweet):
        '''
        return features and label (gender)
        '''
        return (self.tweet2features(tweet), tweet.gender)


class Classifier(MultiClassifierI):

    default_fname="gender-classifier.pickle"

    @staticmethod
    def load(fname=default_fname):
        load_from = expanduser(fname)

        with open(load_from) as data:
            classifier = pickle.load(data)
        return classifier

    @staticmethod
    def save(classifier, fname=default_fname):
        '''
        pickle classifier to some file
        '''
        save_to = expanduser(fname)
        with open(save_to,'wb') as out:
            pickle.dump(classifier, out)
        print "classifier saved to {0}".format(save_to)

    def __init__(self, classifier=None, verbose=False):
        self._classifier = classifier
        #self.name = str(classifier).split(".")[-1][:-2]
        self.name = "gender-classifier"
        #self.fname =  "{0}.pickle".format(self.name)
        self.verbose = verbose

    def train(self, training_data):
        self._classifier = self._classifier.train(training_data)

    def classify(self, datum):
        return self._classifier.classify(datum)

    def labels(self):
        return self._classifier.labels()

    def prob_classify(self, datum):
        return self._classifier.prob_classify(datum)

    def most_informative_features(self, n=None):
        return self._classifier.most_informative_features(n)

    def show_most_informative_features(self, n=None):
        return self._classifier.show_most_informative_features(n)

    def _choose_file(self, fname):
        if fname:
            fname = expanduser(fname)

        return fname or self.fname

    def mumble(self, sometext):
        if self.verbose:
            print sometext

    def show_confidence(self, test):
        distribution = self.prob_classify(test)
        for label in distribution.samples():
            print "{0}:\t{1}".format(label, distribution.prob(label))

    def precision(self, gold_data, label):

        feature_vectors, gold_labels = zip(*gold_data)
        predicted = self.classify_many(feature_vectors)
        tp = 0
        fp = 0
        for i,p in enumerate(predicted):
            if p == gold_labels[i] == label:
                tp += 1
            elif (p == label) and (p != gold_labels[i]): # thought it was right but it was wrong
                fp += 1
        return tp/(tp+fp)


    def recall(self, gold_data, label):

        feature_vectors, gold_labels = zip(*gold_data)
        predicted = self.classify_many(feature_vectors)
        tp = 0
        fn = 0
        for i,p in enumerate(predicted):
            if p == gold_labels[i] == label:
                tp += 1
            elif (gold_labels[i] == label) and (p != label): # thought it was wrong but it was right
                fn += 1
        return tp/(tp + fn)

    def f1(self, gold_data, label):
        """
        F-measure via harmonic mean
        """
        precision = self.recall(gold_data, label)
        recall = self.recall(gold_data, label)
        return 2 * (precision * recall) / (precision + recall)


##########################################################
##########################################################

if __name__ == "__main__":
    print "processing tweets..."

    fe = FeatureExtractor()
    training_data = fe.prepare_training_data()
    classifier = Classifier(NaiveBayesClassifier)
    print "training classifier..."
    classifier.train(training_data)
    save_to = Classifier.default_fname
    Classifier.save(classifier, save_to)
