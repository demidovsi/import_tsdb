import commondata
import time
import threading
import json


class PostOne(threading.Thread):
    needStop = False
    typeobj_code = None
    param_code = None
    id = None
    init_id = ''
    t_beg:str = None
    t_end:str = None
    dt_beg:float = None
    dt_end:float = None

    def __init__(self, typeobj_code, param_code, t_beg, t_end, id):
        threading.Thread.__init__(self)
        self.daemon = True
        self.typeobj_code = typeobj_code
        self.param_code = param_code
        self.t_beg = t_beg
        self.t_end = t_end
        self.dt_beg = int(time.mktime(time.strptime(self.t_beg.strip(), 't_beg=%Y-%m-%d %H:%M:%S')))
        self.dt_end = int(time.mktime(time.strptime(self.t_end.strip(), 't_end=%Y-%m-%d %H:%M:%S')))
        if not id or (id == ''):
            self.id = None
        else:
            self.id = []
            self.init_id = id
            while id != '':
                st, id = commondata.getpole(id, ',')
                st = st.strip()
                self.id.append(st)

    def run(self):
        for mas in commondata.mas_js:
            while not self.needStop:
                try:
                    if (mas['typeobj_code'] == self.typeobj_code) and \
                            (mas['param_code'] == self.param_code) and (not self.id or (mas["id"] in self.id)):
                        discret = int(mas["discret"])
                        t0 = self.dt_beg // discret * discret
                        t1 = self.dt_end // discret * discret
                        while t0 <= t1:
                            # запишем, что приняли в работу
                            txt, result = commondata.send_rest(
                                'Entity.SetValue/config?param_code=value_string' +
                                '&value=' + self.init_id +
                                '~LF~' + time.strftime('t_beg=%Y-%m-%d %H:%M:%S', time.localtime(self.dt_beg)) +
                                '~LF~' + time.strftime('t_end=%Y-%m-%d %H:%M:%S', time.localtime(self.dt_end)) +
                                time.strftime('~LF~work for=%Y-%m-%d %H:%M:%S', time.localtime(t0)) +
                                '&where=sh_name="' + self.typeobj_code + '_' + self.param_code + '"')
                            if not result:
                                commondata.write_log('ERROR ', 'TPostFact.run', txt)
                            work_one_time(t0, discret, mas["equipment_id"], mas["parameter_id"], self.typeobj_code,
                                          self.param_code, mas["id"])
                            t0 = t0 + discret
                        # запишем, что закончили работу
                        txt, result = commondata.send_rest(
                            'Entity.SetValue/config?param_code=value_string' +
                            '&value=' +
                            '&where=sh_name="' + self.typeobj_code + '_' + self.param_code + '"')
                        if not result:
                            commondata.write_log('WARN', 'PostOne.run', txt)
                except:
                    pass

def work_one_time(tek_time, discret, equipment_id, parameter_id, typeobj_code, param_code, id):
    t_beg = int(tek_time - discret) * 1000000
    t_end = int(tek_time) * 1000000
    dt = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tek_time))
    toper = time.time()
    txt, result = commondata.send_tsdb(
        'processed?id=' + equipment_id + '&tsFrom=' + str(t_beg) + '&tsTo=' +
        str(t_end) + '&aggregationWindow=' + str(discret * 100000))
    toper = time.time() - toper
    if result:
        # print(t_beg, t_end, txt)
        js = json.loads(txt)
        val = None
        count = 0
        try:
            for i in range(0, len(js)):
                mvalue = js[i]["measurements"]
                # print(mvalue)
                if parameter_id in mvalue:
                    v = mvalue[parameter_id]["value"]
                    if v:
                        if not val:
                            val = 0
                        val = val + v
                        count = count + 1
            if count > 0:
                val = val / count  # среднее значение
                txt, result = commondata.send_rest(
                    'Entity.SetHistory/' + typeobj_code + '/' + param_code + '/' +
                    str(id) + '?value=' + str(val) + '&dt=' + dt, 'POST')
                if not result:
                    commondata.count_error = commondata.count_error + 1
                    commondata.write_log('ERROR', 'work_one_time', txt)
                # else:
                #     commondata.write_log(
                #         'DEBUG', 'work_one_time', str(id) + ' ' + typeobj_code + ' ' +
                #         param_code + ' ' + str(discret) + ' ' + str(val) + ' ' +
                #         time.ctime(tek_time) + ' error_count=' + str(commondata.count_error) +
                #         "; count=" + str(count) + '; tek=' + time.ctime() + '; t=' + str(toper)
                #     )
        except Exception as err:
            commondata.count_error = commondata.count_error + 1
            commondata.write_log(
                'ERROR ', 'work_one_time' + f"{err}" + ' ' + str(id) + ' ' + typeobj_code + ' ' +
                      param_code + ' ' + str(discret))
    else:
        commondata.count_error = commondata.count_error + 1
        commondata.write_log(
            'ERROR ', 'work_one_time' + ' ' + str(id) + ' ' + typeobj_code + ' ' +
              param_code + ' ' + str(discret) + ' ' + dt + '; t=' + str(toper) + ' : ' + txt)


