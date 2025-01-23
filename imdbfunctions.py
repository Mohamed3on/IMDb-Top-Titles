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


def process_movie(movie, scores, min_score, min_ratio):
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

    # Get the show name
    show_name_element = soup.select_one("h3.ipc-title__text")
    show_name = show_name_element.text.strip() if show_name_element else "Unknown Show"

    episode_links = soup.select(".ep-title > a")

    with ThreadPoolExecutor() as executor:
        episodes = list(executor.map(process_episode, enumerate(episode_links, 1)))

    # Filter episodes based on min_ratio
    filtered_episodes = [ep for ep in episodes if ep and ep["ratio"] >= min_ratio]

    return {"show_name": show_name, "episodes": filtered_episodes}


def process_episode(indexed_ep_link):
    index, ep_link = indexed_ep_link
    episode_id = ep_link["href"].split("/")[2]
    name = ep_link.text.strip()
    episode_link = f"https://www.imdb.com{ep_link['href']}"

    result = get_ep_score(episode_id)
    if not result:
        return None

    _, score, ratings_sum = result
    episode_ratio = score / ratings_sum
    calculated_score = round(score * episode_ratio)

    return {
        "number": index,
        "name": name,
        "score": calculated_score,
        "ratio": round(episode_ratio, 2),
        "link": episode_link,
    }


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
