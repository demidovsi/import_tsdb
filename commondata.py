import requests
from requests.exceptions import HTTPError
import json
import commondata
import time


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
is_live_meteo_fact = False
is_live_meteo_forecast = False
is_live_post_fact = False
mas_js = None  # текущий массив параметров
txt = None  # текст текущего масива параметров
check_mas_db = 30  # периодичность проверки изменений в НСИ исторических данных
count_error = 0
MeteoFact = None
MeteoForecast = None


def login_ksvd():
    result = False
    write_log('DEBUG', 'login_ksvd', "url=" + url + "; username=" + user_name + "; password=" + password)
    # txt_z = {"username": user_name, "password": password, "rememberMe": True}
    try:
        headers = {"Accept": "application/json"}
        response = requests.request(
            'POST', url + 'auth/login', headers=headers,
            json={"username": user_name, "password": password, "rememberMe": True}
            )
    except HTTPError as err:
        data = f'HTTP error occurred: {err}'
        # write_log('ERROR', 'login_ksvd', data)
    except Exception as err:
        data = f'Other error occurred: : {err}'
        # write_log('ERROR', 'login_ksvd', data)
    else:
        try:
            data = response.text
            result = response.ok
            if result:
                js = json.loads(data)
                commondata.token = js["accessToken"]
                commondata.expires = js["expires"]
        except Exception as err:
            data = f'Error occurred: : {err}'
            # write_log('ERROR', 'login_ksvd', data)
            result = False
    if not result:
        write_log(
            'ERROR', 'main', time.ctime() +
            ' not received token from ' + commondata.url + 'auth/login for username=' + commondata.user_name +
            '; ' + txt)
    return data, result


def send_rest(mes, directive="GET"):
    if not token:
        return 'Не получен токен для работы', False
    try:
        headers = {
            "Accept": "application/json"
        }
        response = requests.request(directive, url + mes, headers=headers,
                                    json={"token": token})
    except HTTPError as err:
        data = f'HTTP error occurred: {err}'
        write_log('ERROR', 'send_rest', data + '\n\t' + mes)
        result = False
    except Exception as err:
        data = f'Other error occurred: {err}'
        write_log('ERROR', 'send_rest', data + '\n\t' + mes)
        result = False
    else:
        data = response.text
        result = response.ok
    return data, result


def send_tsdb(mes: str, directive="GET", qrepeat =2) -> (str, bool):
    result = False
    q = 0
    while not result and (q < qrepeat):
        try:
            headers = {
                "Accept": "application/json"
            }
            response = requests.request(directive, url_tsdb + mes, headers=headers)
        except HTTPError as err:
            data = f'HTTP error occurred: {err}'
            result = False
            q = q + 1
        except Exception as err:
            data = f'Other error occurred: {err}'
            result = False
            q = q + 1
        else:
            data = response.text
            result = response.ok
            q = q + 1
    if not result:
        write_log('ERROR', 'send_tsdb', data + '\n\t' + mes)
    return data, result


def time_for_sql(dt, convert=True) -> str:
    if convert:
        dt = dt.toPyDateTime()
    return str(dt.year) + '-' + str(dt.month).zfill(2) + '-' + str(dt.day).zfill(2) + ' ' + \
        str(dt.hour).zfill(2) + ':' + str(dt.minute).zfill(2) + ':' + str(dt.second).zfill(2)


def write_log(level: str, src: str, msg: str):
    print(
        'lvl=' + level + ' src="' + str(src).replace('"', "'") + '" msg="' +
        str(msg).replace('"', "'") + '"')


def getpole(txt, separator=';'):
    k = txt.partition(separator)
    return k[0], k[2]


def traslateToBase(st):
    st = st.replace('\n', '~LF~').replace('(', '~A~').replace(')', '~B~').replace('@', '~a1~')
    st = st.replace(',', '~a2~').replace('=', '~a3~').replace('"', '~a4~').replace("'", '~a5~')
    st = st.replace(':', '~a6~')
    return st
