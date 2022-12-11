import csv
import requests
from bs4 import BeautifulSoup


class Sample_pars:
    def __init__(self, url, name, paginationCD):
        self.url = url
        self.name = name
        self.CSV = str(self.name) + '.csv'
        self.paginationCD = paginationCD
        self.count = 0

    @staticmethod
    def get_html(url, params=None):
        session = requests.Session()
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'}
        datas = {
            'email': 'zakupki@masterservice.ms',
            'password': 'master_service'

        }
        session.post('https://atg-ua.com.ua/avtorizaciya', data=datas, headers=headers, params=None,
                     allow_redirects=True)
        session.post('https://atg-ua.com.ua/lichniy-kabinet', data=datas, headers=headers, params=None,
                     allow_redirects=True)
        session.post('https://atg-ua.com.ua/avtorizaciya', data=datas, headers=headers, params=None,
                     allow_redirects=True)
        session.post('https://atg-ua.com.ua/lichniy-kabinet', data=datas, headers=headers, params=None,
                     allow_redirects=True)
        r = session.get(url, headers=headers, params=params)

        return r

    @staticmethod
    def save_file(items, path):
        with open(path, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Article', 'Availability', 'uah_price', 'link'])
            for item in items:
                writer.writerow([item['title'], item['Availability'], item['uah_price'], item['link']])


class AtgPars_Agregats(Sample_pars):
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
        items = BeautifulSoup(html, 'html.parser').find_all('div', class_='product-block-inner')
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


class AtgPars_SEALS(AtgPars_Agregats):
    @staticmethod
    def get_content(html):
        items = BeautifulSoup(html, 'html.parser').find_all('div', class_='product-block-inner')
        attribute = []
        for item in items:
            availability = 'Yes' if (item.find('div', class_='availability-triangle')) else 'No'
            attribute.append({
                'title': item.find('div', class_='articlemodel').get_text(strip=True),
                'Availability': availability,
                'Manufacturer': item.find('div', class_='manufacturer_product').get_text(strip=True),
                'uah_price': item.find('p', class_='price').get_text(strip=True),
                'link': item.find('a', class_='').get('href'),
            })
        return attribute

    @staticmethod
    def save_file(items, path):
        with open(path, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Article', 'Availability', 'Manufacturer', 'uah_price', 'link'])
            for item in items:
                writer.writerow(
                    [item['title'], item['Availability'], item['Manufacturer'], item['uah_price'], item['link']])


class Gur_Service(Sample_pars):
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
    def get_html(url, params=None):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'}
        r = requests.get(url, headers=headers, params=params)

        return r

    @staticmethod
    def get_content(html):
        items = BeautifulSoup(html, 'html.parser').find('div', class_='products-list-box').find_all('div',
                                                                                                    class_='item')
        attribute = []
        for item in items:
            availability = 'Yes' if (
                item.find('div', class_='status table-cell').find('span', class_='title')) else 'No'
            attribute.append({
                'title': item.find('span', class_='car-model').get_text(strip=True),
                'Availability': availability,
                'uah_price': item.find('div', class_='current-price').get_text(strip=True),
                'link': item.find('a', class_='').get('href'),
            })
        return attribute

    @staticmethod
    def save_file(items, path):
        with open(path, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Article', 'Availability', 'uah_price', 'link'])
            for item in items:
                writer.writerow([item['title'], item['Availability'], item['uah_price'], item['link']])


def list_other_gur():
    object1 = AtgPars_Agregats('https://atg-ua.com.ua/nasosy/gur', "GUR_pumps", 3)
    object1.parser()

    object3 = AtgPars_Agregats('https://atg-ua.com.ua/rulevye-reyki/gidravlicheskie', "StGUR", 22)
    object3.parser()

    object4 = AtgPars_Agregats('https://atg-ua.com.ua/rulevye-reyki/mehanicheskie', "StMEH", 5)
    object4.parser()


def list_other_eps():
    object1 = AtgPars_Agregats('https://atg-ua.com.ua/nasosy/egur', "EPS_pumps", 3)
    object1.parser()

    object2 = AtgPars_Agregats('https://atg-ua.com.ua/rulevye-reyki/elektricheskie', "StEPS", 7)
    object2.parser()


def list_other_Seals():
    object4 = AtgPars_SEALS('https://atg-ua.com.ua/komplektuyushchie/salniki', "Seals", 28)
    object4.parser()

# object6 = Gur_Service('https://nasosy-reyki.com.ua/tovary/rulevaya-reika/rulevyye-reyki-s-gur/?page=', "GurS_StGUR",1)
# object6.parser()


def list_other_emmetec():
    object1 = AtgPars_Agregats('https://atg-ua.com.ua/index.php?route=product/category&path=438_491', "БАЧКИ_И_КРЫШКИ",
                               1)
    object1.parser()

    object2 = AtgPars_Agregats('https://atg-ua.com.ua/komplektuyushchie/valy', "ВАЛЫ", 3)
    object2.parser()

    object3 = AtgPars_Agregats('https://atg-ua.com.ua/index.php?route=product/category&path=438_499',
                               "ДАТЧИКИ, СЕНСОРЫ, СЕРВО", 1)
    object3.parser()

    object4 = AtgPars_Agregats('https://atg-ua.com.ua/komplektuyushchie/zaglushki', "ЗАГЛУШКИ", 1)
    object4.parser()

    object5 = AtgPars_Agregats('https://atg-ua.com.ua/index.php?route=product/category&path=438_495', "ЗАЩИТНЫЕ КРЫШКИ",
                               2)
    object5.parser()

    object6 = AtgPars_Agregats('https://atg-ua.com.ua/komplektuyushchie/kolpachki', "КОЛПАЧКИ, ЗАЩИТНЫЕ МАНЖЕТЫ", 1)
    object6.parser()

    object7 = AtgPars_Agregats('https://atg-ua.com.ua/komplektuyushchie/kolca-rezino-metal', "КОЛЬЦА РЕЗИНО-МЕТАЛ", 1)
    object7.parser()

    object8 = AtgPars_Agregats('https://atg-ua.com.ua/index.php?route=product/category&path=438_497',
                               "КОНТАКТНАЯ ГРУППА, РАЗЬЕМЫ", 3)
    object8.parser()

    object9 = AtgPars_Agregats('https://atg-ua.com.ua/index.php?route=product/category&path=438_496', "КОРПУСА", 3)
    object9.parser()

    object10 = AtgPars_Agregats('https://atg-ua.com.ua/komplektuyushchie/krestoviny', "КРЕСТОВИНЫ", 1)
    object10.parser()

    object11 = AtgPars_Agregats('https://atg-ua.com.ua/index.php?route=product/category&path=438_498',
                                "МОТОРЫ, РЕДУКТОРА", 3)
    object11.parser()

    object12 = AtgPars_Agregats('https://atg-ua.com.ua/komplektuyushchie/podshipniki', "ПОДШИПНИКИ", 2)
    object12.parser()

    object13 = AtgPars_Agregats('https://atg-ua.com.ua/komplektuyushchie/porshni', "ПОРШНИ", 1)
    object13.parser()

    object14 = AtgPars_Agregats('https://atg-ua.com.ua/index.php?route=product/category&path=438_494', "ПРОВОДА", 1)
    object14.parser()

    object15 = AtgPars_Agregats('https://atg-ua.com.ua/komplektuyushchie/pylniki-tyag', "ПЫЛЬНИКИ ТЯГ", 2)
    object15.parser()

    object16 = AtgPars_Agregats('https://atg-ua.com.ua/komplektuyushchie/raznoe', "РАЗНОЕ", 1)
    object16.parser()

    object17 = AtgPars_Agregats('https://atg-ua.com.ua/komplektuyushchie/raspredelitel', "РАСПРЕДЕЛИТЕЛЬ", 1)
    object17.parser()

    object18 = AtgPars_Agregats('https://atg-ua.com.ua/komplektuyushchie/regulirovochnye-vtulki',
                                "РЕГУЛИРОВОЧНЫЕ ВТУЛКИ", 2)
    object18.parser()

    object19 = AtgPars_Agregats('https://atg-ua.com.ua/komplektuyushchie/rezinovye-o-ring', "РЕЗИНОВЫЕ O-RING", 8)
    object19.parser()

    object20 = AtgPars_Agregats('https://atg-ua.com.ua/index.php?route=product/category&path=438_493', "РЕМНИ", 1)
    object20.parser()

    object21 = AtgPars_Agregats('https://atg-ua.com.ua/komplektuyushchie/saylentbloki', "САЙЛЕНТБЛОКИ", 1)
    object21.parser()

    object22 = AtgPars_Agregats('https://atg-ua.com.ua/komplektuyushchie/teflonovye-kolca', "ТЕФЛОНОВЫЕ КОЛЬЦА", 4)
    object22.parser()

    object23 = AtgPars_Agregats('https://atg-ua.com.ua/index.php?route=product/category&path=438_492', "ТОРСИОНЫ", 2)
    object23.parser()

    object24 = AtgPars_Agregats('https://atg-ua.com.ua/komplektuyushchie/trubki', "ТРУБКИ", 2)
    object24.parser()

    object25 = AtgPars_Agregats('https://atg-ua.com.ua/komplektuyushchie/tyagi', "ТЯГИ", 1)
    object25.parser()

    object26 = AtgPars_Agregats('https://atg-ua.com.ua/komplektuyushchie/uplotniteli-rezino-metall',
                                "УПЛОТНИТЕЛИ РЕЗИНО-МЕТАЛЛ", 2)
    object26.parser()

    object27 = AtgPars_Agregats('https://atg-ua.com.ua/komplektuyushchie/fole-vstavka', "ФОЛЬЕ ВСТАВКА", 2)
    object27.parser()

    object28 = AtgPars_Agregats('https://atg-ua.com.ua/komplektuyushchie/homuty', "ХОМУТЫ", 1)
    object28.parser()

    object29 = AtgPars_Agregats('https://atg-ua.com.ua/komplektuyushchie/shayby', "ШАЙБЫ", 1)
    object29.parser()

    object30 = AtgPars_Agregats('https://atg-ua.com.ua/komplektuyushchie/elektro-zapchasti', "ЭЛЕКТРО ЗАПЧАСТИ", 1)
    object30.parser()


list_other_emmetec()
# list_other_gur()
# list_other_eps()
# list_other_Seals()

