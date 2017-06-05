import operator

import functions

minScore = 30000
minVotes = 50000
url = 'http://www.imdb.com/search/title?count=250&num_votes=' + str(minVotes) + ',&sort=num_votes,desc&view=simple'
# to resume execution if the script fails while running
# for testing purposes
scores = functions.loadfile('scores')
scores = functions.getMovies(scores, url, minScore)
functions.savescores(scores,'scores')
sortedscores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
functions.savescores(sortedscores, 'sortedtitles')
