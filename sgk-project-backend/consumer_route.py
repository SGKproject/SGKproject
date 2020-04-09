# -*- coding: utf-8 -*-
import pika
import sys
import pickle
import traceback


class Data:
    max_depth = 15
    empty_val = np.nan

    def __init__(self):
        self.names = []
        self.values = np.empty()
        self.depth = 0
        self.time_cur = 0

    def put_data(self, time, name, val):

        if name not in self.names:
            self.names.append(name)
            self.depth = 1
            param_val = np.zeros((Data.max_depth, 1))
            self.values = np.concatenate((self.values, param_val), axis=1)

        index_val = self.names.index(name)

        if time > self.time_cur:
            self.time_cur = time
            self.values = shift(self.values, -1, Data.empty_val)
            self.values[max_depth - 1, index_val] = val
            self.depth += 1
        elif time == time_cur:
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
channel.queue_declare(queue='route_in',
                      arguments={'x-message-ttl': 1200},
                      durable=True)

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
    print("Received: {}".format(body))

    # функция выгрузки данных объекта
    # отправляем отработанные данные в тестирование
    channel.basic_publish(exchange='out_route',
                          routing_key='out_route_done',
                          body=(pickle.dumps(body, 0)).decode(),
                          properties=pika.BasicProperties(delivery_mode=2))
    print("Sent {}:{}".format('out_route_done', body))


channel.basic_consume(on_message_callback=callback,
                      queue='route_in',
                      auto_ack=True)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
except Exception:
    channel.stop_consuming()
    traceback.print_exc(file=sys.stdout)
