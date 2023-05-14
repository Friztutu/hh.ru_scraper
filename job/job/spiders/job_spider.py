import scrapy
import re
import unidecode
from typing import Optional, Dict, Union


class Converter:
    """Класс для конвертации собранных пауком(скрапером) значений в приемлимый вид"""

    @classmethod
    def convert_salary(cls, salary: Optional[str]) -> int:
        """
        Достает из переданного куска html кода информацию о зарплате.
        Если указано одно значение, то оно и записывается.
        Если указано два значения(зарплатная вилка), то вычисляется среднее значение.
        Из-за страниц вакансий с кастомным дизайном, возможны ошибки
        Если зп не указана, или передаваемый код равен None, возвращается -1(код отсуствия информации)
        """
        if salary is None or 'з/п не указана' in salary:
            return -1

        salary: list[Optional[str]] = list(map(unidecode.unidecode, re.findall(r"[\d]{1,}\s[\d]{1,}", salary)))

        if len(salary) == 2:
            first_num, second_num = salary
            salary: int = (int(first_num.replace(' ', '')) + int(second_num.replace(' ', ''))) // 2
        else:
            first_num = salary[0]
            salary: int = int(first_num.replace(' ', ''))

        return salary

    @classmethod
    def convert_experience(cls, experience: str) -> int:
        """
        Достает из переданного куска html кода информацию о требуемом опыте.
        Если указано одно значение, то оно и записывается.
        Если указано два значения(вилка требуемого опыта), то вычисляется среднее значение.
        Из-за страниц вакансий с кастомным дизайном, возможны ошибки
        Если опыт не требуется возращается 0
        Если передаваемый код равен None, возращается -1(код отсуствия информации)
        """
        if experience is None:
            return -1

        if 'не требуется' in experience:
            return 0

        nums: list[int] = list(map(int, re.findall('\d+', experience)))

        return nums[0] if len(nums) == 1 else sum(nums) // 2

    @classmethod
    def convert_town(cls, town: str) -> Union[int, str]:
        """
        Достает из переданного куска html кода информацию о городе.
        Из-за страниц вакансий с кастомным дизайном, возможны ошибки
        Если передаваемый код равен None, возращается -1(код отсуствия информации)
        Этот метод вызывается если в месте с городом, указана лишняя информация, или есть сокращение 'г.'
        Отделяет название города от остального и записывает
        """
        if town is None:
            return -1
        town: list[str] = town.split(',')

        if '(' in town[0]:
            town: list[str] = town[0].split('(')

        return town[0].replace('г.', '').replace(' ', '')

    @classmethod
    def convert_employment(cls, employment: list[str]) -> Optional[str]:
        """
        Достает из переданного куска html кода информацию о городе.
        Из-за страниц вакансий с кастомным дизайном, возможны ошибки
        Если передаваемый код равен None, возращается -1(код отсуствия информации)
        Первый элемент это код с информации о требуемом опыте, второй о занятости
        Отделяет информацию о занятости от кода и возвращает его
        """
        if len(employment) < 2:
            return

        employment: str = employment[1]
        result: list[str] = re.findall('>[\w\s]+', employment)
        first_word, second_word = result[0].replace('>', ''), result[1].replace('>', '')
        return f'{first_word}, {second_word}'

    @classmethod
    def convert_company(cls, company: str) -> Union[int, str]:
        """
        Достает из переданного куска html кода информацию о городе.
        Из-за страниц вакансий с кастомным дизайном, возможны ошибки
        Если передаваемый код равен None, возращается -1(код отсуствия информации)
        Отделяет название компании от кода и возвращает его
        """
        if company is None:
            return -1

        if not re.findall('span', company):
            return company

        if not re.findall('-->', company):
            result: list[str] = re.findall('>.{0,}<', company)
            result: str = result[0].replace('>', '').replace('<', '')
            return result

        result: list[str] = re.findall('-->.{0,}</span>', company)
        result: str = result[0].replace('-->', '').replace('</span>', '')
        return result


class HeadHunterScraper(scrapy.Spider):
    """
    Паук для скрапинга информации с hh.ru

    search_job - запрос по которому будет проводится скрапинг
    PAGE_ON_SITE - количество страниц по которому будет проводится парсинг
    name - имя паука, используется для твоего вызова
    start_urls - url главной страницы
    converter - конвертер который будет применяться к собранной информации
    """
    search_job: str = input("Какую работу ищем: ").strip()
    PAGE_ON_SITE: int = int(input("Сколько страниц будем парсить: "))
    name: str = 'hh'
    download_delay: int = 1
    start_urls: list[str] = [f'https://pskov.hh.ru/search/vacancy?area=113&text={search_job}&items_on_page=20']
    converter = Converter

    def parse(self, response, **kwargs):
        """
        Первый цикл собирает ссылки на вакансии
        Второй цикл отвечает за переход нв следующую страницу со списком вакансий
        """
        for link in response.css('h3.bloko-header-section-3 a::attr(href)'):
            yield response.follow(
                f'{link.get()}',
                callback=self.parse_vacancy_card
            )

        for page in range(self.PAGE_ON_SITE):
            yield response.follow(
                f'https://pskov.hh.ru/search/vacancy?area=113&text={self.search_job}&items_on_page=20&page={page}',
                callback=self.parse
            )

    def parse_vacancy_card(self, response):
        """
        Собирает информацию со страницы вакансии и передает ее в конвертер
        После того как информация возвращается от конвертера, она записывается в csv файл
        """
        data: Dict[str, (str, int)] = {
            'link': response.url,
            'title': response.css('h1.bloko-header-section-1::text').get(),
            'experience': self.converter.convert_experience(
                experience=response.css('p.vacancy-description-list-item').css('span::text').get()
            ),
            'salary': self.converter.convert_salary(
                salary=response.css('div.wrapper-flat--H4DVL_qLjKLCo1sytcNI').css('div.vacancy-title').css(
                    'span.bloko-header-section-2').get()
            ),
            'employment': self.converter.convert_employment(
                employment=response.css('p.vacancy-description-list-item').getall()
            ),
            'town': self.converter.convert_town(
                town=response.css('div.vacancy-company-redesigned').css('p::text').get()
            ),
            'company': self.converter.convert_company(
                company=response.css('div.vacancy-company-redesigned').css('a.bloko-link').css(
                    'span.bloko-header-section-2').css('span').get()
            ),
        }
        if data['town'] == -1:
            data['town'] = self.converter.convert_town(
                town=response.css('div.vacancy-company-redesigned').css('a.bloko-link_disable-visited').css(
                    'span::text').get()
            )
        yield data
