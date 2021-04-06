import threading
import commondata
import json
import time


class TImport(threading.Thread):
    needStop = False
    mas_js = None
    mas_time = []

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        txt, result = commondata.send_rest('Entity.GetListHis')
        if result:
            js = json.loads(txt)
            self.mas_js = js[0]
            for mas in self.mas_js:
                self.mas_time.append(0)
                print(mas)

    def run(self):
        while not self.needStop:
            for j in range(0, len(self.mas_js)):
                try:
                    mas = self.mas_js[j]
                    discret = int(mas["discret"])
                    tek_time = time.time()
                    if tek_time % discret <= 1:
                        t_beg = int(tek_time - 10) * 1000000
                        t_end = int(tek_time - 9) * 1000000
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
                                txt, result = commondata.send_rest(
                                'Entity.SetHistory/' + mas["typeobj_code"] + '/' + mas["param_code"] + '/' +
                                str(mas["id"]) + '/' + str(val), 'POST')
                                if not result:
                                    print(txt)
                                else:
                                    print(time.ctime(), mas["id"], mas["typeobj_code"], mas["param_code"], discret, val)

                except:
                    pass
            time.sleep(1)