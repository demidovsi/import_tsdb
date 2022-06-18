from xml.etree import ElementTree as ET
import commondata
import commonthread
import os
import time
import postfact
import meteofact
import meteoforecast
# ---------------------

def start_thread():
    at = commonthread.Import()
    commondata.is_live = True
    at.start()
    commondata.write_log('INFO', 'main', 'Start thread Import ' + time.ctime())


def start_thread_meteo_fact():
    commondata.MeteoFact = meteofact.MeteoFact()
    commondata.is_live_meteo_fact = True
    commondata.MeteoFact.start()
    commondata.write_log('INFO', 'main', 'Start thread MeteoFact ' + time.ctime())


def start_thread_meteo_forecast():
    commondata.MeteoForecast = meteoforecast.MeteoForecast()
    commondata.is_live_meteo_forecast = True
    commondata.MeteoForecast.start()
    commondata.write_log('INFO', 'main', 'Start thread MeteoForecast ' + time.ctime())


def start_thread_post_fact():
    at = postfact.PostFact()
    commondata.is_live_post_fact = True
    at.start()
    commondata.write_log('INFO', 'main', 'Start thread PostFact ' + time.ctime())


def read_params():
    try:
        commondata.info_code = os.environ.get("MDMPROXY_INFO_CODE")
        commondata.schema_name = os.environ.get("MDMPROXY_SCHEMA_NAME")
        commondata.url = os.environ.get("MDMPROXY_URL")
        commondata.url_tsdb = os.environ.get("MDMPROXY_URL_TSDB")
        commondata.user_name = os.environ.get("MDMPROXY_USER_NAME")
        commondata.password = os.environ.get("MDMPROXY_PASSWORD")
        st = os.environ.get("MDMPROXY_CHECK_MAS_DB")
        if st:
            commondata.check_mas_db = int(st)
        if not st:
            commondata.check_mas_db = 60
        f = open('config.xml', 'r', encoding='utf-8')
        with f:
            data = f.read()
            root = ET.fromstring(data)
            for child in root:
                if child.tag == 'MDMProxy':
                    for ch in child:
                        if (ch.tag == 'InfoCode') and not commondata.info_code:
                            commondata.info_code = ch.text
                        elif (ch.tag == 'SchemaName') and not commondata.schema_name:
                            commondata.schema_name = ch.text
                        elif (ch.tag == 'URL') and not commondata.url:
                            commondata.url = ch.text
                        elif (ch.tag == 'URL_TSDB') and not commondata.url_tsdb:
                            commondata.url_tsdb = ch.text
                        elif (ch.tag == 'UserName') and not commondata.user_name:
                            commondata.user_name = ch.text
                        elif (ch.tag == 'Password') and not commondata.password:
                            commondata.password = ch.text
                        elif (ch.tag == 'Check_mas_db') and not commondata.check_mas_db:
                            commondata.check_mas_db = int(ch.text)
        if not commondata.info_code:
            commondata.info_code = 'nsi'
        if not commondata.schema_name:
            commondata.schema_name = 'bms'
        st = 'Environments: SchemaName=' + commondata.schema_name + '; InfoCode=' + commondata.info_code + \
             '; url_MDM=' + commondata.url + '; url_TSDB=' + commondata.url_tsdb + \
             '; check_mas_db=' + str(commondata.check_mas_db) + ' sec'
        commondata.write_log('INFO', 'params', st)
    except Exception as e:
        commondata.write_log('ERROR', 'main', f"{e}")


def make_login():
    result = False
    try:
        txt, result, ch = commondata.login()
    except:
        pass
    if not result:
        commondata.count_error_connect_rest = commondata.count_error_connect_rest + 1
        commondata.write_log('INFO', 'main', 'Wait good login: ' + time.ctime() + \
                             ' Sleep 60 seconds; count_error_connect = ' + str(commondata.count_error_connect_rest))
        time.sleep(60)
        make_login()


def get_value_time(t):
    return t.hour * 3600 + t.minute * 60 + t.second + t.microsecond // 1000 / 1000


def get_duration(t: int):
    result = ''
    t1 = int(t) % 60
    t = t // 60
    result = ':' + str(t1).zfill(2)  # секунды
    t1 = int(t) % 60
    t = t // 60
    result = ':' + str(t1).zfill(2) + result  # минуты
    t1 = int(t) % 24
    t = t // 24
    result = str(int(t)) + '/' + str(t1).zfill(2) + result  # дни и часы
    return result


if __name__ == "__main__":
    d: int = 0
    commondata.write_log('WARN', 'main', time.ctime() + ' Start import_tsdb version ' + commondata.version)
    read_params()
    make_login()
    start_thread()
    start_thread_post_fact()
    start_thread_meteo_fact()
    start_thread_meteo_forecast()
    tek_time = time.time()
    time_begin = tek_time
    while True:
        if time.time() - tek_time >= 300:
            tek_time = time.time()
            d = int(tek_time - time_begin)
            commondata.write_log('INFO', 'Live', time.ctime() + ' The Servis import-tsdb version ' +
                                 commondata.version + ' works for ' + get_duration(d))
        time.sleep(1)
        if not commondata.is_live:
            commondata.write_log('WARN', 'main', 'Cancel thread Import')
            start_thread()
        if not commondata.is_live_post_fact:
            commondata.write_log('WARN', 'main', 'Cancel thread PostFact')
            start_thread_post_fact()
        if not commondata.is_live_meteo_fact:
            commondata.write_log('WARN', 'main', 'Cancel thread MeteoFact')
            start_thread_meteo_fact()
        if not commondata.is_live_meteo_forecast:
            commondata.write_log('WARN', 'main', 'Cancel thread MeteoForecast')
            start_thread_meteo_forecast()
        if (commondata.count_error_connect_rest > 50) or (commondata.count_error_connect_tsdb > 50):
            commondata.write_log('WARN', 'main', 'Restart: count_error_connect_rest = ' +
                                 str(commondata.count_error_connect_rest) + '; count_error_connect_tsdb = ' +
                                 str(commondata.count_error_connect_tsdb)
            )
            break  # перегрузиться

