from time import sleep
import webbrowser
from commonfunctions import getSoup
import ast
try:
    with open('offers.txt', 'r') as f:
        NEW_OFFERS = ast.literal_eval(f.read())
except:
    NEW_OFFERS = set()

EARLIEST_MOVE_OUT_MONTH = 8
EARLIEST_MOVE_OUT_YEAR = 18


def is_long_term(ad):
    try:
        move_out = ad.find(
            "p", attrs={'style': 'line-height: 1.2em;'}).text.strip().split('-')[-1].split('.')
        if move_out[0].strip().isdigit():
            if int(move_out[1]) < EARLIEST_MOVE_OUT_MONTH or int(move_out[2]) < EARLIEST_MOVE_OUT_YEAR:
                return False
        return True
    except:
        return True


def find_new_offers(url, isFlat=False):
    soup = getSoup(url)
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
    find_new_offers('https://www.wg-gesucht.de/en/wg-zimmer-in-Berlin.8.0.1.0.html?offer_filter=1&noDeact=1&city_id=8&category=0&rent_type=0&sMin=18&rMax=630&dFr=1520204400&dTo=1523311200&radLat=52.50299&radLng=13.419599999999946&radAdd=Waldemarstra%C3%9Fe+42B%2C+Berlin%2C+Germany&radDis=4000&wgSea=2&wgAge=22&wgMnF=1&wgMxT=5')
    # print("Flats:")
    # find_new_offers('https://www.wg-gesucht.de/en/1-zimmer-wohnungen-in-Berlin.8.1.1.0.html?offer_filter=1&sort_column=0&noDeact=1&city_id=8&category=1&rent_type=0&sMin=30&rMax=800&dFr=1513810800&dTo=1527804000&radLat=52.5127637&radLng=13.415594000000056&radAdd=Am+K%C3%B6llnischen+Park%2C+Berlin%2C+Germany&radDis=5000', True)
    # print(len(NEW_OFFERS))
    print('sleeping for 15 mins')
    sleep(60 * 15)
# Facebook pitch
#  Hi, Steve! I'm super interested in the room. You look like a friendly person, and I think we'd be good flatmates. I'm an open-minded person, clean, kinda funny and easy going. I would love to hang out and cook with you, as I'm not just looking for a flat, but for friends too!

# I love football, computers, movies and video games. I also love making new friends from different cultures, it's amazing to see how different yet how similar we all are! And that's one of the main reasons why I came to Berlin.

# I'm also looking to move in ASAP as I have to vacate my current place shortly so it would be great if we could set up a viewing soon.

# Cheers!
