import time
import os
import json

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ChromeOptions

from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

FILE_URLS_COUNTRIES = 'short_countries_urls.txt'
FILE_COORDS_JSON = 'coordinates.json'


def get_urls():
    with open(FILE_URLS_COUNTRIES, encoding='utf-8') as file:
        return file.readlines()


def get_name(soup: BeautifulSoup):
    data = soup.find_all(class_='lake-name')
    return [str_.get_text(strip=True) for str_ in data]


def get_coordinate(soup):
    data = soup.find_all(class_='data-body')
    coords = []
    for i in data:
        latitude = i.find(class_='lake-lat').get_text(strip=True)
        longitude = i.find(class_='lake-lng').get_text(strip=True)
        coords.append({'latitude': latitude, 'longitude': longitude})
    return coords


def main():
    service = Service(os.environ['PATH_DRIVER'])
    options = ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--incognito")
    driver = webdriver.Chrome(service=service, options=options)

    aliases = []
    coords = []
    urls = get_urls()
    while any(urls):
        url = urls.pop()
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        alias = get_name(soup)
        coordinate = get_coordinate(soup)
        aliases.extend(alias)
        coords.extend(coordinate)

    list_ = zip(aliases, coords)
    dict_ = dict(list_)

    with open(FILE_COORDS_JSON, 'a', encoding='utf-8') as file:
        json.dump(dict_, file, indent=4, ensure_ascii=False)
    driver.quit()


if __name__ == '__main__':
    main()
