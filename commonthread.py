import threading


class Parameter():
    equipment_id = None
    parameter_id = None
    discret = None
    value = None
    last_time = None

class TImport(threading.Thread):
    needStop = False
    typeobj_code = None
    param_code = None
    mas = []  # массив параметров

    def __init__(self, typeobj_code, param_code):
        threading.Thread.__init__(self)
        self.daemon = True
        self.typeobj_code = typeobj_code
        self.param_code = param_code

    def run(self):
        pass
