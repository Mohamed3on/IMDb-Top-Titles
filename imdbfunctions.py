"""
functions to get IMDB scores of titles
"""

# if found item with class next-page go to that item's href and append the scores,
# else return the scores
import json
import time
import concurrent.futures
from functools import partial
from concurrent.futures import ThreadPoolExecutor

from selenium.webdriver.common.by import By

import login
from commonfunctions import getSoup, getSoupFromHTML, savescores, setup_driver


def imdb_login(url):
    driver = setup_driver()
    driver.get("https://www.imdb.com/registration/signin")

    # Update the method to find elements
    driver.find_element(By.LINK_TEXT, "Sign In").click()
    time.sleep(0.5)

    driver.find_element(By.LINK_TEXT, "Sign in with IMDb").click()

    # Finding elements by name
    mailinput = driver.find_element(By.NAME, "email")
    passinput = driver.find_element(By.NAME, "password")

    # Input credentials and submit
    mailinput.send_keys(login.imdbEmail)
    passinput.send_keys(login.imdbPassword)
    driver.find_element(By.ID, "signInSubmit").click()

    time.sleep(1)

    # Reload the page and retrieve content
    driver.get(url)

    content = driver.find_element(
        By.CSS_SELECTOR, "ul.ipc-metadata-list"
    ).get_attribute("innerHTML")
    soup = getSoupFromHTML(content)

    # Close the driver
    driver.close()
    return soup


def get_imdb_soup_after_login(url):
    driver = setup_driver()
    driver.get(url)

    # Update the method to find elements
    driver.find_element(By.LINK_TEXT, "Sign In").click()
    time.sleep(0.5)

    driver.find_element(By.LINK_TEXT, "Sign in with IMDb").click()

    # Finding elements by name
    mailinput = driver.find_element(By.NAME, "email")
    passinput = driver.find_element(By.NAME, "password")

    # Input credentials and submit
    mailinput.send_keys(login.imdbEmail)
    passinput.send_keys(login.imdbPassword)
    time.sleep(3)
    driver.find_element(By.ID, "signInSubmit").click()

    # Reload the page and retrieve content
    driver.get(url)
    content = driver.find_element(
        By.CSS_SELECTOR, "ul.ipc-metadata-list"
    ).get_attribute("innerHTML")
    soup = getSoupFromHTML(content)

    # Close the driver
    driver.close()
    return soup


def get_movies(scores, url, min_score=40000, bypassed=0, min_ratio=0.4, maxbypassed=10):
    soup = imdb_login(url)
    movies = soup.find_all("a", class_="ipc-title-link-wrapper")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        movie_data = list(
            executor.map(
                partial(
                    process_movie,
                    scores=scores,
                    min_score=min_score,
                    min_ratio=min_ratio,
                ),
                movies,
            )
        )

    for data in movie_data:
        if data:
            title_url, score, name, ratio = data
            scores[title_url] = score, name, round(ratio, 2)
            if score > min_score and ratio > min_ratio:
                bypassed = 0
                print(name, ":", str(score))
            else:
                bypassed += 1
                print("bypassed count:", str(bypassed))

        if bypassed > maxbypassed:
            print("last title: " + name)
            savescores(scores, "scores")
            return scores

    savescores(scores, "scores")
    nextdiv = soup.find("a", class_="next-page")
    if not nextdiv:
        print("end reached")
        return scores
    else:
        url = nextdiv["href"]
        nexturl = "https://www.imdb.com" + url
        print("next page")
        return get_movies(scores, nexturl, min_score, bypassed, min_ratio, maxbypassed)


def process_movie(
    movie,
    scores,
):
    url = movie["href"]
    moviename = movie.text
    title_id = url.split("/")[2]
    title_url = "http://www.imdb.com/title/" + title_id
    if title_url not in scores:
        name, score, ratio = get_title_score(title_id)
        return title_url, score, name, ratio
    else:
        print(moviename + " already in scores")
        return None


def get_title_score(title_id):
    url = "http://www.imdb.com/title/" + title_id + "/ratings"
    soup = getSoup(url)
    ratings = []
    name = soup.find("h2").text

    next_data_script = soup.find("script", id="__NEXT_DATA__")
    if next_data_script:
        next_data_json = next_data_script.string
        next_data = json.loads(next_data_json)

        # Extract histogram data
        histogram_data = (
            next_data.get("props", {})
            .get("pageProps", {})
            .get("contentData", {})
            .get("histogramData", {})
        )

        # Process histogram values
        rating_arr = histogram_data.get("histogramValues", [])
        sorted_arr = sorted(rating_arr, key=lambda x: x.get("rating", 0), reverse=True)

        # Extract vote counts
        ratings = [rating.get("voteCount", 0) for rating in sorted_arr]

    else:
        ratings = []
        print('No script element found for title "' + title_id + '"')

    abs_score = ratings[0] + ratings[1] - ratings[-1] - ratings[-2]
    ratio = abs_score / sum(ratings)
    score = round(abs_score * ratio)
    print(name, score, ratio)

    if name[0] == '"' and name[-1] == '"':
        name = name[1:-1]
    return name.strip(), score, ratio


