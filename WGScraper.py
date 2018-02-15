from time import sleep
import webbrowser
from commonfunctions import getSoup
import ast
try:
    with open('offers.txt', 'r') as f:
        NEW_OFFERS = ast.literal_eval(f.read())
except:
    NEW_OFFERS = set()


def find_new_offers(url, isFlat=False):
    soup = getSoup(url)
    counter = 0
    for ad in soup.find_all('div', class_="col-sm-8")[4:]:
        title = ad.find(
            "h3", class_="headline headline-list-view noprint truncate_title")
        counter = counter + 1
        a = title.find("a")
        titletext = a.text.strip()
        href = a["href"]
        offer_url = "http://www.wg-gesucht.de/en/" + href
        if offer_url in NEW_OFFERS:
            continue
        offer = getSoup(offer_url)
        if not isFlat:
            english = offer.find("img", class_="flgS f-en")
            if not english:
                continue
        try:
            webbrowser.open(offer_url, new=2)
            NEW_OFFERS.add(offer_url)
            print(titletext)
        except:
            continue
    with open('offers.txt', 'w') as f:
        f.write(str(NEW_OFFERS))


while True:
    print("Rooms:")
    find_new_offers('https://www.wg-gesucht.de/en/wg-zimmer-in-Berlin.8.0.1.0.html?offer_filter=1&noDeact=1&city_id=8&category=0&rent_type=2&sMin=18&rMax=630&dFr=1517785200&dTo=1525125600&radLat=52.5093115&radLng=13.420192000000043&radAdd=Michaelkirchstra%C3%9Fe+24%2C+10179+Berlin%2C+Germany&radDis=5500&wgSea=2&wgAge=22&wgMnF=1&wgMxT=4')
    # print("Flats:")
    # find_new_offers('https://www.wg-gesucht.de/en/1-zimmer-wohnungen-in-Berlin.8.1.1.0.html?offer_filter=1&sort_column=0&noDeact=1&city_id=8&category=1&rent_type=0&sMin=30&rMax=800&dFr=1513810800&dTo=1527804000&radLat=52.5127637&radLng=13.415594000000056&radAdd=Am+K%C3%B6llnischen+Park%2C+Berlin%2C+Germany&radDis=5000', True)
    # print(len(NEW_OFFERS))
    print('sleeping for 15 mins')
    sleep(60 * 15)
