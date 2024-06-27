import requests
import pytz
from datetime import datetime

def test_get_current_time(timezone = ''):
    response = requests.get('http://localhost:8000/' + timezone)
    assert response.status_code == 200
    assert 'Current time in ' + timezone if timezone else 'GMT' in response.text
    print('test_get_current_time <' + (timezone if timezone else 'GMT') + '> passed')

def test_post_convert_time():
    data = {
        'date': {'date': '12.20.2021 22:21:05', 'tz': 'EST'},
        'target_tz': 'Europe/Moscow'
    }
    response = requests.post('http://localhost:8000/api/v1/convert', json=data)
    assert response.status_code == 200
    response_data = response.json()
    assert 'converted_date' in response_data
    
    # Проверяем правильность преобразования
    ny_tz = pytz.timezone(data['date']['tz'])
    moscow_tz = pytz.timezone(data['target_tz'])
    original_time = ny_tz.localize(datetime.strptime(data['date']['date'], '%m.%d.%Y %H:%M:%S'))
    converted_time = original_time.astimezone(moscow_tz).strftime('%Y-%m-%d %H:%M:%S %Z%z')

    #print(f"Expected: {converted_time}, Actual: {response_data['converted_date']}")

    assert response_data['converted_date'] == converted_time
    print('test_post_convert_time passed')

def test_post_datediff():
    data = {
        'first_date': '12.06.2024 22:21:05',
        'first_tz': 'EST',
        'second_date': '12:30pm 2024-02-01',
        'second_tz': 'Europe/Moscow'
    }
    response = requests.post('http://localhost:8000/api/v1/datediff', json=data)
    assert response.status_code == 200
    response_data = response.json()
    assert 'seconds_difference' in response_data
    
    # Проверяем правильность вычисления разницы
    ny_tz = pytz.timezone(data['first_tz'])
    moscow_tz = pytz.timezone(data['second_tz'])
    
    first_time = ny_tz.localize(datetime.strptime(data['first_date'], '%m.%d.%Y %H:%M:%S'))
    second_time = moscow_tz.localize(datetime.strptime(data['second_date'], '%I:%M%p %Y-%m-%d'))
    
    utc_first_time = first_time.astimezone(pytz.utc)
    utc_second_time = second_time.astimezone(pytz.utc)
    
    time_difference = int((utc_second_time - utc_first_time).total_seconds())

    #print(f"Expected: {time_difference}, Actual: {response_data['seconds_difference']}")

    assert response_data['seconds_difference'] == time_difference
    print('test_post_datediff passed')

if __name__ == '__main__':
    test_get_current_time()
    test_get_current_time('Europe/Moscow')
    test_post_convert_time()
    test_post_datediff()
    print('All tests passed')