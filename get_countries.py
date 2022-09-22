import time
import os
import json

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ChromeOptions

from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

FILE_APPEND_DATA = 'countries.txt'

URL = os.environ['URL']
PAGE = ['3', '2', '1']


def get_countries(soup: BeautifulSoup):
    data = soup.find(id='children').find_all('a')
    return [item.get('href') for item in data]


def get_names(soup: BeautifulSoup):
    data = soup.find(id='children').find_all('a')
    return [item.get_text(strip=True) for item in data]


def main():
    service = Service(os.environ['PATH_DRIVER'])
    options = ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--incognito")
    driver = webdriver.Chrome(service=service, options=options)

    links = []
    texts = []
    while any(PAGE):
        url = ''.join((URL, PAGE.pop()))
        driver.get(url)
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        links.extend(get_countries(soup))
        texts.extend(get_names(soup))
    list_ = zip(texts, links)
    dict_ = dict(list_)

    with open(FILE_APPEND_DATA, 'a', encoding='utf-8') as file:
        json.dump(dict_, file, indent=4, ensure_ascii=False)

    driver.quit()


if __name__ == '__main__':
    main()
