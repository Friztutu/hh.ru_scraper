import scrapy
import re
import unidecode


class CardUrlSpider(scrapy.Spider):
    search_job = input("Какую работу ищем: ").strip()
    PAGE_ON_SITE = int(input("Сколько страниц будем парсить: "))
    name = 'hh'
    download_delay = 1
    start_urls = [f'https://pskov.hh.ru/search/vacancy?area=113&text={search_job}&items_on_page=20']

    def parse(self, response, **kwargs):
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
        data = {
            'link': response.url,
            'title': response.css('h1.bloko-header-section-1::text').get(),
            'experience': self.__convert_experience(experience_string=
                response.css('p.vacancy-description-list-item').css('span::text').get()),
            'salary': self.__convert_salary(salary_html_code=
                response.css('div.wrapper-flat--H4DVL_qLjKLCo1sytcNI').css('div.vacancy-title').css(
                    'span.bloko-header-section-2').get()),
            'employment': self.__convert_employment(response.css('p.vacancy-description-list-item').getall()),
            'town': self.__convert_town(town=response.css('div.vacancy-company-redesigned').css('p::text').get()),
            'company': self.__convert_company(response.css('div.vacancy-company-redesigned').css('a.bloko-link').css('span.bloko-header-section-2').css('span').get()),
        }
        if not data['town']:
            data['town'] = self.__convert_town(town=response.css('div.vacancy-company-redesigned').css('a.bloko-link_disable-visited').css(
                'span::text').get())
        yield data

    @staticmethod
    def __convert_salary(salary_html_code: str):

        if salary_html_code is None or 'з/п не указана' in salary_html_code:
            return -1

        salary = re.findall(r"[\d]{1,}\s[\d]{1,}", salary_html_code)

        if len(salary) == 2:
            first_num, second_num = map(unidecode.unidecode, salary)
            first_num, second_num = int(first_num.replace(' ', '')), int(second_num.replace(' ', ''))
            salary = (first_num + second_num) // 2
        else:
            first_num = unidecode.unidecode(salary[0])
            first_num = int(first_num.replace(' ', ''))
            salary = first_num

        return salary

    @staticmethod
    def __convert_experience(experience_string: str):
        if experience_string is None or 'не требуется' in experience_string:
            return 0

        nums = re.findall('[\d]+', experience_string)
        if len(nums) == 1:
            return nums[0]

        else:
            return (int(nums[0]) + int(nums[1])) // 2

    @staticmethod
    def __convert_town(town):
        if town is None:
            return None
        town = town.split(',')
        if '(' not in town[0]:
            return town[0].replace('г. ', '')
        else:
            town = town[0].split('(')
            return town[0].replace('г. ', '')

    @staticmethod
    def __convert_employment(employment_html_code):
        if len(employment_html_code) < 2:
            return

        employment_html_code = employment_html_code[1]
        result = re.findall('>[\w\s]{1,}', employment_html_code)
        first_word, second_word = result[0].replace('>', ''), result[1].replace('>', '')
        return f'{first_word}, {second_word}'

    @staticmethod
    def __convert_company(company_html_code):
        if company_html_code is None:
            return '-1(Не указано)'

        if not re.findall('span', company_html_code):
            return company_html_code

        if not re.findall('-->', company_html_code):
            result = re.findall('>.{0,}<', company_html_code)
            result = result[0].replace('>', '').replace('<', '')
            return result

        result = re.findall('-->.{0,}</span>', company_html_code)
        result = result[0].replace('-->', '').replace('</span>', '')
        return result
