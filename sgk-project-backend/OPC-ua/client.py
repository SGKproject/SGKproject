from opcua import Client
import time
from opcua.tools import embed

URL = 'opc.tcp://0.0.0.0:4840'
PERIOD = 100

#словарь с именами параметров
params = {}
#лист с данными
total = []

class SubHandler(object):

	def event_notification(self, event):
	    print("New event recived: ", event)
	#пробовал в этом методе брать имя параметра, как node.get_browse_name().name
	#но таким образом этот метод вообще перестает работать, происходит timeout постоянно
	#наверно при get_browse_name происходит обращение к серверу, а это дорого
	#в итоге закинул имена параметров в словарь params - {nodeid, param_name}
	def datachange_notification(self, node, val, data):
		total.append((params[node.nodeid.Identifier] , val))

if __name__ == "__main__":

	client = Client(URL)

	try:
		client.connect()
		print('Client connected')
		root = client.get_root_node()

		#список переменных нужного объекта
		vars = root.get_children()[0].get_children()[1].get_variables()

		#добавляю в словарь имена параметров
		for var in vars:
			params[var.nodeid.Identifier] = var.get_browse_name().Name

		#подписка на изменения среди данных параметров
		msclt = SubHandler()
		sub = client.create_subscription(PERIOD, msclt)
		handle = sub.subscribe_data_change(vars)

		#удобная замена while(True)
		#причем в терминале можно работать с локальными переменными
		embed()
		for h in handle:
			sub.unsubscribe(h)
		sub.delete()
	finally:
		client.disconnect()