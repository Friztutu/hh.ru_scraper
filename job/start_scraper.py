import os
import data_analyze


class Starter:
    """Класс для старта паука(скрапера)"""

    @classmethod
    def start_spider(cls):
        """
        Берет название файла от пользователя(без .csv, расширение поставится само)
        Запускает скрапер
        После конца работа скрапера запускает анализ полученных данных
        """
        if not os.path.exists('csv_data'):
            os.mkdir('csv_data')

        filename: str = input("Имя файла: ").strip()
        os.system(f"scrapy crawl hh -O csv_data/{filename}.csv")

        data_analyze.main(filename)


if __name__ == '__main__':
    Starter.start_spider()
