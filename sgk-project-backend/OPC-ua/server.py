from opcua import ua
from opcua import Server
import datetime
import time
import pandas as pd
from IPython import embed

URL = 'opc.tcp://0.0.0.0:4840'
FILE_NAME = 'ActualDataFeb2020.xlsx'
TIMEOUT = 5

if __name__ == "__main__":
	
	name = 'OPCUA_SERVER'
	server = Server()
	server.set_endpoint(URL)
	addspace = server.register_namespace(name)
	node = server.get_objects_node()

	#добавление объекта
	Param = node.add_object(addspace, 'WATER')

	data = pd.read_excel(FILE_NAME)

	#перевожу в numpy, т.к. возникают проблемы с типами
	table = data.to_numpy()

	#список  с параметрами(типа 'node') из таблички
	variables = []
	for j, param in enumerate(data.columns.tolist()):
		variables.append(Param.add_variable(addspace, param, table[0, j]))
	for var in variables:
		var.set_writable()
	
	server.start()
	print('Server started at {}'.format(URL))
	#print('Put enter to transfer data')
	#input()

	for i in range (1, len(data)):
		for j, var in list(enumerate(variables))[1:]:
			var.set_value((str(table[i, j])))
		print(i, " line sent")
		time.sleep(TIMEOUT)

	print("Data transferred")

	#вызов терминала IPython, нужен для отладки и чтобы сервер не выключался
	#отправки всех данных
	#можно выйти, написав exit
	embed()
	server.stop()
