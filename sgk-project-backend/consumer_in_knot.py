# -*- coding: utf-8 -*-
import pika
import sys
import pickle
import traceback

#подключение к кролику
conn_params = pika.ConnectionParameters('rabbit', 5672)
connection = pika.BlockingConnection(conn_params)
channel = connection.channel()


#внешние датчики
### здесь должно быть подключение к внешнему серверу opc ua
channel.queue_declare(queue='in_queue',
	arguments={'x-message-ttl':60000},
	durable=True)

#маршрутизация здесь надо сделать по очереди для каждого объекта и если в течение некоторого времени из очереди не были получены все параметры объекта, 
#то генерация или ошибка (или для каждого показателя по очереди, но тогда будет неструктурированность)
channel.queue_declare(queue='route_in', 
	arguments={'x-message-ttl':60000}, 
	durable=True)

print("Waiting for messages for routing to маршрутизация. To exit press CTRL+C")

###вместо callback тело консюмера opc ua
def callback(ch, method, properties, body):
	print('asdasd')
	body=pickle.loads(body.encode())
	print("Received: %r" %body)
	#отправляем полученные данные в маршрутизатор
	#здесь и далее преобразования тела сообщения, 
	#чтобы передавать можно было объект произвольной природы, а не только строки
	channel.basic_publish(exchange= '',
		routing_key='route_in', 
		body=(pickle.dumps(body, 0)).decode(), 
		properties = pika.BasicProperties(delivery_mode=2))


channel.basic_consume(on_message_callback=callback, 
	queue='in_queue', 
	auto_ack=True)
try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
except Exception:
    channel.stop_consuming()
    traceback.print_exc(file=sys.stdout)
