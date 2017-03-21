import cgi
import json
import operator

import functions
from pathlib import Path


def unicodeToHTMLEntities(text):
    """Converts unicode to HTML entities.  For example '&' becomes '&amp;'."""
    text = cgi.escape(text).encode('ascii', 'xmlcharrefreplace')
    return str(text).split('b')[1].split("\'")[1]
data=functions.getBooks()
sorteddata = sorted(data.items(), key=operator.itemgetter(1), reverse=True)
functions.savescores(data,'books')
functions.savescores(sorteddata,'sortedbooks')