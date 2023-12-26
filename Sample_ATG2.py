import csv

import requests
from bs4 import BeautifulSoup

from wrvwer import TLSAdapter


# import time


class SamplePars:
    def __init__(self, url, name, pagination_cd):
        self.url = url
        self.name = name
        self.CSV = str(self.name) + '.csv'
        self.pagination_cd = pagination_cd
        self.count = 0

    @staticmethod
    def get_html(url, params=None):
        session = requests.Session()
        headers = requests.utils.default_headers()
        headers.update(
            {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
            }
        )
        datas = {
            'email': 'zakupki@masterservice.ms',
            'password': 'master_service'

        }
        session.post('https://atg-ua.com.ua/login/', data=datas, headers=headers, params=None,
                     allow_redirects=True)
        session.post('https://atg-ua.com.ua/edit-account/', data=datas, headers=headers, params=None,
                     allow_redirects=True)
        session.post('https://atg-ua.com.ua/login/', data=datas, headers=headers, params=None,
                     allow_redirects=True)
        session.post('https://atg-ua.com.ua/edit-account/', data=datas, headers=headers, params=None,
                     allow_redirects=True)
        r = session.get(url, headers=headers, params=params)

        return r

    @staticmethod
    def save_file(items, path):
        with open(path, 'w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(
                ['id', 'article_cards', 'Article', 'Description', 'Availability', 'Manufacturer', 'link', 'uah_price',
                 'img'])
            for item in items:
                writer.writerow([
                    item['id'],
                    item['article_cards'],
                    item['title'],
                    item['Description'],
                    item['Availability'],
                    item['Manufacturer'],
                    item['link'],
                    item['uah_price'],
                    # item['img']
                ])


class AtgParsAgregats(SamplePars):
    def __init__(self, url, name, pagination_cd):
        super().__init__(url, name, pagination_cd)

    def parser1(self):
        attribute_pars = []
        AtgParsAgregats.parser2(self)
        for url1 in self.get_data('articles_urls.txt'):
            html_links_save = None
            while html_links_save is None:
                try:
                    print(url1)
                    html_links_save = self.get_html(url1, params=None).text
                    attribute_pars.extend(self.get_content(html_links_save))
                    # time.sleep(2)
                    break
                except requests.exceptions.ConnectionError:
                    continue
        self.save_file(attribute_pars, self.CSV)

    def parser2(self):
        atr = []
        if self.get_html(self.url).status_code == 200:
            for page in range(1, self.pagination_cd + 1):
                print(f'Scraping page {page}')
                html_save = self.get_html(self.url, params={'page': page})
                atr.extend(self.collection_of_links(html_save.text))
                self.save_links(atr)
        else:
            print('Error')

    @staticmethod
    def get_data(file_links):
        with open(file_links) as file:
            urls_list = [line.strip() for line in file.readlines()]

        return urls_list

    @staticmethod
    def collection_of_links(html):
        items = BeautifulSoup(html, 'html.parser').find_all('div', class_='boxCategory_li')
        atr = []

        for item in items:
            link = item.find('a', class_='sliderProduct_thumb img-position').get('href')
            atr.append(link)
        return atr

    @staticmethod
    def save_links(items):
        with open('articles_urls.txt', 'w') as file:
            for url in items:
                file.write(f'{url}\n')

    @staticmethod
    def get_content(html):
        soup = BeautifulSoup(html, 'lxml')
        attribute = []
        items = soup.find_all('div', class_='listAnalogues_li flex j-c_between')
        for item in items:
            id = str(item.find('button', {'onclick': True}).get('onclick')[len("open_cart_modal('"):-len("', 0);")]) \
                if item.find('button', {'onclick': True}) else "No"

            availability = 'No' if item.find('button', class_='listAnalogues_button disabled_button') else 'Yes'

            uah_price = item.find('p', class_='listAnalogues_new-price').next_element.get_text(strip=True).replace \
                ('.', ',') if item.find('p', class_='listAnalogues_new-price') else 0

            manufacturer = str(item.find('ul', class_='listAnalogues_list').find('span').next_sibling.get_text(
                strip=True)) if item.find('ul', class_='listAnalogues_list').find('span') else item.find(
                'ul', class_='listAnalogues_list').findNext().findNext().get_text(strip=True)

            description = (item.find('div', class_='listAnalogues_center').find('a').get_text(strip=True)) if \
                item.find('div', class_='listAnalogues_center').find('a') else \
                item.find('div', class_='listAnalogues_center').find('h3').get_text(strip=True)

            link = soup.find('link', rel='canonical').get('href') if soup.find('link', rel='canonical') else 'No'

            article_cards = soup.find('div', class_='card-article').get_text(strip=True)

            attribute.append({
                'id': id,
                'article_cards': article_cards,
                'title': item.find('p', class_='listAnalogues_article').get_text(strip=True),
                'Description': description,
                'Availability': availability,
                'Manufacturer': manufacturer,
                'uah_price': uah_price,
                'link': link,
            })
        return attribute


