# coding=utf-8
from opcua import ua
from opcua import Server
import datetime
import time
import pickle
import pandas as pd
import numpy as np
from IPython import embed
from sys import exit

if __name__ != "__main__":
    exit(1)

URL = 'opc.tcp://0.0.0.0:4840/'
FILE_NAME = 'ActualDataFeb2020.xlsx'
TIMEOUT = 5



name = 'OPCUA_SERVER'
server = Server()
server.set_endpoint(URL)
addspace = server.register_namespace(name)
node = server.get_objects_node()

# добавление объекта
Param = node.add_object(addspace, 'WATER')

data = pd.read_excel(FILE_NAME)

# перевожу в numpy, т.к. возникают проблемы с типами
table = data.to_numpy()

# список  с параметрами(типа 'node') из таблички
variables = []
for j, param in list(enumerate(data.columns.tolist()))[1:]:
    body = (pickle.dumps((table[0, j], table[0, 0]), 0)).decode()
    variables.append(Param.add_variable(addspace, param, body))
for var in variables:
    var.set_writable()

server.start()
print('Server started at {}'.format(URL))

for i in range(1, len(data)):
    for j, var in enumerate(variables):
        # Данные размещаются в виде строки "значение  / дата", немного костыльно, так как list из 2 элементов
        # передавать он не может
        body = (pickle.dumps((table[i, j + 1], table[i, 0]), 0)).decode()
        var.set_value(body)

        # var.set_value(str(table[i, j + 1]) + ' | ' + table[i, 0])
    print(i, " line sent")
    time.sleep(TIMEOUT)

print("Data transferred")

# вызов терминала IPython, нужен для отладки и чтобы сервер не выключался
# отправки всех данных
# можно выйти, написав exit
embed()
server.stop()
