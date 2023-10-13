"""
functions to get IMDB scores of titles
"""

# if found item with class next-page go to that item's href and append the scores,
# else return the scores
import time
from commonfunctions import savescores, getSoupFromHTML, getSoup, setup_driver

import login
import json


def get_imdb_soup_after_login(url):
    driver = setup_driver()
    driver.get(url)
    driver.find_element_by_link_text("Sign In").click()
    time.sleep(0.5)

    driver.find_element_by_link_text("Sign in with IMDb").click()
    mailinput = driver.find_element_by_name("email")
    passinput = driver.find_element_by_name("password")
    mailinput.send_keys(login.imdbEmail)
    passinput.send_keys(login.imdbPassword)
    driver.find_element_by_id("signInSubmit").click()
    time.sleep(1)
    driver.get(url)
    content = driver.find_element_by_id("pagecontent").get_attribute("innerHTML")
    soup = getSoupFromHTML(content)
    driver.close()
    return soup


def get_movies(scores, url, min_score=40000, bypassed=0, min_ratio=0.4, maxbypassed=10):
    soup = get_imdb_soup_after_login(url)
    moviename = ""
    for movie in soup.find_all("span", class_="lister-item-header"):
        if bypassed > maxbypassed:
            print("last title: " + moviename)
            savescores(scores, "scores")
            return scores
        title = movie.find("a")
        url = title["href"]
        moviename = title.text
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
    i = soup.find("h3")
    name = i.find("a").text

    for bucket in soup.find_all("div", class_="leftAligned"):
        value = bucket.text.replace(",", "")
        if value.isdigit():
            ratings.append(int(value))
        else:
            continue
    abs_score = ratings[0] + ratings[1] - ratings[-1] - ratings[-2]
    ratio = abs_score / sum(ratings)

    score = round(abs_score * ratio)

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
    episode_number = 0
    for ep in soup.find_all("a", class_="bglHll"):
        if notselected >= max_not_selected:
            return episodes, title
        episode_number += 1
        href = ep.attrs["href"]
        episode_id = href.split("/")[2]
        episode = str(current_season) + "." + str(episode_number)
        result = get_ep_score(episode_id)
        if result:
            name, score, ratings_sum = result
        else:
            return episodes, title
        episode_ratio = score / ratings_sum

        if episode_ratio > min_ratio:
            notselected = 0
            calculated_score = round(score * episode_ratio)
            print(episode, name, calculated_score)
            episodes[str(episode)] = calculated_score, name, round(episode_ratio, 2)

        else:
            notselected += 1
            print("Not selected " + str(notselected) + ": " + episode + " " + name)
            continue

    next_season_link = soup.find("a", {"id": "load_next_episodes"})
    if next_season_link:
        next_season = current_season + 1

        if "Unknown Season" in next_season_link.text:
            next_season = -1
        return get_season(
            next_season, title_id, notselected, min_ratio, episodes, max_not_selected
        )

    return episodes, title


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