class GurService(SamplePars):
    def __init__(self, url, name, pagination_cd):
        super().__init__(url, name, pagination_cd)

    def parser1(self):
        attribute_pars = []
        if self.get_html(self.url).status_code == 200:
            for page in range(1, self.pagination_cd + 1):
                print(f'Scraping page {page}')
                url = self.url + "?page=" + str(page)
                html_save = self.get_html(url)
                attribute_pars.extend(self.get_content(html_save.text))
            self.save_file(attribute_pars, self.CSV)
        else:
            print('Error')

    @staticmethod
    def get_html(url, params=None, TLSAdapter=TLSAdapter):
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/111.0.0.0 Safari/537.36",
            "accept": "*/*"}
        session = requests.session()
        session.mount('https://', TLSAdapter())
        r = session.get(url, headers=headers)

        return r

    @staticmethod
    def get_content(html):
        items = BeautifulSoup(html, 'html.parser').find('div', class_='products-list-box').find_all('div',
                                                                                                    class_='item')
        attribute = []
        for item in items:
            availability = 'No' if (
                item.find('div', class_='status table-cell').find('span', class_='stock-red')) else 'Yes'

            title = item.find('span', class_='car-model').findNext().get_text(strip=True) if item.find \
                ('span', class_='car-model') else item.find('a', class_='product-name').find('b').get_text(strip=True)

            attribute.append({
                'id': str(item.find('a', {'onclick': True}).get('onclick')),
                'title': title,
                'Availability': availability,
                'uah_price': item.find('div', class_='current-price').get_text(strip=True),
                'link': item.find('a', class_='').get('href'),
            })
        return attribute

    @staticmethod
    def save_file(items, path):
        with open(path, 'w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Article', 'Availability', 'uah_price', 'link'])
            for item in items:
                writer.writerow([item['title'], item['Availability'], item['uah_price'], item['link']])


