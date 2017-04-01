import operator

import functions

minScore = 10000
minVotes = 25000
url = 'http://www.imdb.com/search/title?count=250&num_votes=' + str(minVotes) + ',&sort=num_votes,desc&view=simple'
# to resume execution if the script fails while running
scores = functions.loadfile('scores')
scores = functions.getMovies(scores, url, minScore)
sortedscores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
functions.savescores(sortedscores, 'sortedtitles')
## This is a hack to get the desired format to operate on
newsorted = functions.loadfile('sortedtitles')
for score in newsorted:
    score[0] = functions.unicodeToHTMLEntities(score[0])
functions.savescores(newsorted, 'sortedtitles')
