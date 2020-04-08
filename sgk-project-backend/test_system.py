# -*- coding: utf-8 -*-
import pika
import sys
import pickle
import traceback

# подключение к кролику
conn_params = pika.ConnectionParameters('rabbit', 5672)
connection = pika.BlockingConnection(conn_params)
channel = connection.channel()

# вывод на отладку данных
channel.exchange_declare(exchange='out_route',
                         exchange_type='topic')

# for wet

result_wet = channel.queue_declare('', exclusive=True)

queue_name_wet = result_wet.method.queue

channel.queue_bind(exchange='out_route',
                   queue=queue_name_wet,
                   routing_key='out_route_wet')

# for dry
result_done = channel.queue_declare('', exclusive=True)
queue_name_done = result_done.method.queue

channel.queue_bind(exchange='out_route',
                   queue=queue_name_done,
                   routing_key='out_route_done')

print("Waiting for messages from routing to тестирование. To exit press CTRL+C")


def callback(ch, method, properties, body):
    ###далее пример для 1 параметра для показа функциональности
    body = pickle.loads(body.encode())
    if method.routing_key == 'out_route_wet':
        print("Received wet: {}:{}".format(method.routing_key, body))
    else:
        print("Received done: {}:{}".format(method.routing_key, body))
    channel.basic_ack(delivery_tag=method.delivery_tag)


###функция загрузки данных объекта
# отправляем сырые данные в тестирование
channel.basic_consume(on_message_callback=callback, queue=queue_name_wet, auto_ack=False)
###функция выгрузки данных объекта  
# отправляем отработанные данные в тестирование
channel.basic_consume(on_message_callback=callback, queue=queue_name_done, auto_ack=False)
try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
except Exception:
    channel.stop_consuming()
    traceback.print_exc(file=sys.stdout)
