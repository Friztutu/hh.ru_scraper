import scrapy
import re
import unidecode
import os


class CardUrlSpider(scrapy.Spider):
    name = 'hh'
    search_job = input("Какую работу ищем: ").strip()
    start_urls = [f'https://pskov.hh.ru/search/vacancy?area=113&text={search_job}&items_on_page=20']
    download_delay = 1
    PAGE_ON_SITE = 20

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
            'experience': self.__convert_experience(
                response.css('p.vacancy-description-list-item').css('span::text').get()),
            'salary': self.__convert_salary(
                response.css('div.wrapper-flat--H4DVL_qLjKLCo1sytcNI').css('div.vacancy-title').css('span.bloko-header-section-2').get()),
            'employment': response.xpath("/html[@class='desktop']/body[@class=' s-friendly xs-friendly']"
                                         "/div[@id='HH-React-Root']/div/div[@class='HH-MainContent HH-Su"
                                         "pernova-MainContent']/div[@class='main-content']/div[@class='bl"
                                         "oko-columns-wrapper']/div[@class='row-content']/div[@class='blo"
                                         "ko-text bloko-text_large']/div[@class='bloko-columns-row']/div["
                                         "@class='bloko-column bloko-column_container bloko-column_xs-4 bl"
                                         "oko-column_s-8 bloko-column_m-12 bloko-column_l-10']/div[@class="
                                         "'bloko-columns-row'][1]/div[@class='bloko-column bloko-column_xs-"
                                         "4 bloko-column_s-8 bloko-column_m-12 bloko-column_l-10']/div[@class="
                                         "'wrapper-flat--H4DVL_qLjKLCo1sytcNI']/p[@class='vacancy-description"
                                         "-list-item'][2]").extract()[0].replace(
                '<p class="vacancy-description-list-item" data-qa="vacancy-view-employment-mode">', '').replace(
                '<!-- -->, <span>', ', ').replace('</span></p>', ''),
            'town': response.css('div.vacancy-company-redesigned').css('p::text').get(),
        }
        if not data['town']:
            data['town'] = response.css('div.vacancy-company-redesigned').css('a.bloko-link_disable-visited').css(
                'span::text').get()
        yield data

    @staticmethod
    def __convert_salary(salary_html_code: str):

        if 'з/п не указана' in salary_html_code:
            return 0

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
        if 'не требуется' in experience_string:
            return 0

        nums = re.findall('[\d]+', experience_string)
        if len(nums) == 1:
            return nums[0]

        else:
            return (int(nums[0]) + int(nums[1])) // 2
