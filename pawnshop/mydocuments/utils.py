import datetime

def format_spanish_date(date):
    moths =[
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    day = date.day
    month = moths[date.month-1]
    year = date.year

    return f'{day} de {month} del {year}'