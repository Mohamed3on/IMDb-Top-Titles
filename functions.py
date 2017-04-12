import cgi
import json
import operator
import urllib.request
from pathlib import Path

import bs4
from selenium import webdriver


# if found item with class next-page go to that item's href and append the scores, else return the scores
def getMovies(scores, url, minScore):
    soup = getSoup(url)
    bypassed = 0
    for movie in soup.find_all("span", class_="lister-item-header"):
        if bypassed > 30:
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
                scores[name] = score, id
                print(name)
                print(score)
            else:
                bypassed += 1
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
        return getMovies(scores, nexturl, minScore)


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
            ratings.append(int(previous))
        else:
            previous = link.string
        if len(ratings) == 10: break
    score = ratings[0] + ratings[1] - ratings[-1] - ratings[-2]
    return name, score


def getEpisodes(url):
    episodes = {}
    notselected = 0
    soup = getSoup(url)
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
        episode = episode.replace(u'\xa0', u'')
        name, score, sum = getEpscore(id)
        if score / sum > 0.5:
            notselected = 0
            print(episode, name, score)
            episodes[str(episode)] = score, name

        else:
            notselected += 1
            continue
    return episodes


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
        if len(ratings) == 10: break
    score = ratings[0] + ratings[1] - ratings[-1] - ratings[-2]
    return name, score, sum(ratings)


def getBooks(url):
    books = {}
    soup = getSoup(url)
    chromeOptions = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chromeOptions.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome("C:/Users/Mohamed/chromedriver.exe", chrome_options=chromeOptions)
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


def getBookScore(url, driver):
    driver.get(url)
    driver.find_element_by_id("rating_details").click()
    html = driver.page_source
    soup = bs4.BeautifulSoup(html, "lxml")
    scores = []
    for td in soup.find_all("td", width="90"):
        s = td.text
        scores.append(int(s[s.find("(") + 1:s.find(")")]))
    return scores[0] - scores[-1]

def sortandsave(scores,name):
    scores=sortscores(scores)
    savescores(scores,name)
def savescores(scores, name):
    name += '.json'
    with open(name, 'w') as fp:
        json.dump(scores, fp)
def sortscores(scores):
    scores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
    return scores

def loadfile(name):
    my_file = Path(name + ".json")
    if my_file.is_file():
        json1_file = open(name + '.json')
        json1_str = json1_file.read()
        file = json.loads(json1_str)
    else:
        file = {}
    return file


def unicodeToHTMLEntities(text):
    """Converts unicode to HTML entities.  For example '&' becomes '&amp;'."""
    text = cgi.escape(text).encode('ascii', 'xmlcharrefreplace')
    if str(text).find("&") == -1:
        return str(text)[1:]
    else:
        return str(text).split('b')[1].split("\'")[1]
