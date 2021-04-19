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
                                str(t_end) + '&aggregationWindow='+str(discret*100000))
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
                                            "; count=" + str(count) + '; tek=' + time.ctime() + '; t=' + str(toper)
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
                            commondata.write_log(
                                'WARN', 'Timport.run', time.ctime() + 'check_mas_db - приняты изменения')
                            self.print_params()
                    self.time_check = time.time()
                else:
                    if time.time() - time_login >= 3600:  #  прошел час
                        commondata.write_log(
                            'WARN', 'Timport.run', time.ctime() + 'login_ksvd')
                        # print(time.ctime(), commondata.token)
                        commondata.login_ksvd()
                        time_login = time.time()
                time.sleep(1)
                tek_time = time.time()
        except Exception as err:
            commondata.write_log('FATAL ', 'Timport.run', f"{err}")
        commondata.is_live = False
