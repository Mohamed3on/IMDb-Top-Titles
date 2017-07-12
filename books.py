import operator

from selenium import webdriver

import commonfunctions
import goodreadsfunctions


def setup_driver():
    options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    thedriver = webdriver.Chrome(
        "C:/Users/Mohamed/chromedriver.exe", chrome_options=options)
    return thedriver


def savebooks(books, name):
    sorteddata = sorted(
        books.items(), key=operator.itemgetter(1), reverse=True)
    commonfunctions.savescores(sorteddata, 'books/' + name)


def categorized_books(genre='programming', minscore=200, maxconsecutivebypassed=10):
    driver = setup_driver()
    driver = goodreadsfunctions.goodreads_login(driver)
    url = "https://www.goodreads.com/shelf/show/" + genre
    books = goodreadsfunctions.getCategorizedBooks(
        url, driver, minscore=minscore, maxconsecutivebypassed=maxconsecutivebypassed)
    driver.close()
    savebooks(books, genre)


def generalbooks():
    driver = setup_driver()
    mostread = goodreadsfunctions.getPopularBooks(
        "https://www.goodreads.com/book/most_read?category=all&country=all&duration=y", driver)
    morethanmillion = goodreadsfunctions.getPopularBooks(
        "https://www.goodreads.com/list/show/35080.One_million_ratings_", driver)
    driver.close()
    combined = {**morethanmillion, **mostread}
    savebooks(combined, 'generalbooks')


categorized_books('economics', 5000)
