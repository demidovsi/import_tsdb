from xml.etree import ElementTree as ET
import commondata
import commonthread
import os
import time
import postfact
import meteo_fact
import meteo_forecast
import datetime


def start_thread():
    at = commonthread.Import()
    commondata.is_live = True
    at.start()
    commondata.write_log('INFO', 'main', 'Start thread Import ' + time.ctime())


def start_thread_meteo_fact():
    commondata.MeteoFact = meteo_fact.MeteoFact()
    commondata.is_live_meteo_fact = True
    commondata.MeteoFact.start()
    commondata.write_log('INFO', 'main', 'Start thread MeteoFact ' + time.ctime())


def start_thread_meteo_forecast():
    commondata.MeteoForecast = meteo_forecast.MeteoForecast()
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
        if not commondata.info_code:
            commondata.info_code = 'nsi'
        commondata.schema_name = os.environ.get("MDMPROXY_SCHEMA_NAME")
        if not commondata.schema_name:
            commondata.schema_name = 'bms'
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
        st = 'Enviroments: SchemaName=' + commondata.schema_name + '; InfoCode=' + commondata.info_code + \
             '; url_MDM=' + commondata.url + '; url_TSDB=' + commondata.url_tsdb + \
             '; check_mas_db=' + str(commondata.check_mas_db) + ' sec'
        commondata.write_log('INFO', 'params', st)
    except Exception as e:
        commondata.write_log('ERROR', 'main', f"{e}")

def make_login():
    read_params()
    result = False
    try:
        txt, result = commondata.login_ksvd()
    except:
        pass
    if not result:
        commondata.write_log('INFO', 'main', 'Wait good login: ' + time.ctime() + ' Sleep 60 seconds')
        time.sleep(60)
        make_login()

def get_value_time(t):
    return t.hour * 3600 + t.minute * 60 + t.second + t.microsecond // 1000 / 1000

if __name__ == "__main__":
    commondata.write_log('WARN', 'main', time.ctime() + ' Start import_tsdb')
    make_login()
    start_thread()
    start_thread_post_fact()
    start_thread_meteo_fact()
    start_thread_meteo_forecast()
    tek_time = time.time()
    time_begin = datetime.datetime.now()
    while True:
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
        if time.time() - tek_time >= 300:
            tek_time = time.time()
            d = get_value_time(datetime.datetime.now()) - get_value_time(time_begin)
            commondata.write_log('INFO', 'Live', time.ctime() + ' The Servis import-tsdb works for ' + "%.3f" % d + ' sec')
