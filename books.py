import operator

from selenium import webdriver

import commonfunctions
import goodreadsfunctions


def setupDriver():
    options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    thedriver = webdriver.Chrome(
        "C:/Users/Mohamed/chromedriver.exe", chrome_options=options)
    return thedriver


def savebooks(books, name):
    sorteddata = sorted(
        books.items(), key=operator.itemgetter(1), reverse=True)
    commonfunctions.savescores(sorteddata, name + 'books')


def programmingbooks():
    driver = setupDriver()
    driver = goodreadsfunctions.goodreads_login(driver)
    books = goodreadsfunctions.getCategorizedBooks(
        "https://www.goodreads.com/shelf/show/programming", driver, minScore=200)
    driver.close()
    savebooks(books, 'programming')


def generalbooks():
    driver = setupDriver()
    mostread = goodreadsfunctions.getPopularBooks(
        "https://www.goodreads.com/book/most_read?category=combined&country=combined&duration=y", driver)
    morethanmillion = goodreadsfunctions.getPopularBooks(
        "https://www.goodreads.com/list/show/35080.One_million_ratings_", driver)
    driver.close()
    combined = {**morethanmillion, **mostread}
    savebooks(combined, 'generalbooks')


programmingbooks()
