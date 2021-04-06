from xml.etree import ElementTree as ET
import commondata
import os


if __name__ == '__main__':
    print(f'Hi word. I am "Import from TSDB"')

try:
    commondata.info_code =  os.environ.get("MDMPROXY_INFO_CODE")
    commondata.schema_name =  os.environ.get("MDMPROXY_SCHEMA_NAME")
    commondata.url =  os.environ.get("MDMPROXY_URL")
    commondata.url_ksvd =  os.environ.get("MDMPROXY_URL_KSVD")
    commondata.user_name =  os.environ.get("MDMPROXY_USER_NAME")
    commondata.password =  os.environ.get("MDMPROXY_PASSWORD")
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
                    elif ch.tag == 'URL_KSVD':
                        commondata.url_ksvd = ch.text
                    elif ch.tag == 'UserName':
                        commondata.user_name = ch.text
                    elif ch.tag == 'Password':
                        commondata.password = ch.text
except Exception as e:
    print('Ошибка ' + f"{e}")
print('\turl=', commondata.url)
print('\turl_ksvd=', commondata.url_ksvd)
print('\tuser_name=', commondata.user_name)
print('\tpassword=', commondata.password)
txt, result = commondata.login_ksvd()
if result:
    print(commondata.token)
commondata.make_list_his()

while True:
    pass  ###

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
