import re
import yaml
from time import sleep
from random import random
import common


def process_supplement(
        child: str,
        parent: str,
        new_obj: dict,
        visited: set) -> None:
    num = re.findall(r'\d+', parent)[0]
    tmp_obj = common.create_obj_from_link(child, excludes=[parent, child])
    if tmp_obj is None:
        return
    new_obj[parent]['links'].append(tmp_obj)
    visited.add(child)
    for link in tmp_obj[child]['links']:
        if (num in link) & (link not in visited):
            process_supplement(link, parent, new_obj, visited)


if __name__ == '__main__':
    with open('scp_en.yaml') as file:
        obj = yaml.safe_load(file)
    keys = list(obj.keys())

    for i in range(0, len(keys)):
        key = keys[i]
        num = re.findall(r'\d+', key)[0]
        print(i, '/', len(keys))
        links = obj[key]['links']
        visited = set(links)
        visited.add(key)
        new_obj = {key: {'links': []}}
        for link in links:
            if num in link:
                process_supplement(link, key, new_obj, visited)
        if len(new_obj[key]['links']) == 0:
            continue
        with open('../../yaml/en/supplement_en.yaml', 'a') as file:
            yaml.dump(new_obj, file)
        sleep(random() * 10 + 2)
