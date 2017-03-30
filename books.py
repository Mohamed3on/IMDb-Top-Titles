import cgi
import json
import operator

import functions
from pathlib import Path


def unicodeToHTMLEntities(text):
    """Converts unicode to HTML entities.  For example '&' becomes '&amp;'."""
    text = cgi.escape(text).encode('ascii', 'xmlcharrefreplace')
    return str(text).split('b')[1].split("\'")[1]

def savebooks(url,name):
    data = functions.getBooks(url)
    sorteddata = sorted(data.items(), key=operator.itemgetter(1), reverse=True)
    functions.savescores(sorteddata, name)
def programmingbooks():
    savebooks("https://www.goodreads.com/shelf/show/programming",'programmingbooks')


def generalbooks():
    savebooks("https://www.goodreads.com/book/most_read?category=all&country=all&duration=y",'generalbooks')

def businessbooks():
    savebooks("https://www.goodreads.com/shelf/show/business",'businessbooks')
businessbooks()