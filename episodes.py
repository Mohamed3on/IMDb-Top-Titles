import json
import os
import sys
import re

import urllib.parse

import imdbfunctions
import commonfunctions

MIN_RATIO = 0.51


def search_show(query):
    """Search for a TV show on IMDb and return its ID."""
    encoded_query = urllib.parse.quote(query)
    search_url = (
        f"https://www.imdb.com/search/title/?title={encoded_query}&title_type=tv_series"
    )

    soup = commonfunctions.getSoup(search_url)
    first_result = soup.select_one(".ipc-title-link-wrapper")

    if not first_result:
        return None

    show_id = first_result["href"].split("/")[2]
    show_name = first_result.text.strip()
    return show_id, show_name


def save_results(results, show_name):
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Create the 'shows' directory in the script directory
    shows_dir = os.path.join(script_dir, "shows")
    os.makedirs(shows_dir, exist_ok=True)

    # Create the full file path, keeping spaces in the file name
    file_path = os.path.join(shows_dir, f"{show_name}.json")

    # Save the results
    with open(file_path, "w", encoding="utf8") as fp:
        json.dump(results, fp, ensure_ascii=False, indent=2)

    os.open(file_path, os.O_RDONLY)


def main():
    if len(sys.argv) < 2:
        print("Usage: python episodes.py 'Show Name' [min_ratio]")
        sys.exit(1)

    show_name = sys.argv[1]
    args = sys.argv[2:]

    # Parse arguments
    min_ratio = MIN_RATIO

    for arg in args:
        if arg.replace(".", "").isdigit():  # Check if it's a number
            min_ratio = float(arg)

    # Search for the show
    search_result = search_show(show_name)
    if not search_result:
        print(f"No TV show found with name: {show_name}")
        return

    show_id, found_show_name = search_result
    print(f"Found show: {found_show_name} (ID: {show_id})")

    result = imdbfunctions.get_episodes(
        show_id,
        min_ratio=min_ratio,
    )

    if not result:
        print("No episodes found. Check your show name and other parameters.")
        return

    if not result["episodes"]:
        print("No episodes passed the minimum score threshold.")
        return

    # Remove the number part from the show name
    show_name = re.sub(r"^\d+\.\s*", "", result["show_name"]).strip()
    episodes = result["episodes"]

    results = {
        "EpisodesChronological": episodes,
        "EpisodesSorted": sorted(episodes, key=lambda x: x["score"], reverse=True),
    }

    save_results(results, show_name)


if __name__ == "__main__":
    main()
