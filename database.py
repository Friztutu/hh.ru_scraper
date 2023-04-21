from peewee import *
import psycopg2

db = PostgresqlDatabase(
    'postgres',
    user='postgres',
    password='1234',
    port='5432'
)


class BaseModel(Model):
    class Meta:
        database = db


class Vacancy(BaseModel):
    vacancy_id = AutoField(column_name='vacancy_id', primary_key=True)
    vacancy_link = TextField(column_name='vacancy_link', unique=True)
    vacancy_name = TextField(column_name='vacancy_name')
    salary = CharField(column_name='salary', null=True)
    date = DateField(column_name='date')
    town = CharField(column_name='town', max_length=70)
    experience = SmallIntegerField(column_name='experience', null=True)
    employment = CharField(column_name='employment', max_length=50, null=True)

    class Meta:
        table_name = 'PythonVacancies'


def init_db(job_name):
    Vacancy._meta.table_name = job_name
    db.connect()
    db.create_tables([Vacancy])


def insert_into_table(link, name, salary, data, town, experience, employment):
    obj = Vacancy.create(
        vacancy_link=link,
        vacancy_name=name,
        salary=salary,
        date=psycopg2.Date(*map(int, data.split())),
        town=town,
        experience=experience,
        employment=employment
    )

    obj.save()


def close_db():
    db.close()


def show_db(job_name):
    Vacancy._meta.table_name = job_name
    query = Vacancy.select()
    for elem in query.dicts().execute():
        print(elem)


if __name__ == '__main__':
    job_name_db = input('Enter the job title you want to search for: ')
    show_db(job_name_db)
