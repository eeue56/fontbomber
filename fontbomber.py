#!/usr/bin/python
from __future__ import print_function

import re
from requests import get

from os import mkdir
import sys

from functools import partial

from multiprocessing import Pool


URL = 'http://fonts.googleapis.com/css?family={}'
DEBUG = False

def to_url(families):
    ''' If families a list of strings, join them by | and replace spaces
        with +, else just return families'''
    if not isinstance(families, list):
        return families
    return URL.format('|'.join(family.replace(' ', '+') for family in families))

def get_woff_urls(css_data):
    ''' returns all the urls found in the css file'''
    return re.findall('url\((.*?)\)', css_data)

def get_font_family_names(css_data):
    """ Gets the font family names from the css data """
    return re.findall('font-family: \'(.*?)\'', css_data)

def warn_about_missing(css_data, families):
    for family in families:
        if family not in css_data:
            print('Failed to find font "{}".'.format(family))

def get_file_name(url):
    ''' gets a file name from a url '''
    return url[url.rfind('/') + 1:].strip()

def download_to_folder(folder_name, item, family_name, func=lambda x:x):
    ''' downloads an item to a folder, then runs func on it before saving'''

    print('Downloading "{}" from "{}".'.format(family_name, item))
    
    r = get(item)
    file_name = get_file_name(r.url)
    folder_name += '/'

    with open(folder_name + family_name, 'wb') as f:
        f.write(func(r.content))

def fix_css(folder, urls, names, data):
    ''' fixes the css to point to local copies'''
    folder = '../{}/'.format(folder)

    for url, name in zip(urls, names):
        data = data.replace(url, folder + name)

    return data

def clean_name(name):
    """ Cleans the name by removing spaces and adding .ttf to the end """
    EXTENSION = '.ttf'
    return name.replace(' ', '') + EXTENSION

def create_folders(folders):
    ''' creates folders, warns on failure'''
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

        if 'http' not in families:
            families = [f.strip() for f in families.split(',') if f.strip()]
        else:
            families = [f.replace('+', ' ').strip() for f in families[families.find('=') + 1:].split('|')]

    if not families:
        print('Nothing to do!')
        return

    print('Creating folders... ')
    create_folders(['font', 'css'])

    print('Downloading css file... ')
    css = get(to_url(families)).text
    print('Downloaded!')

    warn_about_missing(css, families)
    urls = get_woff_urls(css)
    names = [clean_name(name) for name in get_font_family_names(css)]
    
    downloader = partial(download_to_folder, 'font')

    print('Downloding fonts...')
    for url, family in zip(urls, names):
        downloader(url, family)
    print('Downloaded!')


    css = fix_css('font', urls, names, css)

    with open('css/fonts.css', 'w') as f:
        f.write(css)

    print('Finished!')

if __name__ == '__main__':
    main()