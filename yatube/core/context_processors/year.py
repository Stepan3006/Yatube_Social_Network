import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    current_date = datetime.datetime.now()
    year = int(current_date.strftime('%Y'))
    return {
        'year': year,
    }
