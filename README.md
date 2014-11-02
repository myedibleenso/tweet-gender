tweet-gender
============

TL project

predict the gender of a tweet's author based on:
-  character ngrams of the user's first name
-  token bigrams
-  whether or not the tweet contains a url
-  whether or not the tweet is a retweet
-  whether or not the tweet contains any emoticons
-  whether or not the tweet contains any hashtags
-  any hashtags in the tweet

The code is designed to also analyze the PoS content of the tweet (Penn-style tags modified slightly for twitter), but this feature is disabled by default (see the Processor class).


Running the code:

1. Clone the repository:  

  `git clone https://github.com/myedibleenso/tweet-gender.git`  

2. Install the dependencies (just `nltk`):  

  `pip install -r requirements.txt`

3. Run the classifier:

  `python genderpredictor.py path/to/your/file`


By default, tweets are labeled using a NaiveBayes classifier.  There are also methods to generate precision, recall, and f1 scores for a label (i.e. "male" or "female").
