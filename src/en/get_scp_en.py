import common
import requests
from bs4 import BeautifulSoup

if __name__ == '__main__':
    links = ['scp-' + str(num).zfill(3) if num < 100 else 'scp-' + str(num)
             for num in range(2, 6000)]
    common.iterate_and_save_link_list(links, '../../yaml/en/scp_en')

    metatitle_url = 'http://www.scpwiki.com/scp-series'
    suffix_list = ['', '-2', '-3', '-4', '-5', '-6']
    for suffix in suffix_list:
        print(suffix)
        obj = {}
        res = requests.get(metatitle_url + suffix)
        soup = BeautifulSoup(res.text, 'html.parser')
        content_panel = soup.find(
            'div', {'class': 'content-panel standalone series'})
        lists = content_panel.find_all('li')
        links = common.process_hrefs([li.find('a')['href'] for li in lists])
        for i in range(len(links)):
            link = links[i]
            if links[i] == '1231-warning':
                links[i] = 'scp-1231'
            elif links[i] == 'scp-2615-j':
                links[i] = 'scp-2615'
        texts = [li.text for li in lists]
        common.get_and_save_metatitle(
            links, texts, '../../yaml/en/metatitle_en')
