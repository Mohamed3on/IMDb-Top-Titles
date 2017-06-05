import operator

import functions

scores, name = functions.getEpisodes(
    'tt1856010', 5)
scores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
seasons = {}
for episode in scores:
    season = episode[0].split('.')[0]
    score = episode[1][0]
    if season not in seasons:
        seasons[season] = score
    else:
        seasons[season] += score
file = {}
file['Seasons'] = sorted(seasons.items(), key=operator.itemgetter(1), reverse=True)
file['Episodes'] = scores
print(file)
functions.savescores(file, name)
