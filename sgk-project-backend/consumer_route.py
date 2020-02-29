# -*- coding: utf-8 -*-
import pika
import sys
import pickle
import traceback

#подключение к кролику
conn_params = pika.ConnectionParameters('rabbit', 5672)
connection = pika.BlockingConnection(conn_params)
channel = connection.channel()


#вывод на отладку данных
channel.exchange_declare(exchange='out_route', 
  exchange_type='topic')

#маршрутизация
channel.queue_declare(queue='route_in', 
  arguments={'x-message-ttl':60000}, 
  durable=True)

print("Waiting for messages for routing to маршрутизация. To exit press CTRL+C")


def callback(ch, method, properties, body):
  ###функция загрузки данных объекта
  ###далее пример для 1 параметра для показа функциональности
  #отправляем сырые данные в тестирование
  body=pickle.loads(body.encode())
  channel.basic_publish(exchange='out_route',
    routing_key='out_route_wet',
    body=(pickle.dumps(body, 0)).decode(),
    properties = pika.BasicProperties(
      delivery_mode=2
      ))
  routing_key_info='out_route_wet'
  print("Sent %r:%r" % (routing_key_info, body))

  ###здесь - тело маршрутизатора должно быть
  print("Received: %r" % body)
  
  ###функция выгрузки данных объекта  
  #отправляем отработанные данные в тестирование
  channel.basic_publish(exchange='out_route',
    routing_key='out_route_done',
    body=(pickle.dumps(body, 0)).decode(),
    properties = pika.BasicProperties(delivery_mode=2))
  print("Sent %r:%r" % ('out_route_done', body))



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
