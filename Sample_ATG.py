import csv
import requests

from bs4 import BeautifulSoup


class Sample_pars:
    def __init__(self, url, name, paginationCD):
        self.url = url
        self.name = name
        self.CSV = str(self.name) + '.csv'
        self.paginationCD = paginationCD

    @staticmethod
    def get_html(url, params=None):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/94.0.4606.71 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}
        r = requests.get(url, headers=headers, params=params)
        return r

    @staticmethod
    def save_file(items, path):
        with open(path, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Article', 'Availability', 'uah_price', 'link'])
            for item in items:
                writer.writerow([item['title'], item['Availability'], item['uah_price'], item['link']])


class AtgPars(Sample_pars):
    def __init__(self, url, name, paginationCD):
        super().__init__(url, name, paginationCD)

    def parser(self):
        attribute_pars = []
        if self.get_html(self.url).status_code == 200:
            for page in range(1, self.paginationCD + 1):
                print(f'Scraping page {page}')
                html_save = self.get_html(self.url, params={'page': page})
                attribute_pars.extend(self.get_content(html_save.text))
            self.save_file(attribute_pars, self.CSV)
        else:
            print('Error')

    @staticmethod
    def get_content(html):
        items = BeautifulSoup(html, 'html.parser').find_all('div', class_='product-layout')
        attribute = []
        for item in items:
            availability = 'Yes' if (item.find('div', class_='availability-triangle')) else 'No'
            attribute.append({
                'title': item.find('div', class_='articlemodel').get_text(strip=True),
                'Availability': availability,
                'uah_price': item.find('p', class_='price').get_text(strip=True),
                'link': item.find('a', class_='').get('href'),
            })
        return attribute


object1 = AtgPars('https://atg-ua.com.ua/nasosy/gur', "pumps", 3)
object1.parser()

object2 = AtgPars('https://atg-ua.com.ua/rulevye-reyki/elektricheskie', "StEPS", 6)
object2.parser()
