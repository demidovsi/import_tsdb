# from xml.etree import ElementTree as ET
import commondata
# import commonthread
# import os
import time
# import postfact
# import meteo_fact
# import meteo_forecast


# def start_thread():
#     at = commonthread.TImport()
#     commondata.is_live = True
#     at.start()
#     commondata.write_log('INFO', 'main', 'Start Timport ' + time.ctime())
#
#
# def start_thread_meteo_fact():
#     commondata.MeteoFact = meteo_fact.TMeteoFact()
#     commondata.is_live_meteo_fact = True
#     commondata.MeteoFact.start()
#     commondata.write_log('INFO', 'main', 'Start TMeteoFact ' + time.ctime())
#
#
# def start_thread_meteo_forecast():
#     commondata.MeteoForecast = meteo_forecast.TMeteoForecast()
#     commondata.is_live_meteo_forecast = True
#     commondata.MeteoForecast.start()
#     commondata.write_log('INFO', 'main', 'Start TMeteoForecast ' + time.ctime())
#
#
# def start_thread_post_fact():
#     at = postfact.TPostFact()
#     commondata.is_live_post_fact = True
#     at.start()
#     commondata.write_log('INFO', 'main', 'Start TPostFact ' + time.ctime())
#
# def read_params():
#     try:
#         commondata.info_code = os.environ.get("MDMPROXY_INFO_CODE")
#         if not commondata.info_code:
#             commondata.info_code = 'nsi'
#         commondata.schema_name = os.environ.get("MDMPROXY_SCHEMA_NAME")
#         if not commondata.schema_name:
#             commondata.schema_name = 'bms'
#         commondata.url = os.environ.get("MDMPROXY_URL")
#         commondata.url_tsdb = os.environ.get("MDMPROXY_URL_TSDB")
#         commondata.user_name = os.environ.get("MDMPROXY_USER_NAME")
#         commondata.password = os.environ.get("MDMPROXY_PASSWORD")
#         st = os.environ.get("MDMPROXY_CHECK_MAS_DB")
#         if st:
#             commondata.check_mas_db = int(st)
#         if not st:
#             commondata.check_mas_db = 60
#         f = open('config.xml', 'r', encoding='utf-8')
#         with f:
#             data = f.read()
#             root = ET.fromstring(data)
#             for child in root:
#                 if child.tag == 'MDMProxy':
#                     for ch in child:
#                         if (ch.tag == 'InfoCode') and not commondata.info_code:
#                             commondata.info_code = ch.text
#                         elif (ch.tag == 'SchemaName') and not commondata.schema_name:
#                             commondata.schema_name = ch.text
#                         elif (ch.tag == 'URL') and not commondata.url:
#                             commondata.url = ch.text
#                         elif (ch.tag == 'URL_TSDB') and not commondata.url_tsdb:
#                             commondata.url_tsdb = ch.text
#                         elif (ch.tag == 'UserName') and not commondata.user_name:
#                             commondata.user_name = ch.text
#                         elif (ch.tag == 'Password') and not commondata.password:
#                             commondata.password = ch.text
#                         elif (ch.tag == 'Check_mas_db') and not commondata.check_mas_db:
#                             commondata.check_mas_db = int(ch.text)
#         st = 'SchemaName=' + commondata.schema_name + '; InfoCode=' + commondata.info_code + \
#              '; url_MDM=' + commondata.url + '; url_TSDB=' + commondata.url_tsdb + \
#              '; user_name=' + commondata.user_name + '; password=' + commondata.password + \
#              '; check_mas_db=' + str(commondata.check_mas_db) + ' сек'
#         commondata.write_log('INFO', 'params', st)
#     except Exception as e:
#         commondata.write_log('ERROR', 'main', f"{e}")

if __name__ == "__main__":
    commondata.write_log('INFO', 'main', time.ctime() + ' Start import_tsdb')
    while True:
        time.sleep(10)
        commondata.write_log('INFO', 'main', time.ctime() + ' after sleep')

    # read_params()
    # result = False
    # try:
    #     txt, result = commondata.login_ksvd()
    # except:
    #     result = False
    # if not result:
    #     while not result:
    #         commondata.write_log('INFO', 'main', time.ctime() + ': Sleep 60 seconds')
    #         time.sleep(60)
            # read_params()
            # try:
            #     txt, result = commondata.login_ksvd()
            # except:
            #     result = False
    # start_thread()
    # start_thread_post_fact()
    # start_thread_meteo_fact()
    # start_thread_meteo_forecast()
    # while True:
    #     time.sleep(1)
    #     if not commondata.is_live:
    #         commondata.write_log('WARN', 'main', 'Cancel Timport')
    #         start_thread()
    #     if not commondata.is_live_post_fact:
    #         commondata.write_log('WARN', 'main', 'Cancel TPostFact')
    #         start_thread_post_fact()
    #     if not commondata.is_live_meteo_fact:
    #         commondata.write_log('WARN', 'main', 'Cancel TMeteoFact')
    #         start_thread_meteo_fact()
    #     if not commondata.is_live_meteo_forecast:
    #         commondata.write_log('WARN', 'main', 'Cancel TMeteoForecast')
    #         start_thread_meteo_forecast()
