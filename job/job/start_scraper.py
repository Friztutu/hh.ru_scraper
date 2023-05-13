import scrapy
import os
from job import data_analyze


class Starter:

    @classmethod
    def start_spider(cls):
        filename = input("Имя файла: ").strip()
        os.system(f"scrapy crawl hh -O csv_data/{filename}.csv")

        data_analyze.main(filename)


if __name__ == '__main__':
    Starter.start_spider()
