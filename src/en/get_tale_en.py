import requests
from bs4 import BeautifulSoup
import common

if __name__ == '__main__':
    tale_url = 'http://scp-wiki.wikidot.com/system:page-tags/tag/tale#pages'
    res = requests.get(tale_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    pages_list = soup.find('div', {'id': 'tagged-pages-list'})

    urls = pages_list.find_all('a')
    hrefs = common.process_hrefs([url.get('href') for url in urls])
    common.iterate_and_save_link_list(hrefs, '../../yaml/en/tale_en')

