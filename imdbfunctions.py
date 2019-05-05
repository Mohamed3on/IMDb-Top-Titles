# if found item with class next-page go to that item's href and append the scores, else return the scores
from commonfunctions import savescores, getSoupFromHTML, getSoup, setup_driver
import login
import time


def getIMDBSoupAfterLogin(url):
    driver = setup_driver()
    driver.get(url)
    driver.find_element_by_id('imdb-signin-link').click()
    driver.find_element_by_link_text('Sign in with IMDb').click()
    mailinput = driver.find_element_by_name('email')
    passinput = driver.find_element_by_name('password')
    mailinput.send_keys(login.imdbEmail)
    passinput.send_keys(login.imdbPassword)
    driver.find_element_by_id('signInSubmit').click()
    time.sleep(2)
    content = driver.find_element_by_id(
        'pagecontent').get_attribute('innerHTML')
    soup = getSoupFromHTML(content)
    driver.close()
    return soup


def getMovies(scores, url, minScore=40000, bypassed=0, minratio=0.4, maxbypassed=10):
    soup = getIMDBSoupAfterLogin(url)
    moviename = ''
    for movie in soup.find_all("span", class_="lister-item-header"):
        if bypassed > maxbypassed:
            print("last title: " + moviename)
            savescores(scores, 'scores')
            return scores
        title = movie.find("a")
        url = title["href"]
        moviename = title.text
        titleID = url.split('/')[2]
        titleURL = 'http://www.imdb.com/title/' + titleID
        if titleURL not in scores:
            name, score, ratio = getTitleScore(titleID)
            scores[titleURL] = score, name, round(ratio, 2)
            if score > minScore and ratio > minratio:
                bypassed = 0
                print(name, ":", str(score))
            else:
                bypassed += 1
                print("bypassed count:", str(bypassed))
        else:
            print(moviename + " already in scores")
            continue
    savescores(scores, 'scores')
    nextdiv = soup.find("a", class_="next-page")
    if not nextdiv:
        print("end reached")
        return scores
    else:
        url = nextdiv["href"]
        nexturl = 'http://www.imdb.com' + url
        print("next page")
        return getMovies(scores, nexturl, minScore, bypassed, minratio, maxbypassed)


def getTitleScore(titleID):
    url = 'http://www.imdb.com/title/' + titleID + '/ratings'
    soup = getSoup(url)
    ratings = []
    i = soup.find("h3")
    name = i.find("a").text

    for bucket in soup.find_all('div', class_="leftAligned"):
        value = bucket.text.replace(',', '')
        if value.isdigit():
            ratings.append(int(value))
        else:
            continue
    score = ratings[0] + ratings[1] - ratings[-1] - ratings[-2]
    ratio = score / sum(ratings)
    if name[0] == "\"" and name[-1] == "\"":
        name = name[1:-1]
    return name.strip(), score, ratio


def getEpisodes(titleID, startingSeason=1, minRatio=0.4, max_not_selected=10):

    episodes = {}
    notselected = 0
    episodes, title = getSeason(
        startingSeason, titleID, notselected, minRatio, episodes, max_not_selected)
    return episodes, title


def getSeason(currentSeason, titleID, notselected, minRatio, episodes, max_not_selected=10):
    url = 'http://www.imdb.com/title/' + titleID + \
        '/episodes?season=' + str(currentSeason)
    soup = getSoup(url)
    title = soup.find("a", class_="subnav_heading").text
    episodeNumber = 0
    for ep in soup.find_all("div", class_="list_item"):
        if notselected >= max_not_selected:
            return episodes, title
        episodeNumber += 1
        episodeTitle = ep.find("a", {"itemprop": "name"})
        href = episodeTitle.attrs["href"]
        episodeID = href.split('/')[2]
        episode = str(currentSeason) + '.' + str(episodeNumber)
        result = getEpscore(episodeID)
        if result:
            name, score, ratingsSum = result
        else:
            return episodes, title
        episodeRatio = score / ratingsSum
        if episodeRatio > minRatio:
            notselected = 0
            print(episode, name, score)
            episodes[str(episode)] = score, name, round(episodeRatio, 2)

        else:
            notselected += 1
            print("Not selected " + str(notselected) +
                  ": " + episode + ' ' + name)
            continue

    next_season_link = soup.find("a", {"id": "load_next_episodes"})
    if next_season_link:
        next_season = currentSeason+1

        if ("Unknown Season" in next_season_link.text):
            next_season = -1
        return getSeason(next_season, titleID, notselected, minRatio, episodes, max_not_selected)
    else:
        return episodes, title


def getEpscore(titleID):
    url = 'http://www.imdb.com/title/' + titleID + '/ratings'
    soup = getSoup(url)
    ratings = []
    i = soup.find("h3")
    name = i.find("a").text

    for bucket in soup.find_all('div', class_="leftAligned"):
        value = bucket.text.replace(',', '')
        if value.isdigit():
            ratings.append(int(value))
        else:
            continue
    if len(ratings) < 1:
        return None
    else:
        score = ratings[0] + ratings[1] - ratings[-1] - ratings[-2]
        return name, score, sum(ratings)
