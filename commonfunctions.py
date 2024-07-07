import json
import operator
import os
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver


def sortscores(scores):
    sortedscores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
    return sortedscores


def sortandsave(scores, name):
    scores = sortscores(scores)
    savescores(scores, name)


def savescores(scores, name):
    name += ".json"
    with open(name, "w") as fp:
        json.dump(scores, fp)


def loadfile(name):
    my_file = Path(name + ".json")
    if my_file.is_file():
        json1_file = open(name + ".json")
        json1_str = json1_file.read()
        file = json.loads(json1_str)
    else:
        file = {}
    return file


def loadfileUnicode(name):
    my_file = Path(name + ".json")
    if my_file.is_file():
        json1_file = open(name + ".json")
        json1_str = json1_file.read()
        file = json.loads(json1_str)
    else:
        file = {}
    return file


def getSoup(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        r = response.read()
    return BeautifulSoup(r, "lxml")


def getSoupFromHTML(HTML):
    return BeautifulSoup(HTML, "lxml")


def setup_driver():
    options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    # options.add_argument("--headless")
    options.add_argument("--lang=en")

    thedriver = webdriver.Chrome(options=options)

    return thedriver
