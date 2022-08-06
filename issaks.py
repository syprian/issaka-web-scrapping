import requests
from bs4 import BeautifulSoup
import re
import json


def scrape_language_groups():
    lang_families = ['Afro-Asiatic', 'kx’', 'niger-congo', 'nilo-saharan', 'tuu', 'creole']
    dict = {'name': "African-Language-Families"}
    child_list = []
    for lang in lang_families:
        child_list.append(scrape_page(lang))
    dict['children'] = child_list
    json_dump = json.dumps(dict)
    with open("new.json", "w") as f:
        f.write(json_dump)


def generate_url(language_group):
    urlStart = 'https://www.ethnologue.com/subgroups/'
    return urlStart + language_group


def scrape_page(language_group):
    url = generate_url(language_group)
    result = requests.get(url)
    src = result.content
    soup = BeautifulSoup(src, 'lxml')
    groups = soup.find("div", {"class": "view-content indent1"})
    lang_dict = {'name': language_group}
    lang_dict['children'] = recursive_search(groups.find("div", {"class": "item-list"}), "",
                                             lang_dict)  # begin recursive search on the top level language list
    return lang_dict


def recursive_search(item_list, temp_indent, lang_dict):
    if item_list is None: return  # base case: if there are no lower levels in the tree
    list = item_list.find("ul").find_all("li", recursive=False)
    child_list = []
    for lang in list:
        leaf = lang.find("div", class_=re.compile("^view view-language"), recursive=False)
        leaf_ul = leaf.select('div > div > div > ul')
        if leaf_ul:  # if the language is the special base case, data needs to be accessed differently
            leaf_list = leaf_ul[0].find_all("li", recursive=False)
            for leaf_lang in leaf_list:
                print(temp_indent + leaf_lang.find("span", {"class": "field-content"}).text)
                leaf_dict = {'name': leaf_lang.find("span", {"class": "field-content"}).text.split('(')[0],
                             'value': 1111}
                child_list.append(leaf_dict)
        print(temp_indent + lang.find('a').string)
        sub_dict = {'name': lang.find('a').string.split('(')[0],
                    'children': recursive_search(lang.find("div", {"class": "item-list"}, recursive=False),
                                                 temp_indent + "    ", lang_dict)}
        child_list.append(sub_dict)
    return child_list


scrape_language_groups()