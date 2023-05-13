import pandas as pd
import dask.dataframe as dd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os


def create_file(filename):
    if not os.path.exists('analyze'):
        os.mkdir('analyze')

    with open('analyze/analyze.txt', mode='w') as file:
        file.write('Заголовок'.center(200, '-'))
        file.write('\n\n\n')
        file.write(f'Отчет по запросу: {filename}, Время оформления: {datetime.today()}\n\n\n')


def create_dataframe(filename):
    filename = filename + '.csv'
    df = dd.read_csv(f'csv_data/{filename}', dtype={'salary': 'float64'})
    return df


def analyze_vacancy_town(df):
    result = df.groupby('town')['salary'].count().compute()

    with open('analyze/analyze.txt', mode='a') as file:
        file.write('Вакансии'.center(200, '-') + '\n\n\n')
        file.write(f'Всего вакансий: {len(df.index)}\n\n')
        file.write(f'Количество вакансий по регионам: \n\n')
        for line, town in zip(result, result.index):
            file.write(f'{town.center(20, " ")}: {float(line):.0f} вакансий\n')

        file.write('\n\n')


def analyze_salary(df):
    df_with_salary = df[(df.salary != -1)]

    avg_salary = df_with_salary['salary'].mean().compute()
    salary_by_town = df_with_salary.groupby('town')['salary'].mean().compute()
    salary_by_town.plot(kind='hist')
    plt.savefig('analyze/График_зарплат.png')
    with open('analyze/analyze.txt', mode='a') as file:
        file.write('Зарплата'.center(200, '-') + '\n\n\n')
        file.write(f'Средняя зарплата всех вакансий: {float(avg_salary):.3f}\n')
        file.write(f'Вакансии без зарплаты: {len(df.index) - len(df_with_salary.index)}\n\n')
        file.write(f'Средняя зарплата по городам: \n\n')
        for line, town in zip(salary_by_town, salary_by_town.index):
            file.write(f'{town.center(20, " ")}: {float(line):.3f} руб.\n')

        file.write('\n')


def analyze_experience(df):
    avg_experience = df['experience'].mean().compute()
    avg_experience_by_town = df.groupby('town')['experience'].mean().compute()

    with open('analyze/analyze.txt', mode='a') as file:
        file.write('\n' + 'Опыт'.center(200, '-') + '\n\n\n')
        file.write(f'Средняя требуемый опыт всех вакансий: {float(avg_experience):.3f} лет\n\n')
        file.write(f'Средняя требуемый опыт по городам:\n\n')
        for line, town in zip(avg_experience_by_town, avg_experience_by_town.index):
            file.write(f'{town.center(20, " ")}: {float(line):.3f} года\n')


def analyze_employment(df):
    result = df.groupby('employment')['employment'].count().compute()
    with open('analyze/analyze.txt', mode='a') as file:
        file.write('\n\n' + 'Занятость'.center(200, '-') + '\n\n\n')
        file.write(f'Статистика по вакансиям: \n\n')
        for line, town in zip(result, result.index):
            file.write(f'{town.center(50, " ")}: {line} вакансий\n')


def analyze_company(df):
    df_with_company = df[(df.company != '-1(Не указано)') & (df.salary != -1)]
    result = df_with_company.groupby('company')['salary'].mean().compute()

    with open('analyze/analyze.txt', mode='a') as file:
        file.write('Компании'.center(200, '-') + '\n\n\n')
        file.write(f'Всего компаний: {len(result)}\n\n')
        file.write(f'Средняя з\п по компаниям: \n\n')
        for line, town in zip(result, result.index):
            file.write(f'{town.center(50, " ")}: {float(line):.3f} руб.\n')

        file.write('\n\n')

    result = df_with_company.groupby('company')['salary'].count().compute()

    with open('analyze/analyze.txt', mode='a') as file:
        file.write(f'Количество вакансий по компаниям: \n\n')
        for line, town in zip(result, result.index):
            file.write(f'{town.center(50, " ")}: {float(line):.0f} вакансий\n')

        file.write('\n\n')


def main(filename: str):
    create_file(filename)
    df = create_dataframe(filename)
    analyze_vacancy_town(df)
    analyze_salary(df)
    analyze_experience(df)
    analyze_employment(df)
    analyze_company(df)


if __name__ == '__main__':
    main('кассир')
