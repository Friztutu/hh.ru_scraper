import numpy as np
import pandas as pd
import dask.dataframe as dd
import matplotlib.pyplot as plt


def create_file(job):
    with open('analyze.txt', mode='w') as file:
        file.write(f'Отчет по запросу {job}')


def create_dataframe(filename):
    filename = filename + '.csv'

    # Сброс ограничений на количество выводимых рядов
    pd.set_option('display.max_rows', None)

    # Сброс ограничений на число столбцов
    pd.set_option('display.max_columns', None)

    # Сброс ограничений на количество символов в записи
    pd.set_option('display.max_colwidth', None)

    df = dd.read_csv(filename, dtype={'salary': 'float64'})
    return df


def analyze_salary(df):
    df = df.loc[df['salary'] != -1]

    avg_salary = df['salary'].mean().compute()
    salary_by_town = df.groupby('town')['salary'].mean().compute()
    salary_by_town.plot(kind='hist')
    plt.savefig('График_зарплат.png')
    with open('analyze.txt', mode='a') as file:
        file.write(f'\n\n\nСредняя зарплата всех вакансий: {avg_salary}')
        file.write(f'\n\n\nСредняя зарплата по городам: \n')
        for line, town in zip(salary_by_town, salary_by_town.index):
            file.write(f'{town.center(20, " ")}: {float(line):.0f} руб.\n')


def main(job: str, filename: str):
    create_file(job)
    df = create_dataframe(filename)
    analyze_salary(df)


if __name__ == '__main__':
    main('уборщик', 'vacancies')
