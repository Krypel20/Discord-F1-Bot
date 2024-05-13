from constants import english_to_polish_months
from datetime import datetime

def convert_to_Warsaw_time(date_times):
    new_times = []
    for czas in date_times:
        h, m = map(int, czas.split(':'))
        h += 1
        if h == 24:
            h = 0
        new_time = f"{h:02d}:{m:02d}"
        new_times.append(new_time)
    return new_times

def convert_dates_to_weekdays(date_strings):
    converted_dates = []
    
    for date_string in date_strings:
        for polish_month, english_month in english_to_polish_months.items():
            if polish_month in date_string:
                date_string = date_string.replace(polish_month, english_month)
                break
        
        date_object = datetime.strptime(date_string, '%d %b')
        weekday_num = (date_object.weekday() + 1) % 7
        weekdays = ['Pn', 'Wt', 'Śr', 'Cz', 'Pt', 'Sb', 'Nd']
        weekday_name = weekdays[weekday_num]
        converted_dates.append(weekday_name)
    
    return converted_dates

def convert_date_to_weekday(date_string):
    for polish_month, english_month in english_to_polish_months.items():
        if polish_month is date_string:
            date_string = date_string.replace(polish_month, english_month)
            break
    
    date_object = datetime.strptime(date_string, '%d %b')
    weekday_num = (date_object.weekday() + 1) % 7
    weekdays = ['Pn', 'Wt', 'Śr', 'Cz', 'Pt', 'Sb', 'Nd']
    weekday_name = weekdays[weekday_num]
    return weekday_name

def convert_date_to_polish_months(dates):
    polish_dates = []
    for date_string in dates:
        for polish_month, english_month in english_to_polish_months.items():
            if english_month in date_string:
                day = date_string.split()[0]
                polish_dates.append(f"{day} {polish_month}")
                break
    return polish_dates

def remove_duplicates(list):
    seen = set()
    result = []
    
    for item in list:
        if item not in seen:
            seen.add(item)
            result.append(item)
    
    return result