import json
import operator
import urllib.request
from pathlib import Path
from selenium import webdriver
import bs4
from webdriver_manager.chrome import ChromeDriverManager


def sortscores(scores):
    sortedscores = sorted(
        scores.items(), key=operator.itemgetter(1), reverse=True)
    return sortedscores


def sortandsave(scores, name):
    scores = sortscores(scores)
    savescores(scores, name)


def savescores(scores, name):
    name += '.json'
    with open(name, 'w') as fp:
        json.dump(scores, fp)


def savescoresUnicode(scores, name):
    name += '.json'
    with open(name, 'w', encoding='utf8') as fp:
        json.dump(scores, fp, ensure_ascii=False)


def loadfile(name):
    my_file = Path(name + ".json")
    if my_file.is_file():
        json1_file = open(name + '.json')
        json1_str = json1_file.read()
        file = json.loads(json1_str)
    else:
        file = {}
    return file


def loadfileUnicode(name):
    my_file = Path(name + ".json")
    if my_file.is_file():
        json1_file = open(name + '.json')
        json1_str = json1_file.read()
        file = json.loads(json1_str)
    else:
        file = {}
    return file


def getSoup(url):
    with urllib.request.urlopen(url) as url:
        r = url.read()
    return bs4.BeautifulSoup(r, "lxml")


def getSoupFromHTML(HTML):
    return bs4.BeautifulSoup(HTML, 'lxml')


def setup_driver():
    options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_argument("--headless")
    options.add_argument('--lang=en')
    options.binary_location = "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta"
    options.add_experimental_option("prefs", prefs)
    thedriver = webdriver.Chrome(
        ChromeDriverManager().install(), chrome_options=options)

    return thedriver
