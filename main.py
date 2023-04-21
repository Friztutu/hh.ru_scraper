import requests
from bs4 import BeautifulSoup
from time import sleep
import database
from peewee import IntegrityError
from progress.bar import IncrementalBar


class HeadHunterParser:
    HEADERS = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }

    def __init__(self, job='python junior', page=0):
        url = f'https://hh.ru/search/vacancy?text={job}' + f'&page={page}'
        response = requests.get(url, headers=self.HEADERS)

        if not response:
            raise ValueError('Не удалось загрузить страницу')

        self.main_soup = BeautifulSoup(response.text, 'lxml')

    def __card_soup_generator(self):
        for link_code in self.main_soup.find_all('a', class_='serp-item__title'):
            link = link_code.get('href')
            response = requests.get(link, headers=self.HEADERS)
            card_soup = BeautifulSoup(response.text, 'lxml')
            yield link, card_soup

    @staticmethod
    def __convert_salary(salary):
        if salary == 'з/п не указана':
            return None

        currencies = {'руб.': '₽', 'USD': '$', 'KZT': '₸'}
        salary = salary.split()
        result = []
        for letter in salary:
            if letter.isdigit():
                result += letter

            elif result:
                break

        result = ''.join(result)

        for currency in currencies:
            if currency in salary:
                result += currencies[currency]
                break

        return result

    @staticmethod
    def __convert_data(data):
        month = {
            'января': 1,
            'февраля': 2,
            'марта': 3,
            'апреля': 4,
            'мая': 5,
            'июня': 6,
            'июля': 7,
            'августа': 8,
            'сентября': 9,
            'октября': 10,
            'ноября': 11,
            'декабря': 12,
        }

        dt_str = f'2023 {month[data.split()[-1]]} {data.split()[-2]}'

        return dt_str

    @staticmethod
    def __convert_experience(experience):
        if experience == 'Требуемый опыт работы: не требуется':
            return 0

        for letter in experience:
            if not letter.isdigit():
                continue

            return letter

    def __iter__(self):
        for link, soup in self.__card_soup_generator():
            try:
                vacancy_link = link
                vacancy_name = soup.find("h1", class_="bloko-header-section-1").text
                salary = soup.find("span", class_='bloko-header-section-2 bloko-header-section-2_lite').text
                experience = soup.find_all("p", class_="vacancy-description-list-item")[0].text
                employment = soup.find_all("p", class_="vacancy-description-list-item")[1].text
                town = soup.find("p", class_="vacancy-creation-time-redesigned").text.split()[-1]
                data = ' '.join(soup.find("p", class_="vacancy-creation-time-redesigned").text.split()[0:4])

                salary = self.__convert_salary(salary)
                data = self.__convert_data(data)
                experience = self.__convert_experience(experience)

                yield vacancy_link, vacancy_name, salary, data, town, experience, employment

            except (AttributeError, IndexError) as error:
                print(error)
                print(f'Не удалось получить информацию о вакансии: {link}')


if __name__ == '__main__':
    search_job = input("Enter the job title you want to search for: ").strip()
    database.init_db(search_job)
    bar = IncrementalBar('Progress', max=40)

    for page in range(40):

        try:
            parser = HeadHunterParser(search_job, page=page)
        except ValueError as error:
            print(error)
            continue

        for info in parser:

            try:
                database.insert_into_table(*info)
                sleep(2)
            except IntegrityError as error:
                print(error)

        bar.next()

    database.close_db()
    bar.finish()
