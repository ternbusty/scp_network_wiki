import sys
sys.path.append('../')
import requests
from bs4 import BeautifulSoup
import common

if __name__ == '__main__':
    url = 'http://scp-jp.wikidot.com/scp-jp-ex'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    content_panel = soup.find(
        'div', {'class': 'content-panel standalone series'})
    links = content_panel.find_all('a')
    hrefs = common.process_hrefs([link['href']
                                  for link in links if link.get('href')])

    # Save to ex_scp_jp
    common.iterate_and_save_link_list(hrefs[:-1], '../../yaml/jp/ex_scp_jp', base_url=common.jp_url)

    # Get metatitle
    lists = content_panel.find_all('li')
    texts = [li.text for li in lists]
    common.get_and_save_metatitle(hrefs[:-1], texts[:-1], '../../yaml/jp/ex_metatitle_jp')
