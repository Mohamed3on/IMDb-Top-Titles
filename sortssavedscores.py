import operator

import functions
scores=functions.loadfile('scores')
sortedscores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
functions.savescores(sortedscores, 'sortedtitles')
## This is a hack to get the desired format to operate on
newsorted = functions.loadfile('sortedtitles')
for score in newsorted:
    score[0] = functions.unicodeToHTMLEntities(score[0])
functions.savescores(newsorted, 'sortedtitles')
