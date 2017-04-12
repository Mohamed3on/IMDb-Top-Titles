import functions
scores = functions.getEpisodes(
    'http://www.imdb.com/title/tt2861424/eprate?ref_=tt_eps_rhs_sm')
scores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
functions.savescores(scores, 'rick and morty')
