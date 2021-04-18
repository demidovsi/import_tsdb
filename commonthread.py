import threading
import commondata
import json
import time
import datetime


class TImport(threading.Thread):
    needStop = False
    time_check = None
    time_login = None

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        commondata.count_error = 0
        commondata.txt, result = self.get_params()
        if result:
            self.print_params()
        self.time_check = time.time()  # время последней проверки базы данных

    def get_params(self):
        txt, result = commondata.send_rest('Entity.GetListHis')
        return txt, result

    def print_params(self):
        js = json.loads(commondata.txt)
        commondata.mas_js = js[0]
        for mas in commondata.mas_js:
            commondata.write_log('DEBUG', 'Timport.print_params', mas)

    def run(self):
        try:
            tek_time = time.time()
            time_login = time.time()
            while not self.needStop and (commondata.count_error < 50):
                dt = datetime.datetime.utcnow()
                for mas in commondata.mas_js:
                    try:
                        discret = int(mas["discret"])
                        delta = tek_time % discret
                        if delta <= 1:
                            t_beg = int(tek_time - discret) * 1000000
                            t_end = int(tek_time) * 1000000
                            toper = time.time()
                            txt, result = commondata.send_tsdb(
                                'processed?id=' + mas["equipment_id"] + '&tsFrom=' + str(t_beg) + '&tsTo=' +
                                str(t_end) + '&aggregationWindow='+str(discret*1000000))
                            toper = time.time() - toper
                            if result:
                                # print(t_beg, t_end, txt)
                                js = json.loads(txt)
                                val = None
                                count = 0
                                for i in range(0, len(js)):
                                    mvalue = js[i]["measurements"]
                                    # print(mvalue)
                                    if mas["parameter_id"] in mvalue:
                                        v = mvalue[mas["parameter_id"]]["value"]
                                        if v:
                                            if not val:
                                                val = 0
                                            val = val + v
                                            count = count + 1
                                if count > 0:
                                    val = val / count  # среднее значение
                                    st = commondata.time_for_sql(dt, False)
                                    txt, result = commondata.send_rest(
                                        'Entity.SetHistory/' + mas["typeobj_code"] + '/' + mas["param_code"] + '/' +
                                        str(mas["id"]) + '/' + str(val) + '?dt=' + st, 'POST')
                                    if not result:
                                        commondata.count_error = commondata.count_error + 1
                                        commondata.write_log('WARN', 'Timport.run', txt)
                                    else:
                                        commondata.write_log(
                                            'DEBUG', 'Timport.run', mas["id"] + ' ' + mas["typeobj_code"] + ' ' +
                                            mas["param_code"] + ' ' + str(discret) + ' ' + str(val) + ' ' +
                                            time.ctime(tek_time) + ' error_count=' + str(commondata.count_error) +
                                                                    "; count=" + str(count) + '; t=' + str(toper)
                                        )
                            else:
                                commondata.count_error = commondata.count_error + 1


                    except Exception as err:
                        commondata.count_error = commondata.count_error + 1
                        commondata.write_log(
                            'ERROR ', 'Timport.run' + f"{err}" + ' ' + mas["id"] + ' ' + mas["typeobj_code"] + ' ' +
                            mas["param_code"] + ' ' + mas["discret"])
                # цикл по параметрам закончен
                if tek_time - self.time_check >= commondata.check_mas_db:
                    txt, result = self.get_params()
                    if result:
                        if txt != commondata.txt:
                            commondata.txt = txt
                            commondata.mas_js = json.loads(commondata.txt)[0]
                            print(time.ctime(), 'check_mas_db - приняты изменения')
                            self.print_params()
                    self.time_check = time.time()
                else:
                    if time.time() - time_login >= 3600:  #  прошел час
                        print(time.ctime(), commondata.token)
                        commondata.login_ksvd()
                        time_login = time.time()
                time.sleep(1)
                tek_time = time.time()
        except Exception as err:
            commondata.write_log('FATAL ', 'Timport.run', f"{err}")
        commondata.is_live = False


class TPostFact(threading.Thread):
    needStop = False
    time_check = None

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.time_check = 0  # время последней проверки базы данных

    def run(self):
        while True:
            tek_time = time.time()
            try:
                if tek_time - self.time_check >= commondata.check_mas_db * 2:
                    list = []
                    list_obj = []
                    list_param = []
                    for mas in commondata.mas_js:
                        st = mas["typeobj_code"] + '_' + mas['param_code']
                        if st not in list:
                            list.append(st)  # список возможных постфактумов
                            list_obj.append(mas["typeobj_code"])
                            list_param.append(mas["param_code"])
                    if len(list) > 0:
                # читаем конфигурацию
                        txt, result = commondata.send_rest('Entity.FullList/config')
                        if result:
                            js = json.loads(txt)[0]
                            for i in range(0, len(js)):
                                st = js[i]["sh_name"]
                                if st in list:  # можно делать потоки для постфактумного заполнения
                                    mt = js[i]["value_string"]
                                    for j in range(0, len(list)):
                                        if st == list[j]:
                                            typeobj_code = list_obj[j]
                                            param_code = list_param[j]
                                            break
                                    t_beg, t_end = commondata.getpole(mt, '~LF~')
                                    print(typeobj_code, param_code, t_beg, t_end)
                    self.time_check = time.time()
                time.sleep(1)

            except Exception as err:
                commondata.write_log('FATAL ', 'Timport.run', f"{err}")
        commondata.is_live_post_fact = False
