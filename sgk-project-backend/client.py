# coding=utf-8
from opcua import Client
import pickle
import pika


URL = 'opc.tcp://server:4840/'
PERIOD = 100

params = {}
total = []
channel = ''

conn_params = pika.ConnectionParameters('rabbit', 5672)
connection = pika.BlockingConnection(conn_params)
channel = connection.channel()

channel.queue_declare(queue='route_in',
                      arguments={'x-message-ttl': 60000},
                      durable=True)


class SubHandler(object):

    # пробовал в этом методе брать имя параметра, как node.get_browse_name().name
    # но таким образом этот метод вообще перестает работать, происходит timeout постоянно
    # наверно при get_browse_name происходит обращение к серверу, а это дорого
    # в итоге закинул имена параметров в словарь params - {nodeid, param_name}
    @staticmethod
    def datachange_notification(node, val, data):
        print((params[node.nodeid.Identifier], val))
        total.append((params[node.nodeid.Identifier], val))

        body= str((params[node.nodeid.Identifier], val))
        channel.basic_publish(exchange='',
                              routing_key='route_in',
                              body=(pickle.dumps(body, 0)).decode(),
                              properties=pika.BasicProperties(delivery_mode=2))


if __name__ == "__main__":
    client = Client(URL)

    try:
        client.connect()
        print('Client connected')
        root = client.get_root_node()

        # список переменных нужного объекта
        vars = root.get_children()[0].get_children()[1].get_variables()

        # добавляю в словарь имена параметров
        for var in vars:
            params[var.nodeid.Identifier] = var.get_browse_name().Name

        # подписка на изменения среди данных параметров
        msclt = SubHandler()
        sub = client.create_subscription(PERIOD, msclt)
        handle_data = sub.subscribe_data_change(vars)
        handle_events = sub.subscribe_events()

        while (True):
            a = 1

    finally:
        client.disconnect()
