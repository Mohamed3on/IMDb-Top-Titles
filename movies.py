import operator

import functions

minScore = 10000
# for testing purposes
# scores = functions.loadfile('scores')
scores = {}
scores = functions.getMovies(
    scores, 'http://www.imdb.com/search/title?count=250&num_votes=30000,&sort=num_votes,desc&view=simple', minScore)

sortedscores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
functions.savescores(sortedscores, 'sortedtitles')
newsorted = functions.loadfile('sortedtitles')
for score in newsorted:
    score[0] = functions.unicodeToHTMLEntities(score[0])
functions.savescores(newsorted, 'sortedtitles')
