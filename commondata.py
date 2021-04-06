import requests
from requests.exceptions import HTTPError
import json
import commondata


info_code = "NSI"
schema_name = 'test'
user_name = "user"
password = "!AlteroSmart123"
url = '127.0.0.1:5000/'
url_ksvd = '127.0.0.1:3000/'
token = None
expires = None

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

def make_list_his():
    txt, result = send_rest('TypeParam.GetList')
    mas = []
    if result:
        js = json.loads(txt)
        mas_js = js[0]
        for j in range(0, len(mas_js)):
            if mas_js[j]['typeinfo_code'].upper() == 'HIS':
                if mas_js[j]['typeobj_code'] + '.' + mas_js[j]['code'] not in mas:
                  mas.append(mas_js[j]['typeobj_code'] + '.' + mas_js[j]['code'])
    print(mas)