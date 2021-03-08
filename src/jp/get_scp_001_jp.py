import sys
sys.path.append('../')
from bs4 import BeautifulSoup
import requests
import common


if __name__ == '__main__':
    url = 'http://scp-jp.wikidot.com/scp-001-jp'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    content_panel = soup.find_all(
        'div', {'class': 'content-panel standalone series'})[1]
    links = content_panel.find_all('a')
    print(links)
    hrefs = common.process_hrefs([link['href'] for link in links])
    common.iterate_and_save_link_list(
        hrefs,
        '../../yaml/jp/scp_001_jp',
        base_url=common.jp_url)
