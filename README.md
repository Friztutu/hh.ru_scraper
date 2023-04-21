<p align="center">
      <img src="https://i.ibb.co/52yx53P/parse.png" width="420">
</p>

<p align="center">
   <img src="https://img.shields.io/badge/python-3.10-green" alt="Python Version">
   <img src="https://img.shields.io/badge/Version-1.0(Alpha)-yellowgreen" alt="Parser Version">
   <img src="https://img.shields.io/badge/Licence-MIT-blueviolet" alt="License">
</p>

## About


Job parser for hh.ru . Writes all vacancies to the database (postgresql) on request. The job title, link, salary, required work experience, employment will be recorded. It can be used to analyze the labor market in the post-Soviet space

## Documentation

--CLASS HeadHunterParser

       
class for parsing information from all job cards on the page:

use case

    search_job = input("Enter the job title you want to search for: ")

    for page in range(40):
        el = HeadHunterParser(search_job, page=page)
        for info in el:
            print(*info, sep='\n')
       
methods HeadHunterParser:
       
__init__ - sends hh.ru get request, create main page soup
      
__card_soup_generator - generator with links to job cards -> yield str (card link)
      
__convert_salary - removes extra characters, puts an icon in the currency in which the salary is indicated -> return str ('salary<valute icon>')
      
__convert_data - removes extra characters,  -> return str ('year month day)
      
__convert_experience - removes extra characters, return int (required work experience)
      
__iter__ - generator with information from the vacancy card -> yeild tuple ( vacancy link, vacancy name, salary, data, town, required work experience, employment)


## Developers

- [Alex](https://github.com/Friztutu)

## License

Project JobParser is distributed under the MIT licence
