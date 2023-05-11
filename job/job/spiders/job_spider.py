import scrapy


#search_job = input("Какую работу ищем: ")


class CardUrlSpider(scrapy.Spider):
    name = 'hh'
    start_urls = [f'https://pskov.hh.ru/search/vacancy?area=113&text=python&items_on_page=20']
    download_delay = 1
    counter = 0
    PAGE_ON_SITE = 100

    def parse(self, response, **kwargs):
        for link in response.css('h3.bloko-header-section-3 a::attr(href)'):
            yield response.follow(
                f'{link.get()}',
                callback=self.parse_vacancy_card
            )

        for page in range(self.PAGE_ON_SITE):
            yield response.follow(
                f'https://pskov.hh.ru/search/vacancy?area=113&text=python&items_on_page=20&page={page}',
                callback=self.parse
            )

    def parse_vacancy_card(self, response):
        yield {
            'link': response.url,
            'title': response.css('h1.bloko-header-section-1::text').get(),
            'experience':response.xpath("/html[@class='desktop']/body[@class=' s-friendly xs-friendly']/div["
                                        "@id='HH-React-Root']/div/div[@class='HH-MainContent "
                                        "HH-Supernova-MainContent']/div[@class='main-content']/div["
                                        "@class='bloko-columns-wrapper']/div[@class='row-content']/div["
                                        "@class='bloko-text bloko-text_large']/div[@class='bloko-columns-row']/div["
                                        "@class='bloko-column bloko-column_container bloko-column_xs-4 "
                                        "bloko-column_s-8 bloko-column_m-12 bloko-column_l-10']/div["
                                        "@class='bloko-columns-row'][1]/div[@class='bloko-column bloko-column_xs-4 "
                                        "bloko-column_s-8 bloko-column_m-12 bloko-column_l-10']/div["
                                        "@class='wrapper-flat--H4DVL_qLjKLCo1sytcNI']/p["
                                        "@class='vacancy-description-list-item'][1]").extract()[0].replace('<p class="vacancy-description-list-item">Требуемый опыт работы<!-- -->: <span data-qa="vacancy-experience">', '').replace('</span></p>', ''),
            'salary': self.covert_salary(response.xpath("/html[@class='desktop']/body[@class=' s-friendly xs-friendly']/div["
                                     "@id='HH-React-Root']/div/div[@class='HH-MainContent "
                                     "HH-Supernova-MainContent']/div[@class='main-content']/div["
                                     "@class='bloko-columns-wrapper']/div[@class='row-content']/div["
                                     "@class='bloko-text bloko-text_large']/div[@class='bloko-columns-row']/div["
                                     "@class='bloko-column bloko-column_container bloko-column_xs-4 bloko-column_s-8 "
                                     "bloko-column_m-12 bloko-column_l-10']/div[@class='bloko-columns-row'][1]/div["
                                     "@class='bloko-column bloko-column_xs-4 bloko-column_s-8 bloko-column_m-12 "
                                     "bloko-column_l-10']/div[@class='wrapper-flat--H4DVL_qLjKLCo1sytcNI']/div["
                                     "@class='vacancy-title']/div[2]/span[@class='bloko-header-section-2 "
                                     "bloko-header-section-2_lite']").extract()),
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
                                         "-list-item'][2]").extract()[0].replace('<p class="vacancy-description-list-item" data-qa="vacancy-view-employment-mode">', '').replace('<!-- -->, <span>', ', ').replace('</span></p>', ''),
            'town': response.css('div.vacancy-company-redesigned').css('p::text').get(),
        }

    def covert_salary(self, salary_html_code):
        salary_html_code = salary_html_code[0]

        if 'з/п не указана' in salary_html_code:
            return None

        salary_html_code = salary_html_code.replace('<span data-qa="vacancy-salary-compensation-type-net" '
                                                    'class="bloko-header-section-2 '
                                                    'bloko-header-section-2_lite">от <!-- -->', '').replace('<!-- '
                                                                                                            '-->',
                                                                                                            '').replace(
            '.<span class="vacancy-salary-compensation-type"> на руки</span></span>', '')
        a = salary_html_code.replace(r'"<span data-qa=\"vacancy-salary-compensation-type-gross\" '
                                     r'class=\"bloko-header-section-2 bloko-header-section-2_lite\">', '')
        a = a.replace(r'"<span data-qa=\"vacancy-salary-compensation-type-gross\" class=\"bloko-header-section-2'
                      r'bloko-header-section-2_lite\">', '').replace(r'<span '
                                                                     r'class=\"vacancy-salary-compensation-type\"> до вычета налогов</span></span>"',
                                                                     '')

        a = a.replace(r'<span class="vacancy-salary-compensation-type"> на руки</span></span>', '')
        a = a.replace(r'<span data-qa="vacancy-salary-compensation-type-gross" class="bloko-header-section-2 bloko-header-section-2_lite">от', '')
        a = a.replace(r'<span class="vacancy-salary-compensation-type"> до вычета налогов</span></span>', '')
        a = a.replace(r'<span data-qa="vacancy-salary-compensation-type-net" class="bloko-header-section-2 bloko-header-section-2_lite">до', '')
        a = a.replace(r'<span data-qa="vacancy-salary-compensation-type-gross" class="bloko-header-section-2 bloko-header-section-2_lite">до', '')
        return a
