import json
from selenium import webdriver
from bs4 import BeautifulSoup
import urllib.request


def getScore(id):
    url = 'http://www.imdb.com/title/' + id + '/ratings'
    with urllib.request.urlopen(url) as url:
        r = url.read()
    soup = BeautifulSoup(r, "lxml")
    ratings = []
    previous = 1
    for i in soup.find_all("a", class_="main"):
        name = i.string
        print(name)

    for link in soup.find_all('td'):
        if link.get('nowrap') == "1":
            ratings.append(int(previous))
        else:
            previous = link.string
        if len(ratings) == 10: break
    score = ratings[0] + ratings[1] - ratings[-1] - ratings[-2]
    print("score: ", score)
    return name, score


# if found item with class next-page go to that item's href and append the scores, else return the scores
def getMovies(scores, url, minScore):
    with urllib.request.urlopen(url) as url:
        r = url.read()
    soup = BeautifulSoup(r, "lxml")
    for ana in soup.find_all("span", class_="lister-item-header"):
        url = ana.a["href"]
        id = url.split('/')[2]
        moviename = ana.a.text
        if moviename not in scores:
            name, score = getScore(id)
            if score > minScore:
                scores[name] = score
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


def savescores(scores, name):
    name = name + '.json'
    with open(name, 'w') as fp:
        json.dump(scores, fp)


def getBookScore(url, driver):
    driver.get(url)
    driver.find_element_by_id("rating_details").click()
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")
    scores = []
    for td in soup.find_all("td", width="90"):
        s = td.text
        scores.append(int(s[s.find("(") + 1:s.find(")")]))
    return scores[0] - scores[-1]


def getBooks(books, url):
    chromeOptions = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chromeOptions.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome("C:/Users/Mohamed/chromedriver.exe", chrome_options=chromeOptions)
    with urllib.request.urlopen(url) as url:
        r = url.read()
    soup = BeautifulSoup(r, "lxml")
    count = 1
    for book in soup.find_all("a", class_="bookTitle"):
        title = book.text
        if title not in books:
            href = "https://www.goodreads.com" + book["href"]
            score = getBookScore(href, driver)
            print(count, ':', title)
            print(score)
            books[title] = score
            count += 1
        else:
            continue
    driver.close()
    return books
