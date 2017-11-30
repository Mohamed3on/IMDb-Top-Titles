import time
from commonfunctions import getSoup, savescoresUnicode

newoffers = {}


def find_new_offers():
    soup = getSoup('http://www.wg-gesucht.de/en/wg-zimmer-in-Berlin.8.0.1.0.html?offer_filter=1&noDeact=1&city_id=8&category=0&rent_type=0&rMax=800&dFr=1512082800&dTo=1513724400&radLat=52.5306438&radLng=13.38306829999999&radAdd=Mitte%2C+Berlin%2C+Germany&radDis=8000&wgSea=2&wgAge=22&wgMnF=1&fur=1')
    counter = 0
    for title in soup.find_all("h3", class_="headline headline-list-view noprint truncate_title"):
        counter = counter + 1
        a = title.find("a")
        titletext = a.text.strip()
        href = a["href"]
        offerURL = "http://www.wg-gesucht.de/en/" + href
        if offerURL in newoffers:
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
                newoffers[offerURL] = validoffer
                print(titletext)
            except:
                continue
    print(len(newoffers))
    savescoresUnicode(newoffers, 'offers')


while True:
    find_new_offers()
    print('sleeping for 15 mins')
    time.sleep(60 * 15)
