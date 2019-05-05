import operator
import os
import commonfunctions
import imdbfunctions
import login

MINSCORE = 45000
MIN_RATIO = 0.29

MINVOTES = str(100000)
MAXVOTES = str(360000)
MIN_RELEASE_DATE = str(1988)
MAX_RUNTIME = str(202)
MIN_RATING = str(7.4)

URL = 'http://www.imdb.com/search/title?count=250&num_votes=' + \
    MINVOTES + ',' + MAXVOTES + \
    '&sort=num_votes,desc&view=simple&my_ratings=exclude&user_rating='+MIN_RATING+',&release_date=' + \
    MIN_RELEASE_DATE+',&runtime=,'+MAX_RUNTIME


def getStuff(url, filename='sortedtitles'):
    # to resume execution if the script fails while running
    # for testing purposes
    SCORES = commonfunctions.loadfile('scores')
    SCORES = imdbfunctions.getMovies(
        SCORES, url, MINSCORE, maxbypassed=20, minratio=MIN_RATIO)
    commonfunctions.savescores(SCORES, 'scores')
    SCORES = commonfunctions.loadfile('scores')
    SCORES = {k: v for (k, v) in SCORES.items()
              if v[0] > MINSCORE and v[2] > MIN_RATIO}
    SORTEDSCORES = sorted(
        SCORES.items(), key=operator.itemgetter(1), reverse=True)
    commonfunctions.savescores(SORTEDSCORES, filename)
    os.remove('scores.json')


getStuff(URL)
