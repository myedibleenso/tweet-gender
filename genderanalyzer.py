from __future__ import unicode_literals, division # the pains of Python 2.X
from featureextractor import *
from processor import *
from tweet import *
import sys


##########################################################
##########################################################

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("No file name specified!\n\nUSAGE:\n\tpython genderanalyzer.py /path/to/file/to/classify")
        sys.exit(0)

    fe = FeatureExtractor()
    to_classify = sys.argv[-1]
    try: # attempt to load pickled classifier
        classifier = Classifier.load()
    except: # train from scratch if there's a problem...
        classifier = Classifier(NaiveBayesClassifier)
        classifier.train(fe.prepare_training_data())

    with open(os.path.expanduser(to_classify), "r") as infile:
        for line in infile:
            tweet = Tweet(json.loads(line))
            feature_vector = fe.tweet2features(tweet)
            print classifier.classify(feature_vector)
