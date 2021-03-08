import sys
sys.path.append('../')
import requests
from bs4 import BeautifulSoup
import common

if __name__ == '__main__':
    url = 'http://scp-jp.wikidot.com/archived-scps-jp'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    content_panels = soup.find_all(
        'div', {'class': 'content-panel standalone series'})
    links = []
    for content_panel in content_panels[:2]:
        links.extend(content_panel.find_all('a'))
    hrefs = common.process_hrefs([link['href']
                                  for link in links if link.get('href')])

    # Save to arc_scp_jp
    common.iterate_and_save_link_list(hrefs, '../../yaml/jp/arc_scp_jp', base_url=common.jp_url)

    # Get metatitle
    lists = []
    for content_panel in content_panels[:2]:
        lists.extend(content_panel.find_all('li'))
    texts = [li.text for li in lists]
    common.get_and_save_metatitle(hrefs, texts, '../../yaml/jp/arc_metatitle_jp')
