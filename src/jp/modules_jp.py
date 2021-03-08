import sys
sys.path.append('../')
import pandas as pd
import numpy as np
import yaml
from collections import ChainMap
import common

def classify_scp(tags: list) -> str:
    class_name_list = [
        'neutralized',
        'thaumiel',
        'keter',
        'euclid',
        'safe']
    for class_name in class_name_list:
        if class_name in tags:
            return class_name
    return 'others'


def remove_adult(obj: dict) -> dict:
    keys = list(obj.keys())
    for key in keys:
        if 'adult:' in key:
            new_key = key.replace('adult:', '')
            obj[new_key] = obj[key]
            obj.pop(key)
    return obj


class SCP():
    def __init__(self, path) -> None:
        self.path = path
        self.load_yaml()
        self.merge_obj()
        self.create_summ_obj()

    def load_yaml(self):
        with open(self.path + 'scp_jp.yaml') as file:
            self.scp_jp_obj = remove_adult(yaml.safe_load(file))
        with open(self.path + 'scp_001_jp.yaml') as file:
            self.scp_001_obj = remove_adult(yaml.safe_load(file))
        with open(self.path + 'ex_scp_jp.yaml') as file:
            self.ex_obj = remove_adult(yaml.safe_load(file))
        with open(self.path + 'arc_scp_jp.yaml') as file:
            self.arc_obj = remove_adult(yaml.safe_load(file))
        # with open(self.path + 'd_scp_jp.yaml') as file:
        #     self.d_obj = remove_adult(yaml.safe_load(file))
        with open(self.path + 'j_scp_jp.yaml') as file:
            self.j_obj = remove_adult(yaml.safe_load(file))

        with open(self.path + 'metatitle_jp.yaml') as file:
            self.scp_jp_mt_obj = remove_adult(yaml.safe_load(file))
        with open(self.path + 'ex_metatitle_jp.yaml') as file:
            self.ex_mt_obj = remove_adult(yaml.safe_load(file))
        with open(self.path + 'arc_metatitle_jp.yaml') as file:
            self.arc_mt_obj = remove_adult(yaml.safe_load(file))
        # with open(self.path + 'd_metatitle_jp.yaml') as file:
        #     self.d_mt_obj = remove_adult(yaml.safe_load(file))
        with open(self.path + 'j_metatitle_jp.yaml') as file:
            self.j_mt_obj = remove_adult(yaml.safe_load(file))

        with open(self.path + 'tale_by_series_jp.yaml') as file:
            self.tale_by_series_obj = remove_adult(yaml.safe_load(file))
        with open(self.path + 'tale_jp.yaml') as file:
            self.tale_obj = remove_adult(yaml.safe_load(file))
        with open(self.path + 'essay_jp.yaml') as file:
            self.essay_obj = remove_adult(yaml.safe_load(file))
        self.other_obj = self.essay_obj

        with open(self.path + 'supplement_jp.yaml') as file:
            self.supp_obj = remove_adult(yaml.safe_load(file))

    def merge_obj(self):
        self.scp_obj = ChainMap(self.scp_jp_obj,
                                self.scp_001_obj,
                                self.ex_obj,
                                self.arc_obj,
                                # self.d_obj,
                                self.j_obj)
        self.all_pages_obj = ChainMap(
            self.scp_obj, self.tale_obj, self.other_obj)
        self.scp_001_mt_obj = {}
        for key in self.scp_001_obj.keys():
            self.scp_001_mt_obj[key] = self.scp_001_obj[key]['title']
        self.scp_mt_obj = ChainMap(self.scp_jp_mt_obj,
                                   self.scp_001_mt_obj,
                                   self.ex_mt_obj,
                                   self.arc_mt_obj,
                                   #    self.d_mt_obj,
                                   self.j_mt_obj)
        self.scp_mt_obj_keys = self.scp_mt_obj.keys()

    def add_from_tale_obj(self):
        tale_obj_keys = self.tale_obj.keys()
        for key in tale_obj_keys:
            links = self.tale_obj[key]['links']
            for link in links:
                if link in self.scp_obj.keys():
                    self.summ_obj[link]['appears_in'].add(key)

    def add_from_essay_obj(self):
        essay_obj_keys = self.essay_obj.keys()
        for key in essay_obj_keys:
            links = self.essay_obj[key]['links']
            for link in links:
                if link in self.scp_obj.keys():
                    self.summ_obj[link]['appears_in'].add(key)

    def add_from_supp(self, key):
        if key not in self.supp_obj.keys():
            return
        supp_obj_list = self.supp_obj[key]['links']
        for supp_obj in supp_obj_list:
            name = list(supp_obj.keys())[0]
            self.summ_obj[key]['cites'].discard(name)
            links = supp_obj[name]['links']
            tags = supp_obj[name]['tags']
            if 'supplement' not in tags:
                continue
            self.summ_obj[key]['cites'] |= set(links)

    def create_summ_obj(self):
        self.summ_obj = {}
        for key in self.scp_obj.keys():
            self.summ_obj[key] = {
                'metatitle': '',
                'rate': '',
                'object_type': '',
                'cites': set([]),
                'cited_by': set([]),
                'appears_in': set([])}
        self.add_from_tale_obj()
        self.add_from_essay_obj()

        for key in self.scp_obj.keys():
            # Add 'metatitle'
            if key in self.scp_mt_obj.keys():
                self.summ_obj[key]['metatitle'] = self.scp_mt_obj[key]
            # Add 'rate'
            self.summ_obj[key]['rate'] = self.scp_obj[key]['rate']
            # Add 'object_type'
            self.summ_obj[key]['object_type'] = classify_scp(
                self.scp_obj[key]['tags'])
            # Add 'cites'
            self.summ_obj[key]['cites'] = set(self.scp_obj[key]['links'])
            self.add_from_supp(key)
            # Add 'cited_by' of other objects
            for cite in self.summ_obj[key]['cites']:
                if cite in self.scp_obj:
                    self.summ_obj[cite]['cited_by'].add(key)
                # Add tales cited in the site to 'appears_in'
                # elif cite in self.tale_obj:
                #     self.summ_obj[key]['appears_in'].add(cite)
            # Add 'appears_in'
            if key in self.tale_by_series_obj.keys():
                self.summ_obj[key]['appears_in'] |= set(
                    self.tale_by_series_obj[key])


