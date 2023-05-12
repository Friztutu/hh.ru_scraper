import numpy as np
import pandas as pd
import dask.dataframe as dd
import matplotlib.pyplot as plt


def main():
    filename = 'vacancies.csv'

    # Сброс ограничений на количество выводимых рядов
    pd.set_option('display.max_rows', None)

    # Сброс ограничений на число столбцов
    pd.set_option('display.max_columns', None)

    # Сброс ограничений на количество символов в записи
    pd.set_option('display.max_colwidth', None)

    df = dd.read_csv(filename, dtype={'salary': 'float64'})

    df = df.loc[df['salary']!=0]

    avg_salary = df['salary'].mean().compute()
    salary_by_town = df.groupby('town')['salary'].mean().compute()
    salary_by_town.plot(kind='hist')
    plt.show()

    print(f'Средняя зарплата из всех вакансий: {int(avg_salary)}')
    print(salary_by_town)


if __name__ == '__main__':
    main()
