from __future__ import print_function

import re
from requests import get

from os import mkdir
import sys

from functools import partial


URL = 'http://fonts.googleapis.com/css?family={}'
DEBUG = False

def to_url(families):
    return URL.format('|'.join(family.replace(' ', '+') for family in families))

def get_woff_urls(css_data):
    return re.findall('url\((.*?)\)', css_data)

def get_file_name(url):
    return url[url.rfind('/') + 1:].strip()

def download_to_folder(folder_name, item, func=lambda x:x):
    r = get(item)
    file_name = get_file_name(r.url)
    folder_name += '/'

    with open(folder_name + file_name, 'wb') as f:
        f.write(func(r.content))

def fix_css(folder, urls, data):
    folder += '/'

    for url in urls:
        data = data.replace(url, folder + get_file_name(url))

    return data

def create_folders(folders):
    for folder in folders:
        try:
            mkdir(folder)
        except OSError:
            print('{} already exists!'.format(folder))

def main():
    if DEBUG:
        families = ['Seymour One', 'Chango', 'Exo 2']
    else:
        families = ' '.join(sys.argv[1:])
        families = [f.strip() for f in families.split(',') if f.strip()]

    if not families:
        print('Nothing to do!')
        return

    create_folders(['font', 'css'])

    css = get(to_url(families)).content
    urls = get_woff_urls(css)
    downloader = partial(download_to_folder, 'font')

    for url in urls:
        downloader(url)

    css = fix_css('font', urls, css)

    with open('css/fonts.css', 'wb') as f:
        f.write(css)
        
if __name__ == '__main__':
    main()