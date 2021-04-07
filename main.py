from xml.etree import ElementTree as ET
import commondata
import commonthread
import os
import time


def start_thread():
    at = commonthread.TImport()
    commondata.is_live = True
    at.start()
    commondata.write_log('INFO', 'main', 'Start Timport ' + time.ctime())

# if __name__ == '__main__':
    # print(f'Hi word. I am "Import from TSDB"')


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
    f = open('config.xml', 'r', encoding='utf-8')
    with f:
        data = f.read()
        root = ET.fromstring(data)
        for child in root:
            if child.tag == 'MDMProxy':
                for ch in child:
                    if ch.tag == 'InfoCode':
                        commondata.info_code = ch.text
                    elif ch.tag == 'SchemaName':
                        commondata.schema_name = ch.text
                    elif ch.tag == 'URL':
                        commondata.url = ch.text
                    elif ch.tag == 'URL_TSDB':
                        commondata.url_tsdb = ch.text
                    elif ch.tag == 'UserName':
                        commondata.user_name = ch.text
                    elif ch.tag == 'Password':
                        commondata.password = ch.text
                    elif ch.tag == 'Check_mas_db':
                        commondata.check_mas_db = int(ch.text)
except Exception as e:
    commondata.write_log('INFO', 'main', f"{e}")
commondata.write_log('INFO', 'main', 'url_MDM=' + commondata.url)
commondata.write_log('INFO', 'main', 'url_TSDB=' + commondata.url_tsdb)
commondata.write_log('INFO', 'main', 'user_name=' + commondata.user_name)
commondata.write_log('INFO', 'main', 'password=' + commondata.password)
commondata.write_log('INFO', 'main', 'check_mas_db=' + str(commondata.check_mas_db) + ' сек')
txt, result = commondata.login_ksvd()
if result:
    # print(commondata.token)
    start_thread()
while True:
    time.sleep(1)
    if not commondata.is_live:
        commondata.write_log('WARN', 'main', 'Cancel Timport')
        start_thread()
