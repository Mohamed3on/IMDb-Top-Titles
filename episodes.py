import json
import operator
import os
import commonfunctions
import imdbfunctions

SHOW_ID = "tt11198330"
STARTING_SEASON = 1

MIN_RATIO = 0.79
MAX_NOT_SELECTED = 10


def save_and_open_scores(scores_to_save, file_name):
    file["EpisodesChronological"] = chronological
    commonfunctions.savescoresUnicode(scores_to_save, "shows/" + name)
    os.system("code shows/" + json.dumps(file_name) + ".json")


episodes, name = imdbfunctions.get_episodes(
    SHOW_ID,
    starting_season=STARTING_SEASON,
    min_ratio=MIN_RATIO,
    max_not_selected=MAX_NOT_SELECTED,
)

scores = sorted(episodes.items(), key=operator.itemgetter(1), reverse=True)
seasons = {}
for episode in scores:
    season = episode[0].split(".")[0]
    score = episode[1][0]
    if season not in seasons:
        seasons[season] = score
    else:
        seasons[season] += score
for episode in scores:
    season = episode[0].split(".")[0]
    episodeNum = episode[0].split(".")[1]
    if len(episodeNum) == 1:
        newNum = season + "." + "0" + episodeNum
        oldNum = season + "." + episodeNum
        episodes[newNum] = episodes[oldNum]
        del episodes[oldNum]

file = {}
file["Seasons"] = sorted(seasons.items(), key=operator.itemgetter(1), reverse=True)
file["EpisodesSorted"] = scores
chronological = sorted(episodes.items(), key=operator.itemgetter(0))
if len(seasons.items()) > 0:
    save_and_open_scores(file, name)
