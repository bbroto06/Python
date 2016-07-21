#!/usr/bin/env python

import requests
from BeautifulSoup import BeautifulSoup
import re, cgi

url = "https://www.mybmtc.com/airportservices"
response = requests.get(url)
# parse html
page = str(BeautifulSoup(response.content))


def getURL(page):
    start_link = page.find("a href")
    if start_link == -1:
        return None, 0
    start_quote = page.find('KIAS-8', start_link)
    end_quote = page.find('KIAS-9', start_quote + 1)
    url = page[start_quote + 1: end_quote]
    return url, end_quote

while True:
    url, n = getURL(page)
    page = page[n:]
    # regular expression to remove html tags
    tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')
    if url:
        no_tags = tag_re.sub('', url)
        ready_for_web = cgi.escape(no_tags)
        print ready_for_web
    else:
        break
