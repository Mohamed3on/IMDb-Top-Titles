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
def getMovies(scores,url ,minScore):
    with urllib.request.urlopen(url) as url:
        r = url.read()
    soup = BeautifulSoup(r, "lxml")
    for ana in soup.find_all("span", class_="lister-item-header"):
        url = ana.a["href"]
        id = url.split('/')[2]
        name, score = getScore(id)
        if score>minScore:
            scores[name] = score
    desc = soup.find("div", class_="desc")
    nextdiv = desc.find("a", class_="next-page")
    if not nextdiv:
        print("end reached")
        return scores
    else:
        url = nextdiv["href"]
        nexturl = 'http://www.imdb.com/search/title' + url
        return getMovies(scores, nexturl)


def test(url):
    with urllib.request.urlopen(url) as url:
        r = url.read()
    soup = BeautifulSoup(r, "lxml")
    desc = soup.find("div", class_="desc")
    next = desc.find("a", class_="next-page")
    if next:
        url = next["href"]
        nexturl = 'http://www.imdb.com/search/title' + url
        print(nexturl)
    else:
        print('end')
