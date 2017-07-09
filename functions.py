import json
import operator
import urllib.request
from pathlib import Path

import bs4


# if found item with class next-page go to that item's href and append the scores, else return the scores
def getMovies(scores, url, minScore, bypassed=0):
    soup = getSoup(url)
    bypassed = 0
    for movie in soup.find_all("span", class_="lister-item-header"):
        if bypassed > 20:
            savescores(scores, 'scores')
            return scores
        for title in movie.find_all("a"):
            url = title["href"]
            moviename = title.text
        id = url.split('/')[2]
        if moviename not in scores:
            name, score = getTitleScore(id)
            if score > minScore:
                bypassed = 0
                if name[0] == "\"" and name[-1] == "\"":
                    name = name[1:-1]
                scores[name] = score, id
                print(name, ":", str(score))
            else:
                bypassed += 1
                print("bypassed count:", str(bypassed))
        else:
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
        return getMovies(scores, nexturl, minScore, bypassed)


def getSoup(url):
    with urllib.request.urlopen(url) as url:
        r = url.read()
    return bs4.BeautifulSoup(r, "lxml")


def getTitleScore(id):
    url = 'http://www.imdb.com/title/' + id + '/ratings'
    soup = getSoup(url)
    ratings = []
    previous = 1
    for i in soup.find_all("a", class_="main"):
        name = i.string

    for link in soup.find_all('td'):
        if link.get('nowrap') == "1":
            if (previous != "Average"):
                ratings.append(int(previous))
            else:
                return name, 0
        else:
            previous = link.string
        if len(ratings) == 10:
            break
    score = ratings[0] + ratings[1] - ratings[-1] - ratings[-2]
    return name, score


def getEpisodes(id, startingSeason=0):
    url = 'http://www.imdb.com/title/' + id + '/eprate?ref_=tt_eps_rhs_sm'
    episodes = {}
    notselected = 0
    cutoff = 0.5
    soup = getSoup(url)
    title = soup.find("div", {"id": "tn15title"}).find(
        "h1").text.split("\"")[1]
    table = soup.find("table")
    position = 1
    for ep in table.find_all("tr"):
        if position == 1:
            position += 1
            continue
        if notselected >= 10:
            break
        href = ep.find("a")["href"]
        id = href.split('/')[2]
        episode = ep.find("td").text
        if int(episode.split('.')[0]) < startingSeason:
            print(episode)
            continue
        episode = episode.replace(u'\xa0', u'')
        name, score, sum = getEpscore(id)
        if score / sum > cutoff:
            notselected = 0
            print(episode, name, score)
            episodes[str(episode)] = score, name

        else:
            notselected += 1
            print("Not selected: " + str(notselected))
            continue
    return episodes, title


def getEpscore(id):
    url = 'http://www.imdb.com/title/' + id + '/ratings'
    soup = getSoup(url)
    ratings = []
    previous = 1
    for i in soup.find_all("a", class_="main"):
        name = i.string

    for link in soup.find_all('td'):
        if link.get('nowrap') == "1":
            ratings.append(int(previous))
        else:
            previous = link.string
        if len(ratings) == 10:
            break
    score = ratings[0] + ratings[1] - ratings[-1] - ratings[-2]
    return name, score, sum(ratings)


def getPopularBooks(url, driver):
    books = {}
    soup = getSoup(url)
    bypassed = 1
    for book in soup.find_all("a", class_="bookTitle"):
        title = book.text.strip('\n')
        href = "https://www.goodreads.com" + book["href"]
        score = getBookScore(href, driver)
        print(str(bypassed) + ': ' + title)
        print(score)
        books[title] = score
        bypassed += 1

    driver.close()
    return books


def getCategorizedBooks(baseurl, driver, seen=1, bypassed=0, books={}, page=1):
    maxconsecutivebypassed = 10
    url = baseurl + '?page=' + str(page)
    driver.get(url)
    soup = bs4.BeautifulSoup(driver.page_source, "lxml")
    for book in soup.find_all("a", class_="bookTitle"):
        title = book.text.strip('\n')
        href = "https://www.goodreads.com" + book["href"]
        score, totalvotes = getBookScore(href, driver)
        minScore = totalvotes * 0.4
        if score > minScore:
            print(str(seen) + ': ' + title)
            print(score)
            books[title] = score
            bypassed = 0
        else:
            bypassed += 1
            print(str(seen) + ': ' + title)
            print("score: " + str(score) + " too low, now " +
                  str(bypassed) + " books bypassed")
            books[title] = score
        seen += 1
        if bypassed >= maxconsecutivebypassed:
            return books
    getCategorizedBooks(baseurl, driver, seen, bypassed, books, page + 1)
    return books


def getBookScore(url, driver):
    driver.get(url)
    driver.find_element_by_id("rating_details").click()
    html = driver.page_source
    soup = bs4.BeautifulSoup(html, "lxml")
    scores = []
    for td in soup.find_all("td", width="90"):
        s = td.text
        scores.append(int(s[s.find("(") + 1:s.find(")")]))
    score = scores[0] - scores[-1]
    return score, sum(scores)


def sortandsave(scores, name):
    scores = sortscores(scores)
    savescores(scores, name)


def savescores(scores, name):
    name += '.json'
    with open(name, 'w') as fp:
        json.dump(scores, fp)


def sortscores(scores):
    sortedscores = sorted(
        scores.items(), key=operator.itemgetter(1), reverse=True)
    return sortedscores


def loadfile(name):
    my_file = Path(name + ".json")
    if my_file.is_file():
        json1_file = open(name + '.json')
        json1_str = json1_file.read()
        file = json.loads(json1_str)
    else:
        file = {}
    return file
