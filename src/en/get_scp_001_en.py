import requests
from bs4 import BeautifulSoup
import common

if __name__ == '__main__':
    url = 'http://scp-wiki.wikidot.com/scp-001/'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    content_panel = soup.find_all(
        'div', {'class': 'content-panel standalone series'})[1]
    links = content_panel.find_all('a')
    hrefs = common.process_hrefs([link['href'] for link in links])
    common.iterate_and_save_link_list(hrefs, '../../yaml/en/scp_001_en')
