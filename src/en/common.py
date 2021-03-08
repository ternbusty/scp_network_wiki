from bs4 import BeautifulSoup
import re
import requests
import yaml
from random import random
from time import sleep
import os

en_url = 'https://scp-wiki.wikidot.com/'


def format_num(num: int) -> str:
    return str(num).zfill(3) if num < 100 else str(num)


def extract_rate(soup: BeautifulSoup) -> str:
    rate = soup.find('span', {'class': 'number prw54353'})
    if rate is None:
        return 'unknown'
    else:
        return rate.getText()


def process_hrefs(hrefs: list, excludes: list = []) -> list:
    links = []
    ng_words = ['systems:', 'png', 'jpg', 'local--files', 'component:']
    for href in hrefs:
        href = re.sub(r'https?://(www\.)?scp.*?/', '/', href)
        if not href.startswith('/') or (href == '/'):
            continue
        exclude_flag = False
        for exclude in excludes:
            if href == '/' + exclude:
                exclude_flag = True
                break
        if exclude_flag:
            continue
        for ng_word in ng_words:
            if ng_word in href:
                break
        else:
            links.append(href[1:])
    return links


def extract_links(soup: BeautifulSoup, excludes: list = []) -> list:
    page_content = soup.find('div', {'id': 'page-content'})
    round_footer = 'background-color: #066; border: outset 1.5px #000; '\
        'border-radius: 30px; color: #000; '\
        'background: linear-gradient(to bottom right, rgba(6,108,182,0), rgba(6,108,182,0.35));'
    exclude_list = [['div', 'class', 'footer-wikiwalk-nav'],
                    ['div', 'style', round_footer],
                    ['div', 'class', 'licensebox'],
                    ['div', 'class', 'collection'],
                    ['div', 'id', 'u-credit-view'],
                    ['div', 'id', 'u-credit-otherwise'],
                    ['div', 'class', 'info-container']]
    for exclude in exclude_list:
        components = soup.find_all(exclude[0], {exclude[1]: exclude[2]})
        for component in components:
            component.decompose()
    hrefs = [url.get('href')
             for url in page_content.find_all('a') if url.get('href')]
    links = process_hrefs(hrefs, excludes)
    unique_links = list(set(links))
    return unique_links


def extract_tags(soup: BeautifulSoup) -> list:
    page_tags = soup.find('div', {'class': 'page-tags'})
    if page_tags is None:
        return []
    tags = [url.text for url in page_tags.find_all('a')
            if not url.text.startswith('_')]
    unique_tags = list(set(tags))
    return unique_tags


def correct_unknown_rate(key: str, obj: dict) -> None:
    original_links = obj[key]['links']
    for original_link in original_links:
        if 'adult' in original_link:
            redirect_link = original_link
            break
    else:
        return
    res = requests.get(en_url + redirect_link)
    if res.status_code != 200:
        return
    soup = BeautifulSoup(res.text, 'html.parser')
    rate = extract_rate(soup)
    links = extract_links(soup, [key])
    tags = extract_tags(soup)
    obj[key]['rate'] = rate
    obj[key]['links'] = links
    obj[key]['tags'] = list(set(tags) | set(obj[key]['tags']))


def create_obj_from_link(link: str, excludes: list = []) -> dict:
    if 'system:page-tags' in link:
        title = link.split('/')[-1].split('#')[0]
        print(title)
        rate = 'unknown'
        links = tags = []
    else:
        # print('processing', link)
        url = en_url + link
        res = requests.get(url)
        if res.status_code != 200:
            return None
        soup = BeautifulSoup(res.text, 'html.parser')
        title = soup.find('title').text.replace(' - SCP Foundation', '')
        sleep(random() * 10 + 2)
        links = extract_links(soup, excludes)
        rate = extract_rate(soup)
        tags = extract_tags(soup)
        if (len(links) >= 10):
            print(len(links), 'links found: ', url)
    obj = {
        link: {
            'title': title,
            'rate': rate,
            'links': links,
            'tags': tags}}
    return obj


def iterate_and_save_link_list(
        link_list: list,
        filename: str,
        start: int = 0) -> None:
    if start == 0:
        if os.path.exists(filename + '.yaml'):
            os.remove(filename + '.yaml')
    for i in range(start, len(link_list)):
        link = link_list[i]
        tmp_obj = create_obj_from_link(link, excludes=[link])
        print(i, '/', len(link_list), tmp_obj[link]['title'])
        if tmp_obj[link]['rate'] == 'unknown':
            correct_unknown_rate(link, tmp_obj)
        with open(filename + '.yaml', 'a') as file:
            yaml.dump(tmp_obj, file)
        sleep(random() * 10 + 2)


def get_and_save_metatitle(
        link_list: list,
        text_list: list,
        filename: str) -> None:
    obj = {}
    exclude_list = ['object-classes',
                    'secure-facilities-locations',
                    'security-clearance-levels',
                    'object-classes',
                    'task-forces',
                    'explained-scps-tales-edition']
    for (link, text) in zip(link_list, text_list):
        if link in exclude_list:
            continue
        if ' - ' not in text:
            metatitle = text
        else:
            splitted = text.split(' - ')
            metatitle = ' - '.join(splitted[1:])
        scp_title = link
        obj[scp_title] = metatitle

    with open(filename + '.yaml', 'w') as file:
        yaml.dump(obj, file)
    sleep(random() * 10 + 2)
