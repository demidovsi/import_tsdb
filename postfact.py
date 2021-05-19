import commondata
import time
import threading
import json
import postone

class PostFact(threading.Thread):
    needStop = False
    time_check = None

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.time_check = 0  # время последней проверки базы данных

    def run(self):
        while not self.needStop:
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
                            js = json.loads(txt)
                            for i in range(0, len(js)):
                                st = js[i]["sh_name"]
                                if st in list:  # можно делать потоки для постфактумного заполнения
                                    if "value_string" in js[i]:
                                        mt = js[i]["value_string"]
                                        if mt != '':
                                            for j in range(0, len(list)):
                                                if st == list[j]:
                                                    typeobj_code = list_obj[j]
                                                    param_code = list_param[j]
                                                    break
                                            id, mt = commondata.getpole(mt, '~LF~')  # пусто или список id через запятую
                                            t_beg, t_end = commondata.getpole(mt, '~LF~')
                                            t_end, work = commondata.getpole(t_end, '~LF~')
                                            if not work or (work == ""):  # можно запускать поток
                                                at = postone.PostOne(typeobj_code, param_code, t_beg, t_end, id)
                                                at.start()

                    self.time_check = time.time()
                time.sleep(1)

            except Exception as err:
                commondata.write_log('FATAL ', 'PostFact.run', f"{err}")
                self.time_check = time.time()
        commondata.is_live_post_fact = False

