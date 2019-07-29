#! /usr/local/bin/python3.7

"""
Utils file for stuff to do with the web like soup, caching webpages, etc.
"""

import os
import json
import ssl
import bs4
import requests
import urllib.request
import pickle
import re


from functools import wraps
from multiprocessing.dummy import Pool
from plants.util import sha1hash, timer

from datetime import datetime as time

home = os.path.expanduser(('~'))
webcach_dir = os.path.abspath(f'{home}/Cache/webpages')


def cache(func):
    """Requires the first argument to be a url.
    Also saves the pages as a string"""

    if os.path.exists(webcach_dir) is False:
        # os.mkdir(os.path.dirname(webcach_dir))
        os.mkdir(webcach_dir)

    @wraps(func)
    def load_cache(*args, **kwargs):
        url = args[0]
        urlhash = f'{sha1hash(url)}.html'
        if re.match('http[s]?://', url) is None:
            raise BaseException('First argument needs to be a url')

        if urlhash in os.listdir(webcach_dir) and os.path.getsize(f'{webcach_dir}/{urlhash}') > 0:
            with open(f'{webcach_dir}/{urlhash}', 'rb') as readfile:
                file = pickle.load(readfile)
                t1 = time.now()
                r = bs4.BeautifulSoup(file, features='html.parser')
                return r
        else:
            soup = func(*args, **kwargs)
            with open(f'{webcach_dir}/{urlhash}', 'wb') as writefile:
                pickle.dump(str(soup), writefile)
            return soup
    return load_cache


def get_many_soups(urls):
    """Will return dict of {url: soup}"""
    pool = Pool(os.cpu_count()-1)

    soups = pool.map(get_soup, urls)
    pool.close()
    pool.join()

    results = {}
    for url, soup in zip(urls, soups):
        results.update({url: soup})
    return results


def download(url):
    url = url.encode('utf-8')
    try:
        # http = url.split(':')[0]
        # url = '{}:{}'.format(http, ul.parse.quote(url.replace('{}:'.format(http), '')))
        req = urllib.request.Request(  # Fast
            url,
            data=None,
            headers={
                'User-Agent':
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3)'
                    'AppleWebKit/537.36 (KHTML, like Gecko)'
                    'Chrome/35.0.1916.47 Safari/537.36'}
        )
        # noinspection PyProtectedMember
        context = ssl._create_unverified_context()  # Fast
        web_page = urllib.request.urlopen(req, context=context)
        soup = bs4.BeautifulSoup(web_page, "html.parser")
        return soup
    except urllib.error.URLError as e:
        page = requests.get(url).content
        soup = bs4.BeautifulSoup(page, "html.parser")
        return soup


def get_soup(url, cache=True):
    """Get bs4 get_soup from url"""
    if re.match('http[s]?://', url) is None:
        raise BaseException('First argument needs to be a url')

    urlhash = f'{sha1hash(url)}.html'
    if cache and urlhash in os.listdir(webcach_dir) and os.path.getsize(f'{webcach_dir}/{urlhash}') > 0:
        with open(f'{webcach_dir}/{urlhash}', 'rb') as readfile:
            file = pickle.load(readfile)
            r = bs4.BeautifulSoup(file, features='html.parser')  # ~0.15s to load.
            return r
    else:
        soup = download(url)
        with open(f'{webcach_dir}/{urlhash}', 'wb') as writefile:
            pickle.dump(str(soup), writefile)
        return soup


def jsonApi(url):
    """Returns dict object"""
    r = requests.get(url)# .encoding('utf-8')
    if r.status_code is not 200:
        raise requests.HTTPError('Not 200 status code for {}'.format(url))

    return json.loads(requests.get(url).content.decode("utf-8"))


if __name__ == '__main__':
    get_soup('https://www.rhs.org.uk/Plants/Search-Results?f%2Fplant_colour_by_season%2Fsummer%2Fblue=f%2Fplant_colour_by_season%2Fsummer%2Fblue&form-mode=true&context=b%3D0%26hf%3D10%26l%3Den%26s%3Ddesc%2528plant_merged%2529%26sl%3DplantForm&unwind=undefined')
