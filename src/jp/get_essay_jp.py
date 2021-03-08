import sys
sys.path.append('../')
import requests
from bs4 import BeautifulSoup
import common

if __name__ == '__main__':
    tale_url = 'http://scp-jp.wikidot.com/system:page-tags/tag/%E3%82%A8%E3%83%83%E3%82%BB%E3%82%A4#pages'
    res = requests.get(tale_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    pages_list = soup.find('div', {'id': 'tagged-pages-list'})

    urls = pages_list.find_all('a')
    hrefs = common.process_hrefs([url.get('href') for url in urls])
    common.iterate_and_save_link_list(hrefs, '../../yaml/jp/essay_jp', base_url=common.jp_url)