def get_episodes(title_id, min_ratio=0.4):
    url = f"https://www.imdb.com/search/title/?series={title_id}&sort=release_date,asc&count=250"
    soup = getSoup(url)

    # Find the __NEXT_DATA__ script tag
    next_data_script = soup.find("script", id="__NEXT_DATA__")
    if not next_data_script:
        print(f"Could not find __NEXT_DATA__ script tag for title {title_id}")
        return {"show_name": "Unknown Show", "episodes": []}

    # Parse the JSON data
    try:
        data = json.loads(next_data_script.string)
        results = data["props"]["pageProps"]["searchResults"]["titleResults"]
        episode_items = results.get("titleListItems", [])

        # Attempt to get show name from searchInput first (more robust)
        show_name = (
            data.get("props", {})
            .get("pageProps", {})
            .get("searchInput", {})
            .get("series", {})
            .get("include", [{}])[0]
            .get("text")
        )

        # If not found, try getting it from the first episode's series info
        if not show_name and episode_items:
            show_name = episode_items[0].get("series", {}).get("titleText")

        # Fallback if still not found
        if not show_name:
            show_name = "Unknown Show"  # Fallback name
            print(f"Could not reliably determine show name for {title_id}")

    except (json.JSONDecodeError, KeyError, IndexError) as e:  # Added IndexError
        print(f"Error parsing __NEXT_DATA__ JSON or finding keys: {e}")
        return {"show_name": "Unknown Show", "episodes": []}

    # Helper function to process a single episode item
    def _process_single_episode(indexed_item):
        index, item = indexed_item
        try:
            episode_id = item.get("titleId")
            name = item.get("titleText")
            episode_link = f"https://www.imdb.com/title/{episode_id}/"

            if not episode_id or not name:
                print(f"Skipping item at index {index} due to missing ID or name")
                return None

            # Get score using the existing function
            score_result = get_ep_score(episode_id)
            print(
                f"Score result for {episode_id}: {score_result}"
            )  # Debug score result
            if not score_result:
                print(f"Skipping episode {episode_id} ('{name}') due to scoring error")
                return None

            # Unpack results including season and episode numbers
            _, score, ratings_sum, season_number, episode_number = score_result
            if ratings_sum == 0:
                episode_ratio = 0
                calculated_score = 0
                print(f"Warning: Episode {episode_id} ('{name}') has zero rating sum.")
            else:
                episode_ratio = score / ratings_sum
                calculated_score = round(score * episode_ratio)

            print(
                f"Calculated score: {calculated_score}, Ratio: {episode_ratio:.2f}, Sum: {ratings_sum}"
            )  # Debug calculated values

            # Return episode data if ratio is sufficient
            if episode_ratio >= min_ratio:
                print(
                    f"Adding episode {episode_id} ('{name}') - Ratio {episode_ratio:.2f} >= {min_ratio}"
                )  # Debug adding episode
                return {
                    "name": name,
                    "score": calculated_score,
                    "ratio": round(episode_ratio, 2),
                    "link": episode_link,
                    "season_number": season_number,
                    "episode_number": episode_number,
                }
            else:
                print(
                    f"Skipping episode {episode_id} ('{name}') - Ratio {episode_ratio:.2f} < {min_ratio}"
                )  # Debug skipping episode
                return None  # Episode doesn't meet min_ratio
        except Exception as e:
            print(f"Error processing episode item at index {index}: {item}. Error: {e}")
            return None  # Return None on error

    # Use ThreadPoolExecutor to process episodes in parallel
    episodes = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Map the helper function over the enumerated episode items
        results = executor.map(_process_single_episode, enumerate(episode_items, 1))
        # Filter out None results (from errors or ratio filtering)
        episodes = [ep for ep in results if ep is not None]

    # Sort episodes by number just in case parallel execution messed up the order
    print(episodes)
    episodes.sort(
        key=lambda x: (
            x["season_number"] if x["season_number"] is not None else float("-inf"),
            x["episode_number"] if x["episode_number"] is not None else float("-inf"),
        )
    )

    return {"show_name": show_name, "episodes": episodes}


def get_ep_score(title_id):
    url = "https://www.imdb.com/title/" + title_id + "/ratings"

    soup = getSoup(url)
    season_number = None  # Initialize season number
    episode_number = None  # Initialize episode number

    try:
        ratings = []
        name = soup.find("h3").find("a").text

        for bucket in soup.find_all("div", class_="leftAligned"):
            value = bucket.text.replace(",", "")
            if value.isdigit():
                ratings.append(int(value))
            else:
                continue

        if len(ratings) < 1:
            raise ValueError("No ratings found")
    except (AttributeError, ValueError):
        # Get the script content with the JSON data
        script_element = soup.find("script", {"id": "__NEXT_DATA__"})
        if not script_element:
            print("No script element found", title_id)
            return None
        script_content = script_element.string

        # Parse the JSON data
        data = json.loads(script_content)

        # Extract the ratings from the JSON data
        histogram_values = data["props"]["pageProps"]["contentData"]["histogramData"][
            "histogramValues"
        ]

        sorted_values = sorted(
            histogram_values, key=lambda x: x["rating"], reverse=True
        )
        ratings = [value["voteCount"] for value in sorted_values]

        name = data["props"]["pageProps"]["contentData"]["entityMetadata"]["titleText"][
            "text"
        ]

        # Extract season and episode number from series info if available
        series_info = (
            data.get("props", {})
            .get("pageProps", {})
            .get("contentData", {})
            .get("entityMetadata", {})
            .get("series", {})
        )
        if series_info and isinstance(
            series_info, dict
        ):  # Check if series_info exists and is a dict
            episode_num_info = series_info.get("episodeNumber")
            if episode_num_info and isinstance(
                episode_num_info, dict
            ):  # Check if episodeNumber info exists and is a dict
                season_number = episode_num_info.get("seasonNumber")
                episode_number = episode_num_info.get("episodeNumber")

    if len(ratings) < 1:
        return None

    score = ratings[0] + ratings[1] - ratings[-1] - ratings[-2]
    # Return name, score, sum of ratings, season number, and episode number
    return name, score, sum(ratings), season_number, episode_number
