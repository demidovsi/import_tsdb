import requests
from requests.exceptions import HTTPError
import json
import commondata


info_code = "NSI"
schema_name = 'test'
user_name = "user"
password = "!AlteroSmart123"
url = '127.0.0.1:5000/'
url_tsdb = '127.0.0.1:3001/'
token = None
expires = None
mas_thread = []
is_live = False
mas_js = None  # текущий массив параметров
txt = None  # текст текущего масива параметров
check_mas_db = 30  # периодичность проверки изменений в НСИ исторических данных

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
        commondata.write_log('ERROR', 'login_ksvd', txt)
    except Exception as err:
        txt = f'Other error occurred: : {err}'
        commondata.write_log('ERROR', 'login_ksvd', txt)
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
            commondata.write_log('ERROR', 'login_ksvd', txt_error)
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
        write_log('ERROR', 'send_rest', txt + '\n\t' + mes)
        result = False
    except Exception as err:
        txt = f'Other error occurred: {err}'
        write_log('ERROR', 'send_rest', txt + '\n\t' + mes)
        result = False
    else:
        txt = response.text
        result = response.ok
    return txt, result


def send_tsdb(mes: str, dir="GET") -> (str, bool):
    try:
        headers = {
            "Accept": "application/json"
        }
        response = requests.request(dir, url_tsdb + mes, headers=headers)
    except HTTPError as err:
        txt = f'HTTP error occurred: {err}'
        write_log('ERROR', 'send_tsdb', txt + '\n\t' + mes)
        result = False
    except Exception as err:
        txt = f'Other error occurred: {err}'
        write_log('ERROR', 'send_tsdb', txt + '\n\t' + mes)
        result = False
    else:
        txt = response.text
        result = response.ok
    return txt, result


def time_for_sql(dt, convert=True) -> str:
    if convert:
        dt = dt.toPyDateTime()
    return str(dt.year) + '-' + str(dt.month) + '-' + str(dt.day) + ' ' + \
        str(dt.hour) + ':' + str(dt.minute) + ':' + str(dt.second)


def write_log(level: str, src: str, msg: str):
    print(
        "lvl=" + level + ' ' + 'scr="' + src +'" msg="' +
        str(msg).replace('"','\"') + '"')
