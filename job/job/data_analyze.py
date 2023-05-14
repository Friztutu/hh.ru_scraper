import pandas as pd
import dask.dataframe as dd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os


class Analyzer:

    def __init__(self, filename):
        self.df = dd.read_csv(f'csv_data/{filename}.csv', dtype={'salary': 'float64'})
        self.writer = Writer(filename)

    def default_info(self):
        df_with_salary = self.df[self.df.salary != -1]
        df_with_experience = self.df[self.df.experience != -1]

        avg_salary = df_with_salary['salary'].mean().compute()
        avg_experience = df_with_experience['experience'].mean().compute()

        self.writer.write_title('Общая информация')
        self.writer.write_default_info(len(self.df), avg_salary, avg_experience)

    def analyze_by_town(self):
        df = self.df[(self.df.salary != -1) & (self.df.experience != -1) & (self.df.town != 1)]

        title = 'Статистика по городам'
        table_title = 'Город'.ljust(40, ' ') + 'Вакансий'.ljust(40, ' ') + 'Cредняя з\п'.ljust(40,
                                                                                               ' ') + 'Средний требуемый опыт'.ljust(
            40, ' ')

        vacancy_by_town = df.groupby('town')['salary'].count().compute()
        salary_by_town = df.groupby('town')['salary'].mean().compute()
        avg_experience_by_town = df.groupby('town')['experience'].mean().compute()

        self.writer.write_title(title)
        self.writer.write_table(table_title, df_table=(vacancy_by_town, salary_by_town, avg_experience_by_town))

    def analyze_by_company(self):
        df = self.df[(self.df.salary != -1) & (self.df.experience != -1) & (self.df.company != 1)]

        title = 'Статистика по компаниям'
        table_title = 'Компания'.ljust(40, ' ') + 'Вакансий'.ljust(40, ' ') + 'Cредняя з\п'.ljust(40,
                                                                                                  ' ') + 'Средний требуемый опыт'.ljust(
            40, ' ')

        vacancy_by_company = df.groupby('company')['salary'].count().compute()
        salary_by_company = df.groupby('company')['salary'].mean().compute()
        avg_experience_by_company = df.groupby('company')['experience'].mean().compute()

        self.writer.write_title(title)
        self.writer.write_table(table_title,
                                df_table=(vacancy_by_company, salary_by_company, avg_experience_by_company))

    def start(self):
        self.default_info()
        self.analyze_by_town()
        self.analyze_by_company()


class Writer:

    def __init__(self, filename: str) -> None:
        self.filename = filename

        if not os.path.exists(f'analyze'):
            os.mkdir('analyze')

        with open(f'analyze/{self.filename}_analyze.txt', mode='w') as file:
            file.write('Заголовок'.center(200, '-'))
            file.write('\n\n\n')
            file.write(
                f'Отчет по запросу: {filename}, Время оформления: {datetime.today()}\n\n\n'
            )

    def write_title(self, title: str) -> None:
        with open(f'analyze/{self.filename}_analyze.txt', mode='a') as file:
            file.write(title.center(200, '-'))
            file.write('\n\n\n')

    def write_default_info(self, len_df, avg_salary, avg_experience):
        with open(f'analyze/{self.filename}_analyze.txt', mode='a') as file:
            file.write(f'Количество вакансий в таблице: {len_df}\n')
            file.write(f'Средняя зарплата по вакансиям: {avg_salary:.3f}\n')
            file.write(f'Средний опыт: {avg_experience:.3f}\n\n\n')

    def write_table(self, table_title, df_table, extra_info=tuple()):
        df1, df2, df3 = df_table
        with open(f'analyze/{self.filename}_analyze.txt', mode='a') as file:
            for line in extra_info:
                file.write(line + '\n')
            file.write(table_title + '\n\n')
            for index, line1, line2, line3 in zip(df1.index, df1, df2, df3):
                file.write(
                    f'{index.ljust(40, " ")}' + f'{float(line1):.1f}'.ljust(40, " ") + f'{float(line2):.3f}'.ljust(40,
                                                                                                                   " ") + f'{float(line3):.3f}'.ljust(
                        40, " ") + '\n')

            file.write('\n\n')


class Graphs:
    pass


def main(filename):
    a = Analyzer(filename)
    a.start()


if __name__ == '__main__':
    main('кассир')
