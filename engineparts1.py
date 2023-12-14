import time
import requests
import glob
import csv

from selenium import webdriver as wd
from bs4 import BeautifulSoup

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/113.0.0.0 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
              '*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'}

url_ = 'http://engineparts.com.ua/engines/'


def link_makr_save():
    a = requests.get(url=url_, headers=headers)
    soup = BeautifulSoup(a.text, 'html.parser')
    links_makr = []
    items = soup.find_all('div', class_='morph pic')
    count = 0
    for item in items:
        links = item.find("a").get('href')
        count += 1
        links_makr.append(links)
    links_makr.pop(0)
    return links_makr


links_makr = link_makr_save()


def link_cars_save():
    total_score = 0
    links_cars_save1 = []
    for link in links_makr:
        total_score += 1
        count2 = 0
        b = requests.get(url=link, headers=headers)
        soup2 = BeautifulSoup(b.text, 'html.parser')
        link_cars = soup2.find_all('div', class_='blog-cont')
        for item in link_cars:
            links = item.find("a", class_="sectls-img").get('href')
            links_cars_save1.append(links)
            count2 += 1
            print(total_score, count2)
    return links_cars_save1


link_cars_pars = link_cars_save()


def pars_car_links():
    attribute = []
    for link_pars in link_cars_pars:
        link = link_pars
        c = requests.get(url=link_pars, headers=headers)
        soup3 = BeautifulSoup(c.text, 'html.parser')
        marks = BeautifulSoup(c.text, 'html.parser').find_all("span", itemprop="title")
        title = soup3.find("h3", id="orderItemName").text
        uah_price = soup3.find("strong", id="itemPrice").text
        manufacturer = soup3.find("dd", style="width:65%").text \
            if soup3.find("dd", style="width:65%").text else "no"

        applicability = soup3.find("p", style="color:#000;padding: 10px 1px;").text[
                        len("Применимость:"):] if soup3.\
            find("p", style="color:#000;padding: 10px 1px;").text else "no"

        description = BeautifulSoup(c.text, 'html.parser').find("div", id="prod-tab-1").text[
                      :-len("шаблоны для dle 11.2 ")].strip() if BeautifulSoup(c.text, 'html.parser').\
            find("div", id="prod-tab-1").text else "No"

        soup3_engine_characteristics = soup3.find("dl", style="margin-top: -15px;").find_all("dd")

        img_back = BeautifulSoup(c.text, 'html.parser').find("div", class_="flex-viewport").find("img")
        print(img_back)

        attribute.append({
            "mark": marks[2].text,
            'title': title,
            'uah_price': uah_price,
            'link': link,
            'Manufacturer': manufacturer,
            'Applicability': applicability,
            'Description': soup3_engine_characteristics[0].text,
            'Volume': soup3_engine_characteristics[1].text,
            'Pover': soup3_engine_characteristics[2].text,
            'Mileage': soup3_engine_characteristics[3].text,
            'Type': soup3_engine_characteristics[4].text,
            'IMG': img_back,

        })
    return attribute


pars_car_links()
