import bs4
import time
import login


def getPopularBooks(url, driver):
    books = {}
    driver.get(url)
    soup = bs4.BeautifulSoup(driver.page_source, "lxml")
    seen = 1
    for book in soup.find_all("a", class_="bookTitle"):
        title = book.text.strip('\n')
        href = "https://www.goodreads.com" + book["href"]
        score = getBookScore(href, driver)[0]
        print(str(seen) + ': ' + title)
        print(score)
        books[title] = score
        seen += 1
    return books


def goodreads_login(driver):
    driver.get('https://www.goodreads.com/user/sign_in')
    mailinput = driver.find_element_by_id('user_email')
    passinput = driver.find_element_by_id('user_password')
    mailinput.send_keys(login.email)
    passinput.send_keys(login.password)
    driver.find_element_by_name('next').click()
    return driver


def getCategorizedBooks(baseurl, driver, bypassed=0, books={}, page=1, minscore=0, maxconsecutivebypassed=10, minRatio=0.4):
    count = 0
    url = baseurl + '?page=' + str(page)
    driver.get(url)
    soup = bs4.BeautifulSoup(driver.page_source, "lxml")
    booksContainer = soup.find("div", class_="leftContainer")
    bookList = booksContainer.find_all("div", class_="elementList")
    for element in bookList:
        book = element.find("a", "bookTitle")
        author = "Unknown"
        rating = element.find("div", "ratingStars")
        if 'hasRating' in rating.get("class"):
            continue
        if element.find("a", class_="authorName"):
            author = element.find("a", class_="authorName").text
        try:
            title = book.text.strip('\n') + ' by ' + author
            href = "https://www.goodreads.com" + book["href"]
        except:
            break
        score, totalvotes = getBookScore(href, driver)
        cutoff = max(totalvotes * minRatio, minscore)
        if score > cutoff:
            count = count + 1
            print(str(count) + ': ' + title)
            print(score)
            books[title] = score, href
            bypassed = 0
        else:
            bypassed += 1
            print("score of (" + title + ") is too low, now " +
                  str(bypassed) + " books bypassed")
        if bypassed >= maxconsecutivebypassed:
            return books

    getCategorizedBooks(baseurl, driver, bypassed,
                        books, int(page) + 1, minscore, maxconsecutivebypassed, minRatio)

    return books


def ClickButtonAndGetScores(div_id, driver, sleep_period):
    try:
        driver.find_element_by_id(div_id).click()
        if sleep_period != 0:
            time.sleep(sleep_period)
        html = driver.page_source
        soup = bs4.BeautifulSoup(html, "lxml")
        scores = []
        for td in soup.find_all("td", width="90"):
            s = td.text
            scores.append(int(s[s.find("(") + 1:s.find(")")]))
        return scores
    except:
        return []


def getBookScore(url, driver):
    driver.get(url)
    scores = ClickButtonAndGetScores("rating_details", driver, 0)
    if scores == []:
        scores = ClickButtonAndGetScores("rating_details", driver, 0.5)
    score = scores[0] - scores[-1]
    return score, sum(scores)
