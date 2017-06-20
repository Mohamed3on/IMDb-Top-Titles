import operator

import functions

episodes, name = functions.getEpisodes(
    'tt0306414')
scores = sorted(episodes.items(), key=operator.itemgetter(1), reverse=True)
functions.savescores(episodes, 'test')
seasons = {}
for episode in scores:
    season = episode[0].split('.')[0]
    score = episode[1][0]
    if season not in seasons:
        seasons[season] = score
    else:
        seasons[season] += score
for episode in scores:
    season = episode[0].split('.')[0]
    episodeNum = episode[0].split('.')[1]
    if len(episodeNum) == 1:
        newNum = season + '.' + '0' + episodeNum
        oldNum = season + '.' + episodeNum
        episodes[newNum] = episodes[oldNum]
        del episodes[oldNum]

file = {}
file['Seasons'] = sorted(seasons.items(), key=operator.itemgetter(1), reverse=True)
file['EpisodesSorted'] = scores
chronological = sorted(episodes.items(), key=operator.itemgetter(0))
file['EpisodesChronological'] = chronological

print(file)
functions.savescores(file, name)
