import threading
import commondata
import json
import time
import datetime


class TImport(threading.Thread):
    needStop = False
    time_check = None

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
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
        tek_time = time.time()
        while not self.needStop:
            dt = datetime.datetime.utcnow()
            for mas in commondata.mas_js:
                try:
                    discret = int(mas["discret"])
                    if tek_time % discret <= 1:
                        t_beg = int(tek_time - 1) * 1000000
                        t_end = int(tek_time) * 1000000
                        txt, result = commondata.send_tsdb(
                            'processed?id=' + mas["equipment_id"] + '&tsFrom=' + str(t_beg) + '&tsTo=' + str(t_end))
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
                                    commondata.write_log('WARN', 'Timport.run', txt)
                                else:
                                    commondata.write_log(
                                        'DEBUG', 'Timport.run', mas["id"] + ' ' + mas["typeobj_code"] + ' ' +
                                        mas["param_code"] + ' ' + str(discret) + ' ' + str(val) + ' ' +
                                        time.ctime(tek_time))

                except Exception as err:
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
                time.sleep(1)
                tek_time = time.time()
        commondata.is_live = False
