import requests
from bs4 import BeautifulSoup
import common

if __name__ == '__main__':
    url = 'https://scp-wiki.wikidot.com/archived-scps'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    content_panels = soup.find_all(
        'div', {'class': 'content-panel standalone series'})
    links = []
    for content_panel in content_panels[:2]:
        links.extend(content_panel.find_all('a'))
    hrefs = common.process_hrefs([link['href']
                                  for link in links if link.get('href')])

    # Save to arc_scp_en
    common.iterate_and_save_link_list(hrefs, '../../yaml/en/arc_scp_en')

    # Get metatitle
    lists = []
    for content_panel in content_panels[:2]:
        lists.extend(content_panel.find_all('li'))
    texts = [li.text for li in lists]
    common.get_and_save_metatitle(hrefs, texts, '../../yaml/en/arc_metatitle_en')
