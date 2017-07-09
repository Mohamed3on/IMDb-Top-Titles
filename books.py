import operator

from selenium import webdriver

import functions
import login


def setupDriver():
    OPTIONS = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    OPTIONS.add_experimental_option("prefs", prefs)
    thedriver = webdriver.Chrome(
        "C:/Users/Mohamed/chromedriver.exe", chrome_options=OPTIONS)
    return thedriver


driver = setupDriver()


def savebooks(books, name):
    sorteddata = sorted(
        books.items(), key=operator.itemgetter(1), reverse=True)
    functions.savescores(sorteddata, name + 'books')


def programmingbooks():
    driver.get('https://www.goodreads.com/user/sign_in')
    mailinput = driver.find_element_by_id('user_email')
    passinput = driver.find_element_by_id('user_password')
    mailinput.send_keys(login.email)
    passinput.send_keys(login.password)
    driver.find_element_by_name('next').click()
    books = functions.getCategorizedBooks(
        "https://www.goodreads.com/shelf/show/programming", driver)
    driver.close()
    savebooks(books, 'programming')


def generalbooks():
    mostread = functions.getPopularBooks(
        "https://www.goodreads.com/book/most_read?category=combined&country=combined&duration=y", driver)
    morethanmillion = functions.getPopularBooks(
        "https://www.goodreads.com/list/show/35080.One_million_ratings_", driver)
    driver.close()
    combined = {**morethanmillion, **mostread}
    savebooks(combined, 'generalbooks')


programmingbooks()
