# -*- coding: utf-8 -*-
import pika
import sys
import pickle
import traceback
import copy
import numpy as np


class Data:
    max_depth = 15
    empty_val = np.nan

    def __init__(self):
        self.names = []
        self.record_times = np.zeros((Data.max_depth, 1))
        self.values = np.empty((Data.max_depth, 0))
        self.depth = 0
        self.time_cur = 0

    def put(self, name, val, time):

        if name not in self.names:
            self.names.append(name)
            self.depth = 1
            param_val = np.zeros((Data.max_depth, 1))
            self.values = np.concatenate((self.values, param_val), axis=1)

        index_val = self.names.index(name)

        if time > self.time_cur:
            self.record_times = Data.shift(self.record_times, -1, Data.empty_val)
            self.record_times[Data.max_depth - 1] = time
            self.time_cur = time
            self.values = Data.shift(self.values, -1, Data.empty_val)
            self.values[Data.max_depth - 1, index_val] = val
            self.depth += 1
        elif time == self.time_cur:
            self.values[Data.max_depth - 1, index_val] = val

    @staticmethod
    def shift(arr, num, fill_value=np.nan):
        result = np.empty_like(arr)
        if num > 0:
            result[:num] = fill_value
            result[num:] = arr[:-num]
        elif num < 0:
            result[num:] = fill_value
            result[:num] = arr[-num:]
        else:
            result = arr
        return result


# подключение к кролику
conn_params = pika.ConnectionParameters('rabbit', 5672)
connection = pika.BlockingConnection(conn_params)
channel = connection.channel()

# вывод на отладку данных
channel.exchange_declare(exchange='out_route',
                         exchange_type='topic')

# маршрутизация
channel.queue_declare(queue='route_in1111',
                      arguments={'x-message-ttl': 60000},
                      durable=True)

# инициализируем буфер данных
data = Data()

print("Waiting for messages for routing to маршрутизация. To exit press CTRL+C")


def callback(ch, method, properties, body):
    # функция загрузки данных объекта
    # далее пример для 1 параметра для показа функциональности
    # отправляем сырые данные в тестирование
    body = pickle.loads(body.encode())
    channel.basic_publish(exchange='out_route',
                          routing_key='out_route_wet',
                          body=(pickle.dumps(body, 0)).decode(),
                          properties=pika.BasicProperties(
                              delivery_mode=2
                          ))
    routing_key_info = 'out_route_wet'
    print("Sent {}:{}".format(routing_key_info, body))

    # здесь - тело маршрутизатора должно быть

    # аргументы в tuple в том же порядке
    data.put(*body)

    print("Received: {}".format(body))

    print("Data now:")
    intermed = np.concatenate((data.record_times, data.values), axis=1)
    intermed_names = ["time"]
    intermed_names.extend(data.names)

    print(intermed_names)
    print(intermed)

    # функция выгрузки данных объекта
    # отправляем отработанные данные в тестирование
    channel.basic_publish(exchange='out_route',
                          routing_key='out_route_done',
                          body=(pickle.dumps(body, 0)).decode(),
                          properties=pika.BasicProperties(delivery_mode=2))
    print("Sent {}:{}".format('out_route_done', body))


channel.basic_consume(on_message_callback=callback,
                      queue='route_in1111',
                      auto_ack=True)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
except Exception:
    channel.stop_consuming()
    traceback.print_exc(file=sys.stdout)