class KievApp(SamplePars):
    def __init__(self, url, name, pagination_cd):
        super().__init__(url, name, pagination_cd)

    def parser(self):
        attribute_pars = []
        if self.get_html(self.url).status_code == 200:
            for page in range(1, self.pagination_cd + 1):
                print(f'Scraping page {page}')
                url = self.url + "?PAGEN_1=" + str(page)
                print(url)
                html_save = self.get_html(url)
                attribute_pars.extend(self.get_content(html_save.text))
            self.save_file(attribute_pars, self.CSV)
        else:
            print('Error')

    @staticmethod
    def get_html(url, params=None):
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/108.0.0.0 Safari/537.36",
            "accept": "*/*"}
        r = requests.get(url, headers=headers)

        return r

    @staticmethod
    def get_content(html):
        global size_data
        items = BeautifulSoup(html, 'html.parser').find('div', class_='col-lg-9').find_all('li',
                                                                                           class_='list-group-item')
        attribute = []
        for item in items:
            availability = item.find('div', style='color: green').get_text(strip=True) if (
                item.find('div', style='color: green')) else 'no'

            if item.find('i', class_='fas fa-industry'):
                if not item.find('i', class_='fas fa-industry').findParent().findParent():
                    if not item.find('i', class_='fas fa-industry').findParent():
                        manufacturer = 'no'
                    else:
                        manufacturer = item.find('i', class_='fas fa-industry').findParent().get_text(
                            strip=True)
                else:
                    manufacturer = item.find('i', class_='fas fa-industry').findParent().findParent().get_text(
                        strip=True)
            else:
                manufacturer = 'no'

            if item.find('div', style="color: black"):
                if item.find('div', style="color: black").find('i', class_='fa-industry'):
                    size_data = 'no'
                else:
                    size_data = item.find('div', style="color: black").findNext().next_element.next_element.get_text(
                        strip=True)
            else:
                size_data = 'no'

            attribute.append({
                'title': item.find('h5', style='font-weight: bold;').find('a').get_text(strip=True),
                'Availability': availability,
                'Size': size_data,
                'Manufacturer': manufacturer,
                'uah_price': item.find('strong', class_='').get_text(strip=True).replace(' ', ''),
                'link': item.find('h5', style='font-weight: bold;').find('a', class_='').get('href'),
            })
        return attribute

    @staticmethod
    def save_file(items, path):
        with open(path, 'w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(['Article', 'Availability', 'Size', 'Manufacturer', 'uah_price', 'link'])
            for item in items:
                writer.writerow(
                    [item['title'], item['Availability'], item['Size'], item['Manufacturer'], item['uah_price'],
                     item['link']])


class AgrParce(SamplePars):
    def __init__(self, url, name, pagination_cd):
        super().__init__(url, name, pagination_cd)

    def parser1(self):
        attribute_pars = []
        if self.get_html(self.url).status_code == 200:
            for page in range(1, self.pagination_cd + 1):
                print(f'Scraping page {page}')
                url = self.url + "?page=" + str(page)
                html_save = self.get_html(url)
                attribute_pars.extend(self.get_content(html_save.text))
            self.save_file(attribute_pars, self.CSV)
        else:
            print('Error')

    @staticmethod
    def get_html(url, params=None):
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/108.0.0.0 Safari/537.36",
            "accept": "*/*"}
        r = requests.get(url, headers=headers)
        return r

    @staticmethod
    def get_content(html):
        items = BeautifulSoup(html, 'html.parser').find('div', class_='row row-products product-category').find_all(
            'div', class_='product-thumb product-category__thumb q-pr-th')
        attribute = []
        for item in items:

            availability = 'No' if (
                item.find('button', class_='product-category__cart btn btn-primary btn-primary2')) else 'Yes'

            title = str(item.find('p', {'class': True}).find('strong').text) if item.find('p',
                                                                                          {'class': True}) else "No"

            # id = str(item.find('button', {'data-original-title': True}).get('onclick')[
            #          len("wishlist.add('"):-len("', '1');")]) if item.find('button', {'onclick': True}) else "No"

            attribute.append({
                # 'id': id,
                'title': title,
                'Availability': availability,
                'uah_price': item.find('p', class_='price product-category__price').get_text(strip=True)[:-len(" Грн")],
                'link': item.find('a', class_='').get('href'),
            })
        return attribute

    @staticmethod
    def save_file(items, path):
        with open(path, 'w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Article', 'Availability', 'uah_price', 'link'])
            for item in items:
                writer.writerow([item['title'], item['Availability'], item['uah_price'], item['link']])


def list_other_gur():
    object1 = AtgParsAgregats('https://atg-ua.com.ua/nasosi/gidropidsilyuvach-kerma/', "GUR_pumps", 6)
    object1.parser1()

    object3 = AtgParsAgregats('https://atg-ua.com.ua/rulevye-reyki/c53-gidravlichni/', "StGUR", 48)
    object3.parser1()

    object4 = AtgParsAgregats('https://atg-ua.com.ua/rulevye-reyki/c55-mehanichni/', "StMEH", 11)
    object4.parser1()


def list_other_eps():
    object1 = AtgParsAgregats('https://atg-ua.com.ua/nasosi/elektrogidropidsilyuvach-kerma/', "EPS_pumps", 5)
    object1.parser1()

    object2 = AtgParsAgregats('https://atg-ua.com.ua/rulevye-reyki/c54-elektrichni/', "StEPS", 13)
    object2.parser1()

    # object3 = AtgParsAgregats('https://atg-ua.com.ua/elektropidsilyuvachi', "ELB_EPS", 3)
    # object3.parser1()


def list_other_Seals():
    object4 = AtgParsAgregats('https://atg-ua.com.ua/komplektuyushchie/c44-salniki', "Seals", 71)
    object4.parser1()


