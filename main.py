import functions as imdb
import json
import operator
minScore=10000
scores={}
data = imdb.getMovies(scores,'http://www.imdb.com/search/title?count=250&num_votes=30000,&sort=num_votes,desc&view=simple&page=1&ref_=adv_nxt',minScore)
sorteddata = sorted(data.items(), key=operator.itemgetter(1),reverse=True)
with open('sorted.json', 'w') as fp:
    json.dump(sorteddata, fp)
