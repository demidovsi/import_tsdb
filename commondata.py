import requests
from requests.exceptions import HTTPError
import json
import commondata
import commonthread


info_code = "NSI"
schema_name = 'test'
user_name = "user"
password = "!AlteroSmart123"
url = '127.0.0.1:5000/'
url_ksvd = '127.0.0.1:3000/'
url_tsdb = '127.0.0.1:3001/'
token = None
expires = None
mas_thread = []

def login_ksvd():
    result = False
    txt_z = {"username": user_name, "password": password, "rememberMe": True}
    try:
        headers = {"Accept": "application/json"}
        response = requests.request('POST', url + 'auth/login', headers=headers,
            json={"username": user_name, "password": password, "rememberMe": True}
            )
    except HTTPError as err:
        txt = f'HTTP error occurred: {err}'
        print('Ошибка LOGIN', txt)
    except Exception as err:
        txt = f'Other error occurred: : {err}'
        print('Ошибка LOGIN', txt)
    else:
        try:
            txt = response.text
            result = response.ok
            if result:
                js = json.loads(txt)
                commondata.token = js["accessToken"]
                commondata.expires = js["expires"]
        except Exception as err:
            txt_error = f'Error occurred: : {err}'
            print('Ошибка LOGIN', txt)
    return txt, result


def send_rest(mes, dir="GET"):
    if not token:
        return 'Не получен токен для работы', False
    try:
        headers = {
            "Accept": "application/json"
        }
        response = requests.request(dir, url + mes, headers=headers,
                                    json={"token": commondata.token})
    except HTTPError as err:
        txt = f'HTTP error occurred: {err}'
        print('Ошибка запроса к RESTProxy', txt + '\n\t' + mes)
        result = False
    except Exception as err:
        txt = f'Other error occurred: {err}'
        print('Ошибка запроса к RESTProxy', txt + '\n\t' + mes)
        result = False
    else:
        txt = response.text
        result = response.ok
    return txt, result


def send_tsdb(mes, dir="GET"):
    try:
        headers = {
            "Accept": "application/json"
        }
        response = requests.request(dir, url_tsdb + mes, headers=headers)
    except HTTPError as err:
        txt = f'HTTP error occurred: {err}'
        print('Ошибка запроса к RESTProxy', txt + '\n\t' + mes)
        result = False
    except Exception as err:
        txt = f'Other error occurred: {err}'
        print('Ошибка запроса к RESTProxy', txt + '\n\t' + mes)
        result = False
    else:
        txt = response.text
        result = response.ok
    return txt, result


