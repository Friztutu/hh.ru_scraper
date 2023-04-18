import requests
from bs4 import BeautifulSoup
import lxml
from time import sleep


HEADERS = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
}


def get_request(url):
    response = requests.get(url, headers=HEADERS)
    if response.status_code >= 300:
        raise ValueError('Не удалось загрузить страницу')
    return BeautifulSoup(response.text, 'lxml')


def card_urls(soup):
    for link in soup.find_all('a', class_='serp-item__title'):
        yield link.get('href')


def card_information(url):
    soup = get_request(url)
    vacancy_url = url

    try:
        vacancy_name = soup.find("h1", class_="bloko-header-section-1").text
        salary = soup.find("span", class_='bloko-header-section-2 bloko-header-section-2_lite').text
        expecience = soup.find_all("p", class_="vacancy-description-list-item")[0].text
        time_for_job = soup.find_all("p", class_="vacancy-description-list-item")[1].text
        town = soup.find("p", class_="vacancy-creation-time-redesigned").text.split()[-1]
        data = ' '.join(soup.find("p", class_="vacancy-creation-time-redesigned").text.split()[0:4])
    except (AttributeError, IndexError):
        return f'Не удалось получить информацию о вакансии: {vacancy_url}'

    return vacancy_url, vacancy_name, salary, expecience, time_for_job, town, data


def get_information(vacancy_url, vacancy_name, salary, expecience, time_for_job, town, data):
    result = f'Сслыка на вакансию: {vacancy_url}\n' \
             f'Название вакансии: {vacancy_name}\n' \
             f'Зарплата: {salary}\n' \
             f'Требуемый опыт работы: {expecience}\n' \
             f'Занятость: {time_for_job}\n' \
             f'Город: {town}\n' \
             f'Дата: {data}\n'
    return result


def parse_paige(page, job):
    URL = f'https://hh.ru/search/vacancy?text={job}&page={page}'
    soup = get_request(URL)
    for link in card_urls(soup):
        vacancy_information = card_information(link)

        if isinstance(vacancy_information, str):
            print(vacancy_information + '\n')
            continue

        print(get_information(*vacancy_information))


search_job = input("Enter the job title you want to search for: ")

for page in range(40):
    parse_paige(page, search_job)
    sleep(1)
