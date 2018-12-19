import operator
import os
from selenium import webdriver

import commonfunctions
import goodreadsfunctions


def savebooks(books, name):
    sorteddata = sorted(
        books.items(), key=operator.itemgetter(1), reverse=True)
    commonfunctions.savescoresUnicode(sorteddata, 'books/' + name)


def categorized_books(genre='programming', minscore=200, maxconsecutivebypassed=20, minRatio=0.4):
    driver = commonfunctions.setup_driver()
    driver = goodreadsfunctions.goodreads_login(driver)
    url = "https://www.goodreads.com/shelf/show/" + genre
    books = goodreadsfunctions.getCategorizedBooks(
        url, driver, minscore=minscore, maxconsecutivebypassed=maxconsecutivebypassed, minRatio=minRatio)
    driver.close()
    savebooks(books, genre)
    os.system('code books/' + genre + '.json')


def generalbooks():
    driver = commonfunctions.setup_driver()
    mostread = goodreadsfunctions.getPopularBooks(
        "https://www.goodreads.com/book/most_read?category=all&country=all&duration=y", driver)
    morethanmillion = goodreadsfunctions.getPopularBooks(
        "https://www.goodreads.com/list/show/35080.One_million_ratings_", driver)
    driver.close()
    combined = {**morethanmillion, **mostread}
    savebooks(combined, 'generalbooks')


categorized_books('to-read', minscore=2000,
                  minRatio=0.37, maxconsecutivebypassed=5)
