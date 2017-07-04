import operator
import pickle
from selenium import webdriver

import functions
import login
def setupDriver():
    chromeOptions = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chromeOptions.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome("C:/Users/Mohamed/chromedriver.exe", chrome_options=chromeOptions)
    return driver

driver=setupDriver()



def savebooks(books, name):
    sorteddata = sorted(books.items(), key=operator.itemgetter(1), reverse=True)
    functions.savescores(sorteddata, name + 'books')


def programmingbooks():
    driver.get('https://www.goodreads.com/user/sign_in')
    mailinput=driver.find_element_by_id('user_email')
    passinput=driver.find_element_by_id('user_password')
    mailinput.send_keys(login.email)
    passinput.send_keys(login.password)
    driver.find_element_by_name('next').click()
    page1=functions.getBooks("https://www.goodreads.com/shelf/show/programming?page=1",driver)
    page2=functions.getBooks("https://www.goodreads.com/shelf/show/programming?page=2",driver)
    driver.close()
    both={**page1,**page2}
    savebooks(both,'programming')


def generalbooks():
    mostread = functions.getBooks("https://www.goodreads.com/book/most_read?category=all&country=all&duration=y")
    morethanmillion = functions.getBooks("https://www.goodreads.com/list/show/35080.One_million_ratings_")
    driver.close()
    all = {**morethanmillion, **mostread}
    savebooks(all, 'generalbooks')


def businessbooks():
    savebooks("https://www.goodreads.com/shelf/show/business", 'businessbooks')
programmingbooks()
