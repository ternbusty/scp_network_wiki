import sys
sys.path.append('../')
import common
import requests
from bs4 import BeautifulSoup
import os

if __name__ == '__main__':
    # links = ['scp-' + str(num).zfill(3) + '-jp' if num < 100 else 'scp-' + str(num) + '-jp'
    #          for num in range(2, 3000)]
    # common.iterate_and_save_link_list(links, '../../yaml/jp/scp_jp', base_url=common.jp_url, start=1160)

    filename = '../../yaml/jp/metatitle_jp'
    if os.path.exists(filename + '.yaml'):
        os.remove(filename + '.yaml')
    metatitle_url = 'http://scp-jp.wikidot.com/scp-series-jp'
    suffix_list = ['', '-2', '-3']
    for suffix in suffix_list:
        print(suffix)
        obj = {}
        res = requests.get(metatitle_url + suffix)
        soup = BeautifulSoup(res.text, 'html.parser')
        content_panel = soup.find(
            'div', {'class': 'content-panel standalone series scp'})
        lists = content_panel.find_all('li')
        print(lists)
        links = common.process_hrefs([li.find('a')['href'] for li in lists])
        texts = [li.text for li in lists]
        common.get_and_save_metatitle(
            links, texts, filename, mode='a')
