import operator
import os

import commonfunctions
import imdbfunctions

MINSCORE = 80000
MINVOTES = 100000
URL = 'http://www.imdb.com/search/title?count=250&num_votes=' + \
    str(MINVOTES) + ',&sort=num_votes,desc&view=simple'

# to resume execution if the script fails while running
# for testing purposes
SCORES = commonfunctions.loadfile('scores')
SCORES = imdbfunctions.getMovies(SCORES, URL, MINSCORE, maxbypassed=20)
commonfunctions.savescores(SCORES, 'scores')
SCORES = commonfunctions.loadfile('scores')
SCORES = {k: v for (k, v) in SCORES.items() if v[0] > MINSCORE}
SORTEDSCORES = sorted(SCORES.items(), key=operator.itemgetter(1), reverse=True)
commonfunctions.savescores(SORTEDSCORES, 'sortedtitles')
os.remove('scores.json')
