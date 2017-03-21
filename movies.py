import json
from pathlib import Path

import functions as imdb
import operator

minScore = 10000
my_file = Path("sorted.json")
if my_file.is_file():
    json1_file = open('sorted.json')
    json1_str = json1_file.read()
    scores = json.loads(json1_str)
else:
    scores = {}
data = imdb.getMovies(scores,
                      'http://www.imdb.com/search/title?count=250&num_votes=30000,&sort=num_votes,desc&view=simple&page=15&ref_=adv_prv',
                      minScore)
sorteddata = sorted(data.items(), key=operator.itemgetter(1), reverse=True)
imdb.savescores(data, 'scores')
imdb.savescores(sorteddata, 'sortedtitles')
