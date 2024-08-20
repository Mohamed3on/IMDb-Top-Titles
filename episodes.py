import json
import os
import sys
import re
import subprocess

import imdbfunctions

SHOW_ID = sys.argv[1]
MIN_RATIO = 0.65


def save_results(results, show_name):
    # Create the 'shows' directory if it doesn't exist
    os.makedirs("shows", exist_ok=True)

    # Create the full file path, keeping spaces in the file name
    file_path = os.path.join("shows", f"{show_name}.json")

    # Get the absolute path
    abs_file_path = os.path.abspath(file_path)

    # Save the results
    with open(abs_file_path, "w", encoding="utf8") as fp:
        json.dump(results, fp, ensure_ascii=False, indent=2)

    # Open the file using the appropriate command based on the operating system
    if sys.platform.startswith("darwin"):  # macOS
        subprocess.run(["open", abs_file_path])
    elif sys.platform.startswith("win"):  # Windows
        os.startfile(abs_file_path)
    else:  # Linux and other Unix-like systems
        subprocess.run(["xdg-open", abs_file_path])

    print(f"Results saved to {abs_file_path} and file opened.")


def main():
    result = imdbfunctions.get_episodes(
        SHOW_ID,
        min_ratio=MIN_RATIO,
    )

    if not result or not result["episodes"]:
        print("No episodes found. Check your SHOW_ID and other parameters.")
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