def list_other_emmetec():
    # object1 = AtgParsAgregats('https://atg-ua.com.ua/komplektuyushchie/c16-bachki-ta-krishki', "БАЧКИ_И_КРЫШКИ", 2)
    # object1.parser1()
    #
    object2 = AtgParsAgregats('https://atg-ua.com.ua/komplektuyushchie/c33-vali', "ВАЛЫ", 12)
    object2.parser1()
    #
    # object3 = AtgParsAgregats('https://atg-ua.com.ua/komplektuyushchie/c15-datchiki-sensori-servotroniki',
    #                           "ДАТЧИКИ, СЕНСОРЫ, СЕРВО", 3)
    # object3.parser1()
    #
    # object4 = AtgParsAgregats('https://atg-ua.com.ua/komplektuyushchie/zaglushki', "ЗАГЛУШКИ", 1)
    # object4.parser1()
    #
    # object5 = AtgParsAgregats('https://atg-ua.com.ua/index.php?route=product/category&path=438_495', "ЗАЩИТНЫЕ КРЫШКИ",
    #                           2)
    # object5.parser1()
    #
    # object6 = AtgParsAgregats('https://atg-ua.com.ua/komplektuyushchie/kolpachki', "КОЛПАЧКИ, ЗАЩИТНЫЕ МАНЖЕТЫ", 1)
    # object6.parser1()
    #
    # object7 = AtgParsAgregats('https://atg-ua.com.ua/komplektuyushchie/kolca-rezino-metal', "КОЛЬЦА РЕЗИНО-МЕТАЛ", 1)
    # object7.parser1()
    #
    # object8 = AtgParsAgregats('https://atg-ua.com.ua/index.php?route=product/category&path=438_497',
    #                           "КОНТАКТНАЯ ГРУППА, РАЗЬЕМЫ", 3)
    # object8.parser1()
    #
    # object9 = AtgParsAgregats('https://atg-ua.com.ua/index.php?route=product/category&path=438_496', "КОРПУСА", 3)
    # object9.parser1()
    #
    # object10 = AtgParsAgregats('https://atg-ua.com.ua/komplektuyushchie/krestoviny', "КРЕСТОВИНЫ", 1)
    # object10.parser1()
    #
    # object11 = AtgParsAgregats('https://atg-ua.com.ua/index.php?route=product/category&path=438_498',
    #                            "МОТОРЫ, РЕДУКТОРА", 3)
    # object11.parser1()
    #
    # object12 = AtgParsAgregats('https://atg-ua.com.ua/komplektuyushchie/podshipniki', "ПОДШИПНИКИ", 2)
    # object12.parser1()
    #
    # object13 = AtgParsAgregats('https://atg-ua.com.ua/komplektuyushchie/porshni', "ПОРШНИ", 1)
    # object13.parser1()
    #
    # object14 = AtgParsAgregats('https://atg-ua.com.ua/index.php?route=product/category&path=438_494', "ПРОВОДА", 1)
    # object14.parser1()
    #
    # object15 = AtgParsAgregats('https://atg-ua.com.ua/komplektuyushchie/pylniki-tyag', "ПЫЛЬНИКИ ТЯГ", 2)
    # object15.parser1()
    #
    # object16 = AtgParsAgregats('https://atg-ua.com.ua/komplektuyushchie/raznoe', "РАЗНОЕ", 1)
    # object16.parser1()
    #
    # object17 = AtgParsAgregats('https://atg-ua.com.ua/komplektuyushchie/raspredelitel', "РАСПРЕДЕЛИТЕЛЬ", 1)
    # object17.parser1()
    #
    # object18 = AtgParsAgregats('https://atg-ua.com.ua/komplektuyushchie/regulirovochnye-vtulki',
    #                            "РЕГУЛИРОВОЧНЫЕ ВТУЛКИ", 2)
    # object18.parser1()
    #
    # object19 = AtgParsAgregats('https://atg-ua.com.ua/komplektuyushchie/rezinovye-o-ring', "РЕЗИНОВЫЕ O-RING", 8)
    # object19.parser1()
    #
    # object20 = AtgParsAgregats('https://atg-ua.com.ua/index.php?route=product/category&path=438_493', "РЕМНИ", 1)
    # object20.parser1()
    #
    # object21 = AtgParsAgregats('https://atg-ua.com.ua/komplektuyushchie/saylentbloki', "САЙЛЕНТБЛОКИ", 1)
    # object21.parser1()
    #
    # object22 = AtgParsAgregats('https://atg-ua.com.ua/komplektuyushchie/teflonovye-kolca', "ТЕФЛОНОВЫЕ КОЛЬЦА", 4)
    # object22.parser1()
    #
    # object23 = AtgParsAgregats('https://atg-ua.com.ua/index.php?route=product/category&path=438_492', "ТОРСИОНЫ", 2)
    # object23.parser1()
    #
    # object24 = AtgParsAgregats('https://atg-ua.com.ua/komplektuyushchie/trubki', "ТРУБКИ", 2)
    # object24.parser1()
    #
    # object25 = AtgParsAgregats('https://atg-ua.com.ua/komplektuyushchie/tyagi', "ТЯГИ", 1)
    # object25.parser1()
    #
    # object26 = AtgParsAgregats('https://atg-ua.com.ua/komplektuyushchie/uplotniteli-rezino-metall',
    #                            "УПЛОТНИТЕЛИ РЕЗИНО-МЕТАЛЛ", 2)
    # object26.parser1()
    #
    # object27 = AtgParsAgregats('https://atg-ua.com.ua/komplektuyushchie/fole-vstavka', "ФОЛЬЕ ВСТАВКА", 2)
    # object27.parser1()
    #
    # object28 = AtgParsAgregats('https://atg-ua.com.ua/komplektuyushchie/homuty', "ХОМУТЫ", 1)
    # object28.parser1()
    #
    # object29 = AtgParsAgregats('https://atg-ua.com.ua/komplektuyushchie/shayby', "ШАЙБЫ", 1)
    # object29.parser1()
    #
    # object30 = AtgParsAgregats('https://atg-ua.com.ua/komplektuyushchie/c20-remkomplekti', "РЕМКОМПЛЕКТИ", 10)
    # object30.parser1()

    # object31 = AtgParsAgregats('https://atg-ua.com.ua/komplektuyushchie/elektro-zapchasti', "КОМПЛЕКТУЮЧІ", 288)
    # object31.parser1()


