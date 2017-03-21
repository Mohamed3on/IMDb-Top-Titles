import cgi
import json
import operator

import functions
from pathlib import Path


def unicodeToHTMLEntities(text):
    """Converts unicode to HTML entities.  For example '&' becomes '&amp;'."""
    text = cgi.escape(text).encode('ascii', 'xmlcharrefreplace')
    return str(text).split('b')[1].split("\'")[1]


def programmingbooks():
    my_file = Path("programmingbooks.json")
    if my_file.is_file():
        json1_file = open('programmingbooks.json')
        json1_str = json1_file.read()
        books = json.loads(json1_str)
    else:
        books = {}
    data = functions.getBooks(books, "https://www.goodreads.com/shelf/show/programming")
    sorteddata = sorted(data.items(), key=operator.itemgetter(1), reverse=True)
    functions.savescores(sorteddata, 'programmingbooks')


def generalbooks():
    my_file = Path("generalbooks.json")
    if my_file.is_file():
        json1_file = open('generalbooks.json')
        json1_str = json1_file.read()
        books = json.loads(json1_str)
    else:
        books = {}
    data = functions.getBooks(books, "https://www.goodreads.com/book/most_read?category=all&country=all&duration=y")
    sorteddata = sorted(data.items(), key=operator.itemgetter(1), reverse=True)
    functions.savescores(sorteddata, 'generalbooks')


generalbooks()
