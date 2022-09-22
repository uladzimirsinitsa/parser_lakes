
import json
import time
import os
import locale

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ChromeOptions

from dotenv import load_dotenv
from bs4 import BeautifulSoup
from countries import countries

load_dotenv()

locale.setlocale(locale.LC_ALL, 'en-EN')

PATH_FILE_DATA = 'data/'
FILE_URLS = 'urls.txt'



def get_urls():
    with open(FILE_URLS, encoding='utf-8') as file:

        return file.readlines()


def get_name_lake(soup: BeautifulSoup) -> tuple:
    abbr = soup.find(class_='normal-s').get_text(strip=True)
    name_lake = soup.find('h2').text.strip().rstrip(abbr).strip()
    return name_lake, abbr


def get_nations(soup: BeautifulSoup) -> list:
    data = soup.find_all('td')
    str_ = data[0].get_text(strip=True)
    list_ = str_.split(',')
    new_list = []
    for i in list_:
        i = i.strip()
        i = i.replace('Congo  ( Dem. Rep. )', 'Congo, Democratic Republic of the')
        i = i.replace('Dominican', 'Dominican Republic')
        i = i.replace('Kyrgyz', 'Kyrgyzstan')
        i = i.replace('UK', 'United Kingdom')
        i = i.replace('USA', 'United States')
        i = i.replace('Viet Nam', 'Vietnam')
        i = i.replace('Macedonia', 'North Macedonia')
        i = i.replace('Myanmar', 'Burma')
        new_list.append(i)
    return new_list


def get_link_countries(nations) -> list:
    links = []
    for i in nations:
        link = countries.get(i)
        links.append(link)
    return links


def get_area(soup: BeautifulSoup) -> str:
    data = soup.find_all('td')
    str_ = data[1].get_text(strip=True)
    str_ = str_.replace('km2', 'km²')
    number = int(str_.partition('\xa0')[0])
    km = str_.partition('\xa0')[2]
    number = locale.format_string('%10.0f', number, grouping=True)
    return ' '.join((number, km)).strip()


def get_mean_depth(soup: BeautifulSoup) -> str:
    data = soup.find_all('td')
    str_ = data[2].get_text(strip=True)
    number = float(str_.partition('\xa0')[0])
    m = str_.partition('\xa0')[2]
    number = locale.format_string('%10.1f', number, grouping=True)
    return ' '.join((number, m)).strip()


def get_volume(soup: BeautifulSoup) -> str:
    data = soup.find_all('td')
    str_ = data[3].get_text(strip=True)
    str_ = str_.replace('km3', 'km³')
    number = float(str_.partition('\xa0')[0])
    km = str_.partition('\xa0')[2]
    number = locale.format_string('%10.2f', number, grouping=True)
    return ' '.join((number, km)).strip()


def get_shoreline(soup: BeautifulSoup) -> str:
    data = soup.find_all('td')
    str_ = data[4].get_text(strip=True)
    number = float(str_.partition('\xa0')[0])
    km = str_.partition('\xa0')[2]
    number = locale.format_string('%10.0f', number, grouping=True)
    return ' '.join((number, km)).strip()


def get_catchment_area(soup: BeautifulSoup) -> str:
    data = soup.find_all('td')
    str_ = data[5].get_text(strip=True)
    str_ = str_.replace('km2', 'km²')
    number = float(str_.partition('\xa0')[0])
    km = str_.partition('\xa0')[2]
    number = locale.format_string('%10.0f', number, grouping=True)
    return ' '.join((number, km)).strip()


def get_residence_time(soup: BeautifulSoup):
    data = soup.find_all('td')
    return data[6].get_text(strip=True)


def get_frozen_period(soup: BeautifulSoup):
    data = soup.find_all('td')
    return data[7].get_text(strip=True)


def get_mixing_type(soup: BeautifulSoup):
    data = soup.find_all('td')
    return data[8].get_text(strip=True)


def get_m_d(soup: BeautifulSoup):
    data = soup.find_all('td')
    return data[9].get_text(strip=True)


def get_info(soup: BeautifulSoup):
    data = soup.find_all('td')
    str_ = data[10].get_text(strip=True)
    str_ = str_.replace('km3', 'km³')
    str_ = str_.replace('km2', 'km²')
    return str_


def get_description(soup: BeautifulSoup):
    data = soup.find(id='description').find_all('p')
    list_ = [item.text for item in data]
    return ' '.join(list_)


def main():
    service = Service(os.environ['PATH_DRIVER'])
    options = ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--incognito")
    driver = webdriver.Chrome(service=service, options=options)

    for url in get_urls():

        driver.get(url)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, 'lxml')
        name_lake, abbr = get_name_lake(soup)
        os.mkdir(f'{PATH_FILE_DATA}{abbr}')
        nations = get_nations(soup)
        links = get_link_countries(nations)

        try:
            surface_area = get_area(soup)
        except ValueError:
            surface_area = ''

        try:
            mean_depth = get_mean_depth(soup)
        except ValueError:
            mean_depth = ''

        try:
            volume = get_volume(soup)
        except ValueError:
            volume = ''

        try:
            shoreline = get_shoreline(soup)
        except ValueError:
            shoreline = ''

        try:
            catchment_area = get_catchment_area(soup)
        except ValueError:
            catchment_area = ''

        residence_time = get_residence_time(soup)
        frozen_period = get_frozen_period(soup)
        mixing_type = get_mixing_type(soup)
        m_d = get_m_d(soup)
        info = get_info(soup)
        description = get_description(soup)

        dict_ = {
            'Alias': name_lake,
            'Name short': abbr,
            'Riparian Nation(s)': nations,
            'Latitude': '',
            'Longitude': '',
            'Surface Area': surface_area,
            'Mean Depth': mean_depth,
            'Volume': volume,
            'Shoreline': shoreline,
            'Catchment Area': catchment_area,
            'Residence Time': residence_time,
            'Frozen Period': frozen_period,
            'Mixing Type': mixing_type,
            'Morphogenesis/Dam': m_d,
            'Related Info/Site': info,
            'description': description,
            'Links': links
            }

        with open(f'{PATH_FILE_DATA}card_item_{abbr}.json', 'w', encoding='utf-8') as file:
            json.dump(dict_, file, indent=4, ensure_ascii=False)

    driver.quit()


if __name__ == '__main__':
    main()
