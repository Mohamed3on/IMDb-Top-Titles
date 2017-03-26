import operator

import functions

minScore = 10000
# for testing purposes
scores = functions.loadfile('scores')
# scores = imdb.getMovies(scores,
#                       'http://www.imdb.com/search/title?num_votes=1000,&sort=user_rating,desc&title_type=tv_episode&view=simple',
#                       minScore)

sortedscores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
functions.savescores(sortedscores, 'sortedtitles')
newsorted = functions.loadfile('sortedtitles')
for score in newsorted:
    score[0] = functions.unicodeToHTMLEntities(score[0])

functions.savescores(newsorted, 'sortedtitles')
