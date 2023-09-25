import time
import requests
import glob
import csv

from selenium import webdriver as wd
from bs4 import BeautifulSoup

"""
"""


def parce_site_in_html_files():
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/113.0.0.0 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                  '*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'}

    url_ = 'https://aleto.ua/autoparts/'
    a = requests.get(url=url_, headers=headers)
    soup = BeautifulSoup(a.text, 'html.parser')
    links_makr = []
    items = soup.find_all('li', class_='col-12 col-sm-4 col-xs-6')
    count = 0
    for item in items:
        links = item.find("a").get('href')
        count += 1
        links_makr.append(links)

    total_score = 0
    for link in links_makr:
        total_score += 1
        count = 0
        while True:
            # if total_score < 28: ##Если сбой программы
            #     break
            driver = wd.Chrome()

            try:

                count += 1
                link_car = link + f"page-{count}"
                print(link_car)
                driver.get(url=link_car)
                html_ = driver.page_source

                if not BeautifulSoup(html_, 'html.parser').find('div', class_='col-3 col-bg-4 col-sm-6 mb'):
                    print("break")
                    break

                with open(
                        f'C:/Users/GameMax/Desktop/Visual_cloud_Python/Gid_Phyton_Visual_cloud/Pars_other/HTML_save_link/{total_score}_{count}.html',
                        'w', encoding='utf-8-sig') as file:
                    file.write(driver.page_source)
                time.sleep(2)

            except Exception as _ex:
                print(_ex)

            finally:
                driver.close()
                driver.quit()


def pars_html_file():
    path_ = r"C:\Users\GameMax\Desktop\Visual_cloud_Python\Gid_Phyton_Visual_cloud\Pars_other\HTML_save_link\*.html"
    a = (glob.glob(path_))
    count = 0

    with open('Aleto.csv', 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Article', 'Number', 'Manufacturer', 'uah_price', 'usd_price', 'link', 'Img'])

    for link in a:
        count += 1
        with open(link, 'r', encoding='utf-8') as f:
            html = f.read()

        attribute = []
        soup = BeautifulSoup(html, "lxml")
        items = soup.find_all('div', class_='col-3 col-bg-4 col-sm-6 mb')

        for item in items:
            usd_price = item.find('div', class_='detail-item-uprice').get_text(strip=True).replace(' $', '').replace(
                '.', ',') \
                if item.find('div', class_='detail-item-uprice') else 0

            uah_price = item.find('div', class_='detail-item-price').get_text(strip=True).replace(' грн', '') \
                if item.find('div', class_='detail-item-price') else 0

            link = item.find('a', class_='detail-item-img').get('href')

            Article = item.find('div', class_='col-5').get_text(strip=True).replace('Арт.', '')

            Number = item.find('div', class_='col-7').get_text(strip=True).replace('Номер', '')

            Manufacturer = item.find('a', class_='detail-item-img').get('title')

            Img = item.find('img', class_='lazy').get('data-src')

            attribute.append({
                'Article': Article,
                'Number': Number,
                'Manufacturer': Manufacturer,
                'uah_price': uah_price,
                'usd_price': usd_price,
                'link': link,
                'Img': Img,
            })
        with open('Aleto.csv', 'a', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';')
            for item in attribute:
                writer.writerow([
                    item['Article'],
                    item['Number'],
                    item['Manufacturer'],
                    item['uah_price'],
                    item['usd_price'],
                    item['link'],
                    item['Img']
                ])
        print(count)


parce_site_in_html_files()  # Парсим сайт и сохраняем страници с товаром.
pars_html_file()  # Забираем данные с сохраненных html файлов и сохраняем.
