import operator
import os
from selenium import webdriver

import commonfunctions
import goodreadsfunctions

import sys

def savebooks(books, name):
    sorteddata = sorted(
        books.items(), key=operator.itemgetter(1), reverse=True)
    commonfunctions.savescoresUnicode(sorteddata, 'books/' + name)

def printBestBookLink(books):
     sorteddata = sorted(
        books.items(), key=operator.itemgetter(1), reverse=True)
     print(sorteddata[0][1][2])

def categorized_books(genre='currently-reading', minscore=200, maxconsecutivebypassed=2, minRatio=0.4):
    driver = commonfunctions.setup_driver()
    driver = goodreadsfunctions.goodreads_login(driver)
    url = "https://www.goodreads.com/shelf/show/" + genre
    books = goodreadsfunctions.getCategorizedBooks(
        url, driver, minscore=minscore, maxconsecutivebypassed=maxconsecutivebypassed, minRatio=minRatio)
    driver.close()
    printBestBookLink(books)



categorized_books(sys.argv[1],minscore=int(sys.argv[2]),minRatio=float(sys.argv[3]))