def list_other_nasosy_reyki():
    object6 = GurService('https://nasosy-reyki.com.ua/tovary/',
                         "GURS_other", 322)
    object6.parser1()

    object6 = GurService('https://nasosy-reyki.com.ua/ru/tovary/rulevaya-reika/',
                         "GURS_reyki", 216)
    object6.parser1()

    object6 = GurService('https://nasosy-reyki.com.ua/ru/tovary/nasosy/',
                         "GURS_nasosy", 101)
    object6.parser1()


def list_other_KievApp():
    object1 = KievApp('https://app.kiev.ua/catalog/podshipniki/', "Аpp_kiev_podshipniki", 1780)
    object1.parser()

    object2 = KievApp('https://app.kiev.ua/catalog/salniki/',
                      "Аpp_kiev_salniki", 1115)
    object2.parser()

    object3 = KievApp('https://app.kiev.ua/catalog/vtulki/',
                      "Аpp_kiev_vtulki", 23)
    object3.parser()

    object4 = KievApp('https://app.kiev.ua/catalog/koltsa_uplotnitelnye/',
                      "Аpp_kiev_koltsa_uplotnitelnye", 39)
    object4.parser()

    object5 = KievApp('https://app.kiev.ua/catalog/manzhety/',
                      "Аpp_kiev_manzhety", 3)
    object5.parser()

    object6 = KievApp('https://app.kiev.ua/catalog/shariki/',
                      "Аpp_kiev_shariki", 3)
    object6.parser()


def list_other_AgrParce_EPS():
    # object1 = AgrParce('https://autoagregat.com.ua/rulovi-reiki-z-elektropidsilyuvachem-4', "AgrParce_REPS", 52)
    # object1.parser1()
    #
    # object2 = AgrParce('https://autoagregat.com.ua/nasosi-gidropidsilyuvacha-z-elektroprivodom-5', "AgrParce_PEPS", 20)
    # object2.parser1()

    object3 = AgrParce('https://autoagregat.com.ua/shtoki-rulovih-reiok-6', "AgrParce_Shtoki", 9)
    object3.parser1()


def command_papser_subcategories_ATG():
    count = int(input())
    if count == 1:
        list_other_emmetec()
    elif count == 2:
        list_other_gur()
    elif count == 3:
        list_other_eps()
    elif count == 4:
        list_other_Seals()
    elif count == 5:
        list_other_nasosy_reyki()
    elif count == 6:
        list_other_KievApp()
    elif count == 7:
        list_other_AgrParce_EPS()
    else:
        print("Not found")


command_papser_subcategories_ATG()
