import bs4

import login


def getPopularBooks(url, driver):
    books = {}
    driver.get(url)
    soup = bs4.BeautifulSoup(driver.page_source, "lxml")
    seen = 1
    for book in soup.find_all("a", class_="bookTitle"):
        title = book.text.strip('\n')
        href = "https://www.goodreads.com" + book["href"]
        score, totalVotes = getBookScore(href, driver)
        print(str(seen) + ': ' + title)
        print(score)
        books[title] = score
        seen += 1

    driver.close()
    return books


def goodreads_login(driver):
    driver.get('https://www.goodreads.com/user/sign_in')
    mailinput = driver.find_element_by_id('user_email')
    passinput = driver.find_element_by_id('user_password')
    mailinput.send_keys(login.email)
    passinput.send_keys(login.password)
    driver.find_element_by_name('next').click()
    return driver


def getCategorizedBooks(baseurl, driver, seen=0, bypassed=0, books={}, page=1, minScore=0):
    maxconsecutivebypassed = 10
    url = baseurl + '?page=' + str(page)
    driver.get(url)
    soup = bs4.BeautifulSoup(driver.page_source, "lxml")
    for element in soup.find_all("div", class_="elementList"):
        seen += 1
        if seen % 50 == 1 and seen > 50:
            break
        book = element.find("a", "bookTitle")
        author = element.find("a", class_="authorName").text
        title = book.text.strip('\n') + ' by ' + author
        href = "https://www.goodreads.com" + book["href"]
        score, totalvotes = getBookScore(href, driver)
        cutoff = max(totalvotes * 0.4, minScore)
        if score > cutoff:
            print(str(seen) + ': ' + title)
            print(score)
            books[title] = score
            bypassed = 0
        else:
            bypassed += 1
            print("score (" + str(score) + ") is too low, now " +
                  str(bypassed) + " books bypassed")
        if bypassed >= maxconsecutivebypassed:
            return books

    getCategorizedBooks(baseurl, driver, seen, bypassed,
                        books, int(page) + 1, minScore)

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
