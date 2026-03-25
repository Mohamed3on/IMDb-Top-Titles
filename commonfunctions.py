import json
import operator
import os
import random
import time
import urllib.request
import gzip
import zlib
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
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
    ]
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    time.sleep(random.uniform(0.1, 0.5))

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        r = response.read()
    if response.info().get("Content-Encoding") == "gzip":
        r = gzip.decompress(r)
    elif response.info().get("Content-Encoding") == "deflate":
        r = zlib.decompress(r)

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
