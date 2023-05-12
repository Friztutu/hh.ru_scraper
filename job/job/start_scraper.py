import scrapy
import os
from data_analyze import main


def start_scraper():
    filename = input('Видите имя файла: ')
    os.system(f"scrapy crawl hh -O {filename}.csv")

    main(filename)


if __name__ == '__main__':
    start_scraper()
