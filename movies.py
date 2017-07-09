import operator
import os

import functions

MINSCORE = 50000
MINVOTES = 100000
URL = 'http://www.imdb.com/search/title?count=250&num_votes=' + \
      str(MINVOTES) + ',&sort=num_votes,desc&view=simple'
# to resume execution if the script fails while running
# for testing purposes
SCORES = functions.loadfile('SCORES')
SCORES = functions.getMovies(SCORES, URL, MINSCORE)
functions.savescores(SCORES, 'SCORES')
SORTEDSCORES = sorted(SCORES.items(), key=operator.itemgetter(1), reverse=True)
functions.savescores(SORTEDSCORES, 'sortedtitles')
os.remove('SCORES.json')
