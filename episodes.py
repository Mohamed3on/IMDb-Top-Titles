import json
import operator
import os
import sys

import imdbfunctions

SHOW_ID = sys.argv[1]
STARTING_SEASON = 1
MIN_RATIO = 0.50
MAX_NOT_SELECTED = 10


def pad_episode_numbers(episodes):
    padded_episodes = {}
    for episode, data in episodes.items():
        season, ep_num = episode.split(".")
        padded_ep_num = f"{season}.{ep_num.zfill(2)}"
        padded_episodes[padded_ep_num] = data
    return padded_episodes


def calculate_season_scores(episodes):
    seasons = {}
    for episode, values in episodes.items():
        score = values[0]  # Assuming score is the first element
        season = int(episode.split(".")[0])
        if season not in seasons:
            seasons[season] = []
        seasons[season].append(score)

    for season, scores in seasons.items():
        seasons[season] = sum(scores) / len(scores)

    return seasons


def save_results(results, show_name):
    # Create the 'shows' directory if it doesn't exist
    os.makedirs("shows", exist_ok=True)

    # Create the full file path
    file_path = os.path.join("shows", f"{show_name}.json")

    # Save the results
    with open(file_path, "w", encoding="utf8") as fp:
        json.dump(results, fp, ensure_ascii=False, indent=2)

    # Open the file
    os.system(f"cursor {file_path}")


def main():
    episodes, show_name = imdbfunctions.get_episodes(
        SHOW_ID,
        starting_season=STARTING_SEASON,
        min_ratio=MIN_RATIO,
        max_not_selected=MAX_NOT_SELECTED,
    )

    episodes = pad_episode_numbers(episodes)
    sorted_episodes = sorted(episodes.items(), key=lambda x: x[1][0], reverse=True)
    seasons = calculate_season_scores(episodes)

    results = {
        "Seasons": sorted(seasons.items(), key=operator.itemgetter(1), reverse=True),
        "EpisodesSorted": sorted_episodes,
        "EpisodesChronological": sorted(episodes.items(), key=operator.itemgetter(0)),
    }

    if results["Seasons"]:
        save_results(results, show_name)
        print(f"Results saved to shows/{show_name}.json and file opened.")
    else:
        print("No episodes found. Check your SHOW_ID and other parameters.")


if __name__ == "__main__":
    main()
