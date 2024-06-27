import json
from datetime import datetime
import pytz
from wsgiref.simple_server import make_server

def application(environ, start_response):
    path = environ.get('PATH_INFO', '').lstrip('/')
    method = environ.get('REQUEST_METHOD', '')
    if method == 'GET':
        return current_time_response(start_response, path)
    elif method == 'POST' and path == 'api/v1/convert':
        return convert_time_response(environ, start_response)
    elif method == 'POST' and path == 'api/v1/datediff':
        return date_diff_response(environ, start_response)
    else:
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return [b'404 Not Found']

def current_time_response(start_response, tz_name):
    if tz_name == '':
        tz = pytz.utc
    else:
        try:
            tz = pytz.timezone(tz_name)
        except pytz.UnknownTimeZoneError:
            start_response('400 Bad Request', [('Content-Type', 'text/plain')])
            return [b'Unknown timezone']

    current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %Z%z')
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [f"<html><body><h1>Current time in {tz_name or 'GMT'}: {current_time}</h1></body></html>".encode('utf-8')]

def convert_time_response(environ, start_response):
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        request_body = environ['wsgi.input'].read(request_body_size)
        data = json.loads(request_body)
        source_date_str = data['date']['date']
        source_tz = data['date']['tz']
        target_tz = data['target_tz']
        
        source_tz = pytz.timezone(source_tz)
        target_tz = pytz.timezone(target_tz)
        
        source_date = datetime.strptime(source_date_str, '%m.%d.%Y %H:%M:%S')
        source_date = source_tz.localize(source_date)
        target_date = source_date.astimezone(target_tz)
        
        response = {
            'converted_date': target_date.strftime('%Y-%m-%d %H:%M:%S %Z%z')
        }
        
        start_response('200 OK', [('Content-Type', 'application/json')])
        return [json.dumps(response).encode('utf-8')]
    
    except (KeyError, ValueError, pytz.UnknownTimeZoneError) as e:
        start_response('400 Bad Request', [('Content-Type', 'application/json')])
        return [json.dumps({'error': str(e)}).encode('utf-8')]

def date_diff_response(environ, start_response):
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        request_body = environ['wsgi.input'].read(request_body_size)
        data = json.loads(request_body)
        
        first_date_str = data['first_date']
        first_tz = data['first_tz']
        second_date_str = data['second_date']
        second_tz = data['second_tz']
        
        first_tz = pytz.timezone(first_tz)
        second_tz = pytz.timezone(second_tz)
        
        first_date = first_tz.localize(datetime.strptime(first_date_str, '%m.%d.%Y %H:%M:%S'))
        second_date = second_tz.localize(datetime.strptime(second_date_str, '%I:%M%p %Y-%m-%d'))
        
        utc_time_first = first_date.astimezone(pytz.utc)
        utc_time_second = second_date.astimezone(pytz.utc)
        
        diff = int((utc_time_second - utc_time_first).total_seconds())
        
        response = {
            'seconds_difference': diff
        }
        
        start_response('200 OK', [('Content-Type', 'application/json')])
        return [json.dumps(response).encode('utf-8')]
    
    except (KeyError, ValueError, pytz.UnknownTimeZoneError) as e:
        start_response('400 Bad Request', [('Content-Type', 'application/json')])
        return [json.dumps({'error': str(e)}).encode('utf-8')]

if __name__ == '__main__':
    httpd = make_server('', 8000, application)
    print("Server started on port 8000...")
    httpd.serve_forever()