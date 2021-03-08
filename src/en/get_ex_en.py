import requests
from bs4 import BeautifulSoup
import common

if __name__ == '__main__':
    url = 'https://scp-wiki.wikidot.com/scp-ex/noredirect/true'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    content_panel = soup.find(
        'div', {'class': 'content-panel standalone series'})
    links = content_panel.find_all('a')
    hrefs = common.process_hrefs([link['href']
                                  for link in links if link.get('href')])

    # Save to ex_scp_en
    common.iterate_and_save_link_list(hrefs[:-1], '../../yaml/en/ex_scp_en')

    # Get metatitle
    lists = content_panel.find_all('li')
    texts = [li.text for li in lists]
    common.get_and_save_metatitle(hrefs[:-1], texts[:-1], '../../yaml/en/ex_metatitle_en')
