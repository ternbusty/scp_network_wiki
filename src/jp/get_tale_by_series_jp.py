import sys
sys.path.append('../')
import os
import common
from typing import Union
from random import random
from time import sleep
import yaml
from bs4 import BeautifulSoup, element
import requests

def process_sibling(
        sibling: Union[element.NavigableString, element.Tag], obj: dict) -> None:
    links = sibling.find_all('a')
    hrefs = [link['href'] for link in links if link.get('href')]
    if len(links) == 1:
        result = []
    else:
        result = common.process_hrefs(hrefs[1:])
    obj[hrefs[0][1:]] = result


filename = '../../yaml/jp/tale_by_series_jp'

if os.path.exists(filename + '.yaml'):
    os.remove(filename + '.yaml')

for i in range(1, 4):
    url = f'https://scp-jp.wikidot.com//scp-series-jp-{i}-tales-edition/noredirect/true'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    collapsible_blocks = soup.find_all('div', {'class': 'collapsible-block'})
    for collapsible_block in collapsible_blocks:
        collapsible_block.decompose()
    content_panel = soup.find(
        'div', {'class': 'content-panel standalone series'})
    if i == 1:
        h1s = content_panel.find_all('h1')[:-1]
    else:
        h1s = content_panel.find_all('h1')[1:]

    obj = {}
    for h1 in h1s:
        block = h1.next_sibling.next_sibling
        elem = block.find('li')
        while elem is None:
            block = block.next_sibling.next_sibling
            elem = block.find('li')
        process_sibling(elem, obj)
        siblings = elem.next_siblings
        for sibling in siblings:
            if sibling == '\n':
                continue
            process_sibling(sibling, obj)

    with open(filename + '.yaml', 'a') as file:
        yaml.dump(obj, file)
    sleep(random() * 10 + 2)
