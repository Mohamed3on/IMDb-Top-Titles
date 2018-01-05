# if found item with class next-page go to that item's href and append the scores, else return the scores
from commonfunctions import savescores, getSoup


def getMovies(scores, url, minScore=40000, bypassed=0, minratio=0.4, maxbypassed=10):
    soup = getSoup(url)
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
        if moviename not in scores:
            name, score, ratio = getTitleScore(titleID)
            scores[name] = score, 'http://www.imdb.com/title/' + titleID
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
    desc = soup.find("div", class_="desc")
    nextdiv = desc.find("a", class_="next-page")
    if not nextdiv:
        print("end reached")
        return scores
    else:
        url = nextdiv["href"]
        nexturl = 'http://www.imdb.com/search/title' + url
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


def getEpisodes(titleID, startingSeason=1, minRatio=0.4):

    episodes = {}
    notselected = 0
    episodes, title = getSeason(
        startingSeason, titleID, notselected, minRatio, episodes)
    return episodes, title


def getSeason(currentSeason, titleID, notselected, minRatio, episodes):
    url = 'http://www.imdb.com/title/' + titleID + \
        '/episodes?season=' + str(currentSeason)
    soup = getSoup(url)
    title = soup.find("a", class_="subnav_heading").text
    episodeNumber = 0
    for ep in soup.find_all("div", class_="list_item"):
        if notselected >= 10:
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
            episodes[str(episode)] = score, name

        else:
            notselected += 1
            print("Not selected " + str(notselected) +
                  ": " + episode + ' ' + name)
            continue
    if soup.find("a", {"id": "load_next_episodes"}):
        return getSeason(currentSeason + 1, titleID, notselected, minRatio, episodes)
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
