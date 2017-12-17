import time

from commonfunctions import getSoup, savescoresUnicode

NEW_OFFERS = {}

EARLIEST_MOVE_OUT_MONTH = 6
EARLIEST_MOVE_OUT_YEAR = 18


def is_long_term(ad):
    try:
        move_out = ad.find(
            "p", attrs={'style': 'line-height: 1.2em;'}).text.strip().split('-')[-1].split('.')
        if int(move_out[1]) < EARLIEST_MOVE_OUT_MONTH or int(move_out[2]) < EARLIEST_MOVE_OUT_YEAR:
            return False
        else:
            return True
    except:
        return True


def find_new_offers():
    soup = getSoup('http://www.wg-gesucht.de/en/wg-zimmer-in-Berlin.8.0.1.0.html?offer_filter=1&noDeact=1&city_id=8&category=0&rent_type=0&sMin=13&rMax=800&dFr=1513810800&dTo=1525125600&radLat=52.5306438&radLng=13.38306829999999&radAdd=Mitte%2C+Berlin%2C+Germany&radDis=7000&wgSea=2&wgAge=22&wgMnF=1&fur=1')
    counter = 0
    for ad in soup.find_all('div', class_="col-sm-8")[4:]:
        if not is_long_term(ad):
            continue
        title = ad.find(
            "h3", class_="headline headline-list-view noprint truncate_title")
        counter = counter + 1
        a = title.find("a")
        titletext = a.text.strip()
        href = a["href"]
        offer_url = "http://www.wg-gesucht.de/en/" + href
        if offer_url in NEW_OFFERS:
            break
        offer = getSoup(
            "http://www.wg-gesucht.de/en/" + href)
        english = offer.find("img", class_="flgS f-en")
        if not english:
            continue
        else:
            try:
                validoffer = {}
                validoffer["desc"] = offer.find(
                    "div", class_="freitext wordWrap").text.strip().replace('\n', "").replace('\r', '')
                validoffer["price"] = offer.find_all(
                    "div", class_="col-xs-6 text-center print_inline")[1].find("h2").text.strip()
                validoffer["size"] = offer.find_all(
                    "div", class_="col-xs-6 text-center print_inline")[0].find("h2").text.strip()
                validoffer["Title"] = titletext
                NEW_OFFERS[offer_url] = validoffer
                print(titletext)
            except:
                continue
    print(len(NEW_OFFERS))
    savescoresUnicode(NEW_OFFERS, 'offers')


while True:
    find_new_offers()
    print('sleeping for 15 mins')
    time.sleep(60 * 15)
