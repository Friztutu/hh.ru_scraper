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
    salary = IntegerField(column_name='salary', null=True)
    date = DateField(column_name='date')
    town = CharField(column_name='town', max_length=70)
    experience = SmallIntegerField(column_name='experience', null=True)
    employment = CharField(column_name='employment', max_length=50, null=True)
    parse_date = DateField(column_name='parse_date')

    class Meta:
        table_name = 'PythonVacancies'

    @classmethod
    def init_db(cls, job_name):
        cls._meta.table_name = job_name
        db.connect()
        if db.table_exists(job_name):
            db.drop_tables(Vacancy)
        db.create_tables([Vacancy])

    @classmethod
    def insert_into_table(cls, link, name, salary, data, town, experience, employment, parse_date):
        obj = cls.create(
            vacancy_link=link,
            vacancy_name=name,
            salary=salary,
            date=psycopg2.Date(*map(int, data.split())),
            town=town,
            experience=experience,
            employment=employment,
            parse_date=parse_date,
        )

        obj.save()

    @staticmethod
    def close_db():
        db.close()

    @classmethod
    def show_db(cls, job_name):
        cls._meta.table_name = job_name
        query = Vacancy.select()
        for elem in query.dicts().execute():
            print(elem)


if __name__ == '__main__':
    job_name_db = input('Enter the job title you want to search for: ')
    Vacancy.show_db(job_name_db)
