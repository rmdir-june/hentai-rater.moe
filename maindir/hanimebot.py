import selenium, os
from bs4 import BeautifulSoup
import re, requests
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from time import sleep
from .config import token
import json

os.environ['GH_TOKEN'] = token
os.environ["DISPLAY"] = ":0"

hanime_points = {
    "bdsm": 6,
    "fantasy": 4,
    "filmed": 4,
    "foot job": 4,
    "futanari": 4,
    "gangbang": 6,
    "incest": 4,
    "inflation": 8,
    "lactation": 8,
    "loli": 10,
    "mind break": 8,
    "mind control": 8,
    "monster": 6,
    "nekomimi": 4,
    "ntr": 6,
    "orgy": 6,
    "pregnant": 8,
    "rape": 15,
    "rimjob": 10,
    "scat": 50,
    "tentacle": 6,
    "ugly bastard": 10
}
hanime_rank = {
    0: ["5% Degen", "cute <3"],
    (1, 10): ["15% Degen", "Nothing wrong with a little kinks!"],
    (10, 17): ["35% Degen", "Now that's pretty weird..."],
    (17, 30): ["50% Degen", "Do you know what the outside world is like?"],
    (30, 50): ["80% Degen", "You are the lowest of the low. There is no hope for you."],
    (50, 100): ["100% Degen", "dial 911"]
}
nhentai_points = {
    "group/": 2,
    "lolicon/": 14,
    "rape/": 20,
    "bondage/": 6,
    "incest/": 8,
    "futanari/": 2,
    "netorare/": 4,
    "tentacles/": 6,
    "mind-break/": 10,
    "lactation/": 6,
    "mind-control/": 10,
    "exhibitionism/": 6,
    "pregnant/": 6,
    "footjob/": 2,
    "gender-bender/": 2,
    "urination/": 8,
    "prostitution/": 6,
    "scat/": 50,
    "inflation/": 6,
}
nhentai_rank = {
    0: ["5% Degen", "cute <3"],
    (1, 10): ["15% Degen", "Nothing wrong with a little kinks!"],
    (10, 17): ["35% Degen", "Now that's pretty weird..."],
    (17, 30): ["50% Degen", "Do you know what the outside world is like?"],
    (30, 50): ["80% Degen", "You are the lowest of the low. There is no hope for you."],
    (50, 500): ["100% Degen", "dial 911.."]
}

with open('scores.json') as scores:
    stored_scores = json.load(scores)
    print("scores:", stored_scores)


def main(urls):
    print("feedback")
    if " " not in urls:
        if 'hanime' in urls:
            if urls in stored_scores:
                header, response = rate_hanime(stored_scores[urls])
            else:
                links = get_hanime_links(urls)
                if links is None:
                    return None, None
                rank_value = get_hanime_value(links)
                header, response = rate_hanime(rank_value)

                print(urls, "fuckalluh")
                stored_scores[urls] = rank_value

            jason = json.dumps(stored_scores)
            f = open('scores.json', 'w')
            f.write(jason)
            f.close()

            return header, response
        if 'nhentai' in urls:
            if urls in stored_scores.keys():
                header, response = rate_nhentai(stored_scores[urls])
            else:
                links, io = get_nhentai_links(urls)
                rank_value = get_nhentai_value(links, io=io)
                header, response = rate_nhentai(rank_value)

                stored_scores[urls] = rank_value

            jason = json.dumps(stored_scores)
            f = open('scores.json', 'w')
            f.write(jason)
            f.close()

            return header, response
    return None, None


def get_nhentai_links(urls):
    io = bool()
    links = str()
    html = requests.get(urls, timeout=0.5)
    soup = BeautifulSoup(html.text, 'html.parser')

    if "nhentai.net" in urls:
        links = [link['href'] for link in soup.find_all('a', {"href": re.compile('^/tag/')})]
        io = False
    elif "nhentai.io" in urls:
        links = [link['href'] for link in soup.find_all('a', {"href": re.compile('^https://nhentai.io/genre/')})]
        io = True
    else:
        links = None
        io = None
        print("error with io")
    return links, io


def get_nhentai_value(links, io):
    rank_value = int()
    if not io:
        tags = [link[5:] for link in links]
    else:
        tags = [link[25:] for link in links]
    for tag in tags:
        try:
            rank_value += nhentai_points[str(tag)]
        except KeyError:
            pass
    return rank_value


def rate_nhentai(rank_value):
    header = str()
    response = str()
    for i, key in enumerate(nhentai_rank.keys()):
        if i == 0:
            if rank_value == key:
                header = nhentai_rank[key][0]
                response = nhentai_rank[key][1]
        elif rank_value in range(key[0], key[1]):
            header = nhentai_rank[key][0]
            response = nhentai_rank[key][1]
    return header, response


def get_hanime_links(urls):
    driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
    try:
        driver.get(urls)
    except selenium.common.exceptions.InvalidArgumentException:
        return None
    try:
        if 'hanime' in urls:
            (driver.find_element_by_xpath('/html/body/div/div/div/div[4]/main/div/div/div/div[1]/button')).click()
    except:
        pass
    sleep(3)
    html = driver.page_source
    driver.close()

    soup = BeautifulSoup(html, 'html.parser')
    links = [link["href"] for link in soup.find_all('a', {"href": re.compile('^/browse/tags/'), "class": "ml-0 "
                                                                                                         "mr-3 "
                                                                                                         "btn "
                                                                                                         "btn"
                                                                                                         "--outline"
                                                                                                         " btn--dep"
                                                                                                         "ressed bt"
                                                                                                         "n--router"
                                                                                                         " grey--te"
                                                                                                         "xt"})]
    return links


def get_hanime_value(links):
    rank_value = int()
    has_multiple = 0
    tags = [link[13:] for link in links]
    for tag in tags:
        if tag == "gangbang" or "orgy":
            has_multiple = 1
        try:
            if not tag == "gangbang" or "orgy" and not has_multiple == 1:
                rank_value += hanime_points[str(tag)]
        except KeyError:
            pass
    return rank_value


def rate_hanime(rank_value):
    header = str()
    response = str()
    for i, key in enumerate(hanime_rank.keys()):
        if i == 0:
            if rank_value == key:
                print("working")
                header = hanime_rank[key][0]
                response = hanime_rank[key][1]
        elif rank_value in range(key[0], key[1]):
            print("working")
            header = hanime_rank[key][0]
            response = hanime_rank[key][1]
    return header, response