class MarkdownWriter():
    def __init__(self, scp: SCP, path: str) -> None:
        self.scp = scp
        self.path = path

    def format_object_link(self, link: str) -> str:
        # if link in self.scp.scp_001_obj.keys():
        #     title = 'SCP-001'
        if 'decomm:' in link:
            title = link.replace('decomm:', '').upper()
        else:
            title = link.upper()
        metatitle = self.scp.summ_obj[link]['metatitle']
        rate = self.scp.summ_obj[link]['rate']
        result = f'    - [{title}]({common.jp_url}{link}) '
        if rate != 'unknown':
            return result + f'({metatitle}, {rate})\n'
        else:
            return result + f'({metatitle})\n'

    def format_tale_link(self, link: str) -> str:
        title = self.scp.tale_obj[link]['title']
        rate = self.scp.tale_obj[link]['rate']
        result = f'    - [{title}]({common.jp_url}{link})'
        if rate != 'unknown':
            return result + f' ({rate})\n'
        else:
            return result + '\n'

    def format_other_link(self, link: str) -> str:
        title = self.scp.other_obj[link]['title']
        rate = self.scp.other_obj[link]['rate']
        result = f'    - [{title}]({common.jp_url}{link})'
        if rate != 'unknown':
            return result + f' ({rate})\n'
        else:
            return result + '\n'

    def classify_links(self, links: list) -> list:
        object_links = []
        tale_links = []
        other_links = []
        for link in links:
            if link in self.scp.scp_obj.keys():
                object_links.append(link)
            elif link in self.scp.tale_obj.keys():
                tale_links.append(link)
            elif link in self.scp.other_obj.keys():
                other_links.append(link)
            else:
                obj = common.create_obj_from_link(link, excludes=[link])
                if obj is None:
                    continue
                self.scp.other_obj[link] = obj[link]
                other_links.append(link)
        return [object_links, tale_links, other_links]

    def sort_by_rate(self, links: list) -> list:
        rates = []
        for link in links:
            rate = self.scp.all_pages_obj[link]['rate']
            if rate == 'unknown':
                rates.append(0)
            else:
                rates.append(int(rate))
        idx = np.argsort(rates)[::-1]
        sorted_links = np.array(links)[idx]
        return sorted_links

    def format_cited_by_links(self, links: list) -> str:
        sorted_object_links = self.sort_by_rate(links)
        # Format to str
        result = ''
        if len(sorted_object_links) != 0:
            result += f'- **Cited by {len(links)} SCPs**:\n'
        for link in sorted_object_links:
            result += self.format_object_link(link)
        return result

    def format_appears_in_links(self, links: list) -> str:
        [object_links, tale_links, other_links] = self.classify_links(links)
        sorted_object_links = self.sort_by_rate(object_links)
        sorted_tale_links = self.sort_by_rate(tale_links)
        sorted_other_links = self.sort_by_rate(other_links)
        # Format to str
        result = ''
        if len(sorted_object_links) != 0:
            result += f'- **Appears in {len(sorted_object_links)} SCPs**:\n'
        for link in sorted_object_links:
            result += self.format_object_link(link)
        if len(sorted_tale_links) != 0:
            result += f'- **Appears in {len(sorted_tale_links)} tales**:\n'
        for link in sorted_tale_links:
            result += self.format_tale_link(link)
        if len(sorted_other_links) != 0:
            result += f'- **Associated with**:\n'
        for link in sorted_other_links:
            result += self.format_other_link(link)
        return result

    def format_each_scp(self, key: str) -> str:
        result = ''
        scp_title = key.replace('decomm:', '')
        metatitle = self.scp.summ_obj[key]['metatitle']
        rate = self.scp.summ_obj[key]['rate']

        cited_by = self.scp.summ_obj[key]['cited_by']
        cited_by_result = self.format_cited_by_links(list(cited_by))

        appears_in = self.scp.summ_obj[key]['appears_in'] - cited_by
        appears_in_result = self.format_appears_in_links(appears_in)

        result += f'### [{scp_title.upper()}]({common.jp_url + key})\n' + \
            f'- **Metatitle**: {metatitle}\n' + \
            f'- **Rate**: {rate}\n' + \
            f'{cited_by_result}' + \
            f'{appears_in_result}'
        return result

    def save_scp(self) -> None:
        series = ['I', 'II', 'III']
        # series = ['I', 'II', 'III', 'IV', 'V', 'VI']
        for i in range(0, 3):
            # for i in range(0, 6):
            result = '# Series ' + series[i] + '\n\n'
            print('-----', series[i], '-----')
            a = i * 1000
            for j in range(0, 10):
                b = a + j * 100
                result += f'## {common.format_num(max(2, b))} to {common.format_num(b + 99)}\n\n'
                for k in range(0, 100):
                    c = b + k
                    scp_id = common.format_num(c)
                    scp_title = 'scp-' + scp_id + '-jp'
                    if scp_title in self.scp.scp_obj.keys():
                        result += self.format_each_scp(scp_title) + '\n'
            with open(self.path + f'scp_by_series_jp/series{i + 1}.md', 'w', encoding='utf-8') as file:
                file.write(result)

    def save_to_markdown(self) -> None:
        self.save_scp()

        scp_001_result = '# SCP-001\n\n'
        for obj in self.scp.scp_001_obj:
            scp_001_result += self.format_each_scp(obj) + '\n'
        with open(self.path + 'scp_by_series_jp/scp-001.md', 'w', encoding='utf-8') as file:
            file.write(scp_001_result)

        ex_result = '# Explained SCPs\n\n'
        for obj in self.scp.ex_obj:
            ex_result += self.format_each_scp(obj) + '\n'
        with open(self.path + 'other_scps_jp/explained.md', 'w', encoding='utf-8') as file:
            file.write(ex_result)

        arc_result = '# Archived SCPs\n\n'
        for obj in self.scp.arc_obj:
            arc_result += self.format_each_scp(obj) + '\n'
        with open(self.path + 'other_scps_jp/archived.md', 'w', encoding='utf-8') as file:
            file.write(arc_result)

        # d_result = '# Decommissioned SCPs\n\n'
        # for obj in self.scp.d_obj:
        #     d_result += self.format_each_scp(obj) + '\n'
        # with open(self.path + 'other_scps/decommissioned.md', 'w', encoding='utf-8') as file:
        #     file.write(d_result)

        j_result = '# Joke SCPs\n\n'
        for obj in self.scp.j_obj:
            j_result += self.format_each_scp(obj) + '\n'
        with open(self.path + 'other_scps_jp/joke.md', 'w', encoding='utf-8') as file:
            file.write(j_result)


