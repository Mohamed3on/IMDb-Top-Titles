import html
import time

import bs4
from numpy import save

from commonfunctions import getSoup, loadfile, savescores

offers = loadfile('offers')

# def setup_driver():
#     options = webdriver.ChromeOptions()
#     prefs = {"profile.managed_default_content_settings.images": 2}
#     options.add_experimental_option("prefs", prefs)
#     thedriver = webdriver.Chrome(chrome_options=options)
#     return thedriver


def find_new_offers():
    soup = getSoup('http://www.wg-gesucht.de/en/wg-zimmer-in-Berlin.8.0.1.0.html?offer_filter=1&city_id=8&category=0&rent_type=0&rMax=700&dFr=1505858400&wgSea=2&wgSmo=2&wgAge=22&wgMnF=1&fur=1')
    counter = 0
    for title in soup.find_all("h3", class_="headline headline-list-view noprint"):
        counter = counter + 1
        a = title.find("a")
        titletext = html.escape(a.text.strip())
        if titletext in offers:
            print('ollllld')
            break
        href = a["href"]
        offer = getSoup(
            "http://www.wg-gesucht.de/en/" + href)
        english = offer.find("img", class_="flgS f-en")
        if not english:
            continue
        else:
            validoffer = {}
            validoffer["desc"] = html.escape(offer.find(
                "div", class_="freitext wordWrap").text.strip().replace('\n', ""))
            validoffer["price"] = html.escape(offer.find_all(
                "div", class_="col-xs-6 text-center print_inline")[1].find("h2").text.strip())
            validoffer["size"] = html.escape(offer.find_all(
                "div", class_="col-xs-6 text-center print_inline")[0].find("h2").text.strip())
            validoffer["href"] = html.escape(
                "http://www.wg-gesucht.de/en/" + href)
            offers[titletext] = validoffer
            print(counter)
            print(validoffer)
            savescores(offers, 'offers')


while True:
    find_new_offers()
    print('sleeping for 30 mins')
    time.sleep(60 * 30)
