import operator
import os
import commonfunctions
import imdbfunctions

MINSCORE = 8000
MIN_RATIO = 0.14  # default is 0.29 (superbad)

MINVOTES = str(80000)
MAXVOTES = str(800000)
MIN_RELEASE_DATE = str(1964)
MAX_RUNTIME = str(200)  # at most as long as seven samurai
MIN_RATING = str(7.1)

URL = 'http://www.imdb.com/search/title?count=250&num_votes=' + \
    MINVOTES + ',' + MAXVOTES + \
    '&sort=num_votes,desc&view=simple&my_ratings=exclude&user_rating='+MIN_RATING+',&release_date=' + \
    MIN_RELEASE_DATE+',&runtime=,'+MAX_RUNTIME


def get_stuff(url, filename='sortedtitles'):
    # to resume execution if the script fails while running
    # for testing purposes
    SCORES = commonfunctions.loadfile('scores')
    SCORES = imdbfunctions.get_movies(
        SCORES, url, MINSCORE, maxbypassed=40, min_ratio=MIN_RATIO)
    commonfunctions.savescores(SCORES, 'scores')
    SCORES = commonfunctions.loadfile('scores')
    SCORES = {k: v for (k, v) in SCORES.items()
              if v[0] > MINSCORE and v[2] > MIN_RATIO}
    SORTEDSCORES = sorted(
        SCORES.items(), key=operator.itemgetter(1), reverse=True)
    commonfunctions.savescores(SORTEDSCORES, filename)
    os.remove('scores.json')
    os.system("code "+filename+".json")


get_stuff(URL, 'movies')
