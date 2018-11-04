import operator
import os
import commonfunctions
import imdbfunctions
import login
MINSCORE = 60000
MINVOTES = 120000
MAXVOTES = 350000
MIN_RELEASE_DATE = 1979

URL = 'http://www.imdb.com/search/title?count=250&num_votes=' + \
    str(MINVOTES) + ',' + str(MAXVOTES) + \
    '&sort=num_votes,desc&view=simple&my_ratings=exclude&user_rating=6.8,&release_date=' + \
    MIN_RELEASE_DATE+',&runtime=,202'


def getStuff(url, filename='sortedtitles'):
    # to resume execution if the script fails while running
    # for testing purposes
    SCORES = commonfunctions.loadfile('scores')
    SCORES = imdbfunctions.getMovies(
        SCORES, url, MINSCORE, maxbypassed=15, minratio=0.18)
    commonfunctions.savescores(SCORES, 'scores')
    SCORES = commonfunctions.loadfile('scores')
    SCORES = {k: v for (k, v) in SCORES.items() if v[0] > MINSCORE}
    SORTEDSCORES = sorted(
        SCORES.items(), key=operator.itemgetter(1), reverse=True)
    commonfunctions.savescores(SORTEDSCORES, filename)
    os.remove('scores.json')


getStuff(URL)
