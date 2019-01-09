import operator

import commonfunctions
import imdbfunctions


def saveAndOpenScores(scores, name):
    file['EpisodesChronological'] = chronological
    commonfunctions.savescoresUnicode(scores, 'shows/' + name)
    open("shows/" + name + '.json')


SHOW_ID = 'tt0804503'
episodes, name = imdbfunctions.getEpisodes(
    SHOW_ID, startingSeason=1, minRatio=0.23, max_not_selected=13)
scores = sorted(episodes.items(), key=operator.itemgetter(1), reverse=True)
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
file['Seasons'] = sorted(
    seasons.items(), key=operator.itemgetter(1), reverse=True)
file['EpisodesSorted'] = scores
chronological = sorted(episodes.items(), key=operator.itemgetter(0))
if len(seasons.items()) > 0:
    saveAndOpenScores(file, name)
