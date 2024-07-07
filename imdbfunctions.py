"""
functions to get IMDB scores of titles
"""

# if found item with class next-page go to that item's href and append the scores,
# else return the scores
import json
import time
import concurrent.futures
from functools import partial

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
    # soup = getSoup(url)
    moviename = ""
    for movie in soup.find_all("a", class_="ipc-title-link-wrapper"):
        if bypassed > maxbypassed:
            print("last title: " + moviename)
            savescores(scores, "scores")
            return scores

        url = movie["href"]
        moviename = movie.text
        title_id = url.split("/")[2]
        title_url = "http://www.imdb.com/title/" + title_id
        if title_url not in scores:
            name, score, ratio = get_title_score(title_id)
            scores[title_url] = score, name, round(ratio, 2)
            if score > min_score and ratio > min_ratio:
                bypassed = 0
                print(name, ":", str(score))
            else:
                bypassed += 1
                print("bypassed count:", str(bypassed))
        else:
            print(moviename + " already in scores")
            continue
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


def get_episodes(title_id, starting_season=1, min_ratio=0.4, max_not_selected=10):
    episodes = {}
    notselected = 0
    episodes, title = get_season(
        starting_season, title_id, notselected, min_ratio, episodes, max_not_selected
    )
    return episodes, title


def get_season(
    current_season, title_id, notselected, min_ratio, episodes, max_not_selected=10
):
    url = (
        "http://www.imdb.com/title/"
        + title_id
        + "/episodes?season="
        + str(current_season)
    )
    soup = getSoup(url)
    title = soup.find("h2").text

    episode_elements = soup.find_all("h4", {"data-testid": "slate-list-card-title"})

    # Create a partial function with fixed arguments
    process_episode_partial = partial(
        process_episode, current_season=current_season, min_ratio=min_ratio
    )

    # Use ThreadPoolExecutor to parallelize episode processing
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(
            executor.map(process_episode_partial, enumerate(episode_elements, 1))
        )

    # Process results
    for result in results:
        if result:
            episode, calculated_score, name, episode_ratio = result
            episodes[str(episode)] = calculated_score, name, round(episode_ratio, 2)
            print(episode, name, calculated_score)
            notselected = 0
        else:
            notselected += 1
            if notselected >= max_not_selected:
                return episodes, title

    # Check for next season
    next_season_link = soup.find("button", {"id": "next-season-btn"})
    if next_season_link:
        next_season = current_season + 1
        if "Unknown Season" in next_season_link.text:
            next_season = -1
        return get_season(
            next_season, title_id, notselected, min_ratio, episodes, max_not_selected
        )

    return episodes, title


def process_episode(enum_ep, current_season, min_ratio):
    episode_number, ep = enum_ep
    href = ep.find("a")["href"]
    episode_id = href.split("/")[2]
    episode = f"{current_season}.{episode_number}"

    result = get_ep_score(episode_id)
    if not result:
        return None

    name, score, ratings_sum = result
    episode_ratio = score / ratings_sum

    if episode_ratio > min_ratio:
        calculated_score = round(score * episode_ratio)
        return episode, calculated_score, name, episode_ratio

    print("bypassed", episode, name, score, episode_ratio)
    return None


def get_ep_score(title_id):
    url = "https://www.imdb.com/title/" + title_id + "/ratings"

    soup = getSoup(url)

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

    if len(ratings) < 1:
        return None

    score = ratings[0] + ratings[1] - ratings[-1] - ratings[-2]
    return name, score, sum(ratings)