class GraphDataWriter():
    def __init__(self, scp: SCP, path: str) -> None:
        self.scp = scp
        self.path = path

    def create_points(self) -> np.ndarray:
        keys = list(self.scp.scp_jp_obj.keys())
        keys.extend(list(self.scp.scp_001_obj.keys()))
        data_store = np.empty((len(keys), 8), dtype='object')
        for i in range(len(keys)):
            key = keys[i]
            data_store[i][0] = key.upper()
            data_store[i][1] = self.scp.summ_obj[key]['object_type'].capitalize()
            data_store[i][2] = self.scp.summ_obj[key]['rate']
            data_store[i][3] = self.scp.summ_obj[key]['metatitle']
            data_store[i][4] = len(self.scp.summ_obj[key]['cites'])
            data_store[i][5] = len(self.scp.summ_obj[key]['cited_by'])
            data_store[i][6] = len(self.scp.summ_obj[key]['appears_in'])
            if key in self.scp.scp_jp_obj.keys():
                num = int(key.replace('scp-', '').replace('-jp', ''))
                series_num = num // 1000 + 1
                data_store[i][7] = f'https://iwasaki501.github.io/ternbusty/scp_by_series_jp/series' + \
                    f'{series_num}.html#{key}'
            else:
                data_store[i][
                    7] = f'https://iwasaki501.github.io/ternbusty/scp_by_series_jp/scp-001.html#{key}'
        # points = data_store[data_store[:, 5] > 1]
        points = data_store
        return points

    def remove_orphan_nodes(
            self,
            points: np.ndarray,
            not_orphan_set: set) -> np.ndarray:
        all_set = set(points[:, 0])
        orphan_set = all_set - not_orphan_set
        delete_row_idx = []
        for orphan in orphan_set:
            delete_row_idx.append(np.where(points[:, 0] == orphan)[0][0])
        return np.delete(points, delete_row_idx, axis=0)

    def save_points_file(self, points: np.ndarray) -> None:
        column_name = [
            'ID',
            'ObjectType',
            'Rate',
            'Metatitle',
            'CitesNum',
            'CitedByNum',
            'AppearsInNum',
            'URL']

        df = pd.DataFrame(points, columns=column_name)
        df.to_csv(self.path + 'Points.csv', index=False)

    def create_links(self, points: np.ndarray) -> list:
        selected_scp = points[:, 0]
        target_list = []
        source_list = []
        not_orphan_set = set([])
        for row in points:
            target = row[0]
            for cite in self.scp.summ_obj[target.lower()]['cites']:
                if cite.upper() in selected_scp:
                    target_list.append(target)
                    source_list.append(cite.upper())
                    not_orphan_set.add(target)
                    not_orphan_set.add(cite.upper())
        return [target_list, source_list], not_orphan_set

    def save_links_file(self, links: list) -> None:
        links = pd.concat([pd.DataFrame(links[0]),
                           pd.DataFrame(links[1])], axis=1)
        links.columns = ['Source', 'Target']
        links.to_csv(self.path + 'Links.csv', index=False)

    def save_to_csv(self):
        points = self.create_points()
        links, not_orphan_set = self.create_links(points)
        points = self.remove_orphan_nodes(points, not_orphan_set)
        self.save_points_file(points)
        self.save_links_file(links)
