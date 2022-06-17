import threading
import commondata
import json
import time
import datetime
import requests
from requests.exceptions import HTTPError


class MeteoFact(threading.Thread):
    needStop = False
    url = ''
    api_id = None

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

    def send_url(self, url, api_id, x, y, directive="GET", qrepeat=2) -> (str, bool):
        result = False
        q = 0
        while not result and (q < qrepeat):
            try:
                headers = {
                    "Accept": "application/json"
                }
                mes = '?lat=' + str(x) + '&lon=' + str(y) + '&appid=' + api_id + '&units=metric'
                response = requests.request(directive, url + mes, headers=headers)
                # print(url + mes)
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
            commondata.write_log('ERROR', 'send_url', data + '\n\t' + mes)
        return data, result

    def run(self):
        try:
            tek_time = time.time()
            while not self.needStop and (commondata.count_error < 50):
                dt = datetime.datetime.utcnow()
                for mas in commondata.mas_js:
                    if mas["type_his"] != 'meteo':
                        continue
                    # обрабатываем только тип временных рядов meteo (фактическая погода)
                    try:
                        discret = int(mas["discret"])
                        delta = tek_time % discret
                        if delta <= 1:
                            toper = time.time()
                            txt, result = self.send_url(
                                commondata.traslateFromBase(mas['meteo_url']), mas['meteo_api_id'], mas['x'], mas['y'])
                            toper = time.time() - toper
                            val = json.loads(txt)['current']
                            st = commondata.time_for_sql(dt, False)

                            txt = 'v1/MDM/his/' + commondata.schema_name + '/' + mas["typeobj_code"] + '/' + \
                                    mas["param_code"] + '/' +  str(mas["id"]) + '?value_json=' + str(val) + '&dt=' + st
                            txt, result = commondata.send_rest(txt, 'POST')
                            if not result or ('error_sql' in txt):
                                commondata.count_error = commondata.count_error + 1
                                commondata.write_log('ERROR', 'MeteoFact', time.ctime() + ' ' + txt)
                            # else:
                            #     commondata.write_log(
                            #         'DEBUG', 'MeteoFact', str(mas["id"]) + ' ' + mas["typeobj_code"] + ' ' +
                            #         mas["param_code"] + ' ' + str(discret) + ' ' +
                            #         time.ctime(tek_time) + ' error_count=' + str(commondata.count_error) +
                            #         '; x=' + str(mas["x"]) + '; y=' + str(mas["y"]) +
                            #         '; tek=' + time.ctime() + '; t=' + str(toper)
                            #     )
                    except Exception as err:
                        commondata.count_error = commondata.count_error + 1
                        commondata.write_log(
                            'ERROR ', 'MeteoFact.run', time.ctime() + ' ' + f"{err}" + ' ' + mas["id"] +
                                                        ';' + mas["typeobj_code"] + '; ' + mas["param_code"] +
                                                        '; x=' + str(mas["x"]) +
                                                        '; y=' + str(mas["y"]) + '; ' + str(mas["discret"]))
                time.sleep(1)
                tek_time = time.time()

        except Exception as err:
            commondata.write_log('FATAL ', 'MeteoFact.run', time.ctime() + ' ' + f"{err}")
        commondata.is_live_meteo_fact = False

