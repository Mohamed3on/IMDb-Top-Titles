# if found item with class next-page go to that item's href and append the scores, else return the scores
from commonfunctions import savescores, getSoup


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